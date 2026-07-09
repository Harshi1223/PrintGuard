class AnomalyDetector:

    def detect(self, data):

        alerts = []

        if data["nozzle_temperature"] > 245:
            alerts.append({
                "type": "Nozzle Overheat",
                "severity": "Critical"
            })

        if data["bed_temperature"] > 95:
            alerts.append({
                "type": "Bed Overheat",
                "severity": "High"
            })

        if data["filament_level"] < 10:
            alerts.append({
                "type": "Low Filament",
                "severity": "Medium"
            })

        if data["vibration"] > 5:
            alerts.append({
                "type": "High Vibration",
                "severity": "High"
            })

        if data["humidity"] > 70:
            alerts.append({
                "type": "High Humidity",
                "severity": "Medium"
            })

        return alerts