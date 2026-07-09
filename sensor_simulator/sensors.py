import random

from config import (
    NORMAL_NOZZLE_TEMP,
    NORMAL_BED_TEMP,
    NORMAL_FILAMENT_LEVEL,
    NORMAL_VIBRATION,
    NORMAL_HUMIDITY,
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
        min_value, max_value = NORMAL_NOZZLE_TEMP
        super().__init__(
            "Nozzle Temperature",
            min_value,
            max_value,
            "°C"
        )


class BedTemperatureSensor(Sensor):
    def __init__(self):
        min_value, max_value = NORMAL_BED_TEMP
        super().__init__(
            "Bed Temperature",
            min_value,
            max_value,
            "°C"
        )


class FilamentLevelSensor(Sensor):
    def __init__(self):
        min_value, max_value = NORMAL_FILAMENT_LEVEL
        super().__init__(
            "Filament Level",
            min_value,
            max_value,
            "%"
        )


class VibrationSensor(Sensor):
    def __init__(self):
        min_value, max_value = NORMAL_VIBRATION
        super().__init__(
            "Vibration",
            min_value,
            max_value,
            "mm/s"
        )


class HumiditySensor(Sensor):
    def __init__(self):
        min_value, max_value = NORMAL_HUMIDITY
        super().__init__(
            "Humidity",
            min_value,
            max_value,
            "%"
        )