import json
import requests

from config import API_GATEWAY_URL
import logger

log = logger.get_logger("dispatcher")


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

    def send_to_cloud(self, batch):
        """
        Attempt to send a completed batch to AWS via API Gateway.
        Returns True only on a confirmed successful send - the caller
        (main.py) is responsible for buffering the batch via
        RetryBuffer when this returns False.
        """

        if not API_GATEWAY_URL:
            log.warning(
                "API_GATEWAY_URL not configured - treating backend as unreachable"
            )
            return False

        try:
            response = requests.post(
                API_GATEWAY_URL,
                json=batch,
                timeout=5,
            )

            if response.status_code < 300:
                log.info(
                    "Batch %s sent to cloud (status %s)",
                    batch.get("batch_id"), response.status_code,
                )
                return True

            log.warning(
                "Cloud rejected batch %s (status %s)",
                batch.get("batch_id"), response.status_code,
            )
            return False

        except requests.RequestException as exc:
            log.warning("Could not reach cloud backend: %s", exc)
            return False