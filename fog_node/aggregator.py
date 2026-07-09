class Aggregator:

    def __init__(self):
        self.latest_readings = {}

    def update(self, reading):

        printer_id = reading["printer_id"]

        self.latest_readings[printer_id] = reading

    def get_summary(self):

        if not self.latest_readings:
            return {}

        readings = list(self.latest_readings.values())

        total = len(readings)

        avg_nozzle = sum(
            r["nozzle_temperature"] for r in readings
        ) / total

        avg_bed = sum(
            r["bed_temperature"] for r in readings
        ) / total

        avg_humidity = sum(
            r["humidity"] for r in readings
        ) / total

        avg_vibration = sum(
            r["vibration"] for r in readings
        ) / total

        avg_filament = sum(
            r["filament_level"] for r in readings
        ) / total

        healthy = sum(
            1 for r in readings
            if r["fog_health_status"] == "Healthy"
        )

        warning = sum(
            1 for r in readings
            if r["fog_health_status"] == "Warning"
        )

        critical = sum(
            1 for r in readings
            if r["fog_health_status"] == "Critical"
        )

        return {

            "printer_count": total,

            "average_nozzle_temperature":
                round(avg_nozzle, 2),

            "average_bed_temperature":
                round(avg_bed, 2),

            "average_humidity":
                round(avg_humidity, 2),

            "average_vibration":
                round(avg_vibration, 2),

            "average_filament":
                round(avg_filament, 2),

            "healthy_printers": healthy,

            "warning_printers": warning,

            "critical_printers": critical

        }