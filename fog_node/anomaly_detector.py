from config import (
    MATERIAL_THRESHOLDS,
    DEFAULT_MATERIAL,
    LOW_FILAMENT_THRESHOLD,
    HIGH_VIBRATION_THRESHOLD,
    HIGH_HUMIDITY_THRESHOLD,
)


class AnomalyDetector:

    def detect(self, data):

        alerts = []

        # Nozzle/bed overheat thresholds depend on the print material -
        # PLA, ABS, and PETG each have a different normal operating
        # range. Falls back to PLA's thresholds if the reading has no
        # "material" field or an unrecognised one, so behaviour is
        # unchanged for any data that predates this field.
        material = data.get("material", DEFAULT_MATERIAL)
        thresholds = MATERIAL_THRESHOLDS.get(material, MATERIAL_THRESHOLDS[DEFAULT_MATERIAL])

        if data["nozzle_temperature"] > thresholds["nozzle_overheat"]:
            alerts.append({
                "type": "Nozzle Overheat",
                "severity": "Critical"
            })

        if data["bed_temperature"] > thresholds["bed_overheat"]:
            alerts.append({
                "type": "Bed Overheat",
                "severity": "High"
            })

        if data["filament_level"] < LOW_FILAMENT_THRESHOLD:
            alerts.append({
                "type": "Low Filament",
                "severity": "Medium"
            })

        if data["vibration"] > HIGH_VIBRATION_THRESHOLD:
            alerts.append({
                "type": "High Vibration",
                "severity": "High"
            })

        if data["humidity"] > HIGH_HUMIDITY_THRESHOLD:
            alerts.append({
                "type": "High Humidity",
                "severity": "Medium"
            })

        return alerts