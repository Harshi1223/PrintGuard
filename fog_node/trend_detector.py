"""
PrintGuard Fog Node - Trend Detector
---------------------------------------
Novel addition (not present in OctoPrint, 3DQue, or any referenced
commercial print-farm tool): flags a sensor value that is trending
upward across recent readings, BEFORE it crosses the hard overheat/
fault threshold - not just after, like standard threshold-based
detection.

This is deliberately a separate, self-contained, ADDITIVE module:
- It does not replace anomaly_detector.py's existing threshold checks
- It maintains its own small rolling window of recent readings per
  printer (in memory), since the rest of the fog node is stateless
  per-message
- Its alerts use a distinct severity ("Early Warning") so they never
  get confused with or override the existing Critical/Medium/High
  threshold-crossing alerts

Integration point: call TrendDetector.check(reading) once per reading
in main.py, and extend the existing alerts list with whatever it
returns - see the integration note at the bottom of this file.
"""

from collections import deque


class TrendDetector:

    def __init__(self, window_size=5, rate_thresholds=None):
        """
        window_size: how many recent readings per printer to keep.
        rate_thresholds: dict of {field_name: rate_per_reading} - if a
            field rises by more than this amount per reading, averaged
            across the window, it's flagged as trending.
        """
        self.window_size = window_size

        self.rate_thresholds = rate_thresholds or {
            "nozzle_temperature": 3.0,   # °C per reading
            "bed_temperature": 2.0,      # °C per reading
            "vibration": 0.5,            # units per reading
            "humidity": 2.0,             # % per reading
        }

        # printer_id -> deque of recent readings (dicts)
        self._history = {}

    def _get_window(self, printer_id):
        if printer_id not in self._history:
            self._history[printer_id] = deque(maxlen=self.window_size)
        return self._history[printer_id]

    def _average_rate(self, values):
        """
        Simple average rate of change across consecutive values in the
        window - deliberately simple (not a full linear regression) so
        it's easy to explain and verify: sum of consecutive differences
        divided by the number of steps.
        """
        if len(values) < 2:
            return 0.0

        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        return sum(diffs) / len(diffs)

    def check(self, reading):
        """
        reading: a single processed sensor reading (dict) with at least
        'printer_id' and the numeric fields listed in rate_thresholds.

        Returns a list of trend alerts (possibly empty), in the same
        shape as anomaly_detector.py's alerts, e.g.:
            [{"type": "Nozzle Temperature Trending Up",
              "severity": "Early Warning",
              "rate": 4.2}]
        """
        printer_id = reading.get("printer_id")
        if printer_id is None:
            return []

        window = self._get_window(printer_id)
        window.append(reading)

        alerts = []

        # Need a full window before making a trend judgement - avoids
        # false positives from only 1-2 data points.
        if len(window) < self.window_size:
            return alerts

        for field, threshold in self.rate_thresholds.items():
            values = [w.get(field) for w in window if w.get(field) is not None]
            if len(values) < self.window_size:
                continue

            rate = self._average_rate(values)

            if rate >= threshold:
                label = field.replace("_", " ").title()
                alerts.append({
                    "type": f"{label} Trending Up",
                    "severity": "Early Warning",
                    "rate": round(rate, 2),
                })

        return alerts


# ---------------------------------------------------------------------
# Integration note for main.py (do this manually - shown here rather
# than assumed, since main.py's exact current content may have drifted
# from earlier versions):
#
#   from trend_detector import TrendDetector
#   trend_detector = TrendDetector()          # near your other module inits
#
#   ...inside the per-reading processing loop, after your existing
#   anomaly_detector.detect(...) call:
#
#   trend_alerts = trend_detector.check(data)
#   alerts.extend(trend_alerts)                # merge into existing alerts list
#
# No other files need to change - trend alerts flow through the same
# batching/dispatch/DynamoDB/dashboard path as existing alerts, since
# they're just additional entries in the same "fog_alerts" list.
# ---------------------------------------------------------------------