from datetime import datetime, timezone
import uuid


class BatchManager:

    def __init__(self, batch_size):

        self.batch_size = batch_size

        self.batch = []

    def add_reading(self, reading):

        self.batch.append(reading)

        if len(self.batch) >= self.batch_size:

            completed_batch = self.create_batch()

            self.batch = []

            return completed_batch

        return None

    def create_batch(self):

        return {

            "batch_id": str(uuid.uuid4()),

            "timestamp": datetime.now(timezone.utc).isoformat(),

            "message_count": len(self.batch),

            "readings": self.batch

        }