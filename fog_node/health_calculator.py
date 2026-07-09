class HealthCalculator:

    def calculate(self, data):

        score = 100

        if data["filament_level"] < 20:
            score -= 20

        if data["humidity"] > 70:
            score -= 15

        if data["vibration"] > 5:
            score -= 25

        if data["nozzle_temperature"] > 245:
            score -= 30

        if data["bed_temperature"] > 95:
            score -= 25

        score = max(score, 0)

        if score >= 90:
            status = "Healthy"
        elif score >= 70:
            status = "Warning"
        else:
            status = "Critical"

        return score, status