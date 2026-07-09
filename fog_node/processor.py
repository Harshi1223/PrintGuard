import hashlib
import json


class Processor:

    REQUIRED_FIELDS = [
        "printer_id",
        "timestamp",
        "status",
        "nozzle_temperature",
        "bed_temperature",
        "filament_level",
        "vibration",
        "humidity"
    ]

    def __init__(self):
        self.processed_messages = set()

    def validate(self, data):

        for field in self.REQUIRED_FIELDS:

            if field not in data:
                return False, f"Missing field: {field}"

        if data["nozzle_temperature"] < 0:
            return False, "Invalid nozzle temperature"

        if data["bed_temperature"] < 0:
            return False, "Invalid bed temperature"

        if data["filament_level"] < 0:
            return False, "Invalid filament level"

        if data["humidity"] < 0 or data["humidity"] > 100:
            return False, "Invalid humidity"

        return True, "Valid"

    def is_duplicate(self, data):

        message = json.dumps(data, sort_keys=True)

        message_hash = hashlib.md5(
            message.encode()
        ).hexdigest()

        if message_hash in self.processed_messages:
            return True

        self.processed_messages.add(message_hash)

        return False

    def process(self, data):

        valid, reason = self.validate(data)

        if not valid:
            print(reason)
            return None

        if self.is_duplicate(data):
            print("Duplicate reading ignored")
            return None

        return data