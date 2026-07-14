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

            elif alert_type == "Nozzle Temperature Trending Up":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Nozzle temperature is climbing steadily - monitor closely, "
                        "no action needed yet unless it continues to rise."
                })

            elif alert_type == "Bed Temperature Trending Up":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Bed temperature is climbing steadily - monitor closely, "
                        "no action needed yet unless it continues to rise."
                })

            elif alert_type == "Vibration Trending Up":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Vibration is increasing over recent readings - check for "
                        "early signs of a loose belt or shifting load."
                })

            elif alert_type == "Humidity Trending Up":

                recommendations.append({
                    "alert": alert_type,
                    "recommended_action":
                        "Humidity is rising steadily - consider moving filament to "
                        "dry storage before it crosses the safe threshold."
                })

        return recommendations