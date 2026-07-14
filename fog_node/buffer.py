"""
PrintGuard Fog Node - Retry Buffer
------------------------------------
Answers the brief's question directly: "What happens if the backend
is unreachable?" -> Save locally, retry with backoff, drop only after
MAX_RETRY_COUNT attempts. This is what lets the fog node keep running
(and keep making local STOP/health decisions) even during a temporary
AWS outage, without silently losing data.

Flow: Save -> Retry -> Delete (on success) or Drop (after max retries)
"""

import json
import os
import threading
import time

from config import BUFFER_FILE, MAX_RETRY_COUNT, RETRY_INTERVAL
import logger

log = logger.get_logger("buffer")


class RetryBuffer:

    def __init__(self, send_fn):
        # send_fn(batch) -> bool. Should return True only on a
        # confirmed successful send to the cloud backend.
        self.send_fn = send_fn
        self.lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(BUFFER_FILE):
            with open(BUFFER_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_all(self):
        with self.lock:
            try:
                with open(BUFFER_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return []

    def _write_all(self, entries):
        with self.lock:
            with open(BUFFER_FILE, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2)

    def save(self, batch):
        """Persist a batch that failed to send, with a retry counter."""

        entries = self._read_all()
        entries.append({"batch": batch, "attempts": 0})
        self._write_all(entries)

        log.warning(
            "Buffered batch %s (backend unreachable) - %d batch(es) pending",
            batch.get("batch_id", "unknown"),
            len(entries),
        )

    def retry_pending(self):
        """Attempt to resend everything currently buffered."""

        entries = self._read_all()

        if not entries:
            return

        remaining = []

        for entry in entries:
            batch = entry["batch"]
            attempts = entry["attempts"] + 1

            success = False
            try:
                success = self.send_fn(batch)
            except OSError as exc:
                log.warning(
                    "Retry failed for batch %s: %s",
                    batch.get("batch_id"), exc,
                )

            if success:
                log.info(
                    "Buffered batch %s sent successfully - removing from buffer",
                    batch.get("batch_id"),
                )
                continue

            if attempts >= MAX_RETRY_COUNT:
                log.error(
                    "Batch %s exceeded max retry count (%d) - dropping",
                    batch.get("batch_id"), MAX_RETRY_COUNT,
                )
                continue

            entry["attempts"] = attempts
            remaining.append(entry)

        self._write_all(remaining)

    def start_background_retry(self):
        """Run retry_pending() on a loop in a daemon thread."""

        def loop():
            while True:
                time.sleep(RETRY_INTERVAL)
                self.retry_pending()

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        log.info(
            "Background retry started (every %ds, max %d attempts)",
            RETRY_INTERVAL, MAX_RETRY_COUNT,
        )