class RecommendationEngine:

    def generate(self, alerts):

        recommendations = []

        for alert in alerts:

            alert_type = alert["type"]

            if alert_type == "Nozzle Overheat":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Pause print immediately and inspect nozzle heating element."
                })

            elif alert_type == "Bed Overheat":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Reduce bed temperature and inspect heating pad."
                })

            elif alert_type == "Low Filament":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Replace filament spool before the next print cycle."
                })

            elif alert_type == "High Vibration":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Pause printing and inspect belts, bearings, and frame."
                })

            elif alert_type == "High Humidity":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Move filament to a dry storage box or use a filament dryer."
                })

        return recommendations