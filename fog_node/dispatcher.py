import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config import SQS_QUEUE_URL, AWS_REGION
import logger

log = logger.get_logger("dispatcher")


class Dispatcher:

    def __init__(self):
        # Created once and reused - boto3 clients are thread-safe and
        # opening a new one per call would add needless overhead.
        self._sqs_client = None

    def _get_sqs_client(self):
        if self._sqs_client is None:
            self._sqs_client = boto3.client("sqs", region_name=AWS_REGION)
        return self._sqs_client

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
        Publish a completed batch directly to the SQS ingestion queue.
        Returns True only on a confirmed successful send - the caller
        (main.py) is responsible for buffering the batch via
        RetryBuffer when this returns False.
        """

        if not SQS_QUEUE_URL:
            log.warning(
                "SQS_QUEUE_URL not configured - treating backend as unreachable"
            )
            return False

        try:
            client = self._get_sqs_client()

            response = client.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(batch),
                MessageAttributes={
                    "batch_id": {
                        "DataType": "String",
                        "StringValue": batch.get("batch_id", "unknown"),
                    }
                },
            )

            message_id = response.get("MessageId")

            log.info(
                "Batch %s sent to SQS (MessageId %s)",
                batch.get("batch_id"), message_id,
            )
            return True

        except (BotoCoreError, ClientError) as exc:
            log.warning("Could not reach SQS: %s", exc)
            return False