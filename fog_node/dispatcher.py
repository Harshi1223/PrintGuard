import json


class Dispatcher:

    def dispatch(
        self,
        data,
        alerts,
        recommendations,
        health_score,
        health_status
    ):

        output = {

            **data,

            "fog_health_score": health_score,

            "fog_health_status": health_status,

            "fog_alerts": alerts,

            "fog_recommendations": recommendations

        }

        print("\n")
        print("=" * 80)
        print("FOG NODE OUTPUT")
        print("=" * 80)

        print(
            json.dumps(
                output,
                indent=4
            )
        )

        print("=" * 80)

        return output