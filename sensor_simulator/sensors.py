import random
from config import (
    NOZZLE_TEMP,
    BED_TEMP,
    FILAMENT_LEVEL,
    VIBRATION,
    HUMIDITY,
)


class Sensor:
    def __init__(self, name, min_value, max_value, unit):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.unit = unit

    def generate_value(self):
        return round(random.uniform(self.min_value, self.max_value), 2)


class NozzleTemperatureSensor(Sensor):
    def __init__(self):
        super().__init__(
            "Nozzle Temperature",
            NOZZLE_TEMP["min"],
            NOZZLE_TEMP["max"],
            "°C"
        )


class BedTemperatureSensor(Sensor):
    def __init__(self):
        super().__init__(
            "Bed Temperature",
            BED_TEMP["min"],
            BED_TEMP["max"],
            "°C"
        )


class FilamentLevelSensor(Sensor):
    def __init__(self):
        super().__init__(
            "Filament Level",
            FILAMENT_LEVEL["min"],
            FILAMENT_LEVEL["max"],
            "%"
        )


class VibrationSensor(Sensor):
    def __init__(self):
        super().__init__(
            "Vibration",
            VIBRATION["min"],
            VIBRATION["max"],
            "mm/s"
        )


class HumiditySensor(Sensor):
    def __init__(self):
        super().__init__(
            "Humidity",
            HUMIDITY["min"],
            HUMIDITY["max"],
            "%"
        )