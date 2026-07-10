"""
PrintGuard Lambda - Process Batch
------------------------------------
Triggered by SQS (printguard-batches-queue). Each SQS message body is
one batch produced by the fog node's BatchManager:

    {
        "batch_id": "...",
        "timestamp": "...",          <- batch creation time
        "message_count": 10,
        "readings": [ {...}, {...} ],  <- individual processed readings
        "summary": {...}                <- farm-wide aggregate (optional)
    }

Each entry in "readings" already has printer_id + timestamp (added by
the sensor simulator) plus the fog node's health score, alerts, and
recommendations. This function writes each reading as its own item in
DynamoDB (partition key: printer_id, sort key: timestamp).
"""

import json
import os
from decimal import Decimal

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "PrintGuardReadings")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    written = 0
    skipped = 0

    for record in event.get("Records", []):

        try:
            # parse_float=Decimal because DynamoDB does not accept
            # native Python floats via the resource API.
            body = json.loads(record["body"], parse_float=Decimal)
        except (KeyError, json.JSONDecodeError) as exc:
            print(f"Skipping SQS record - could not parse body: {exc}")
            skipped += 1
            continue

        batch_id = body.get("batch_id", "unknown")
        readings = body.get("readings", [])

        for reading in readings:

            if "printer_id" not in reading or "timestamp" not in reading:
                print(
                    f"Skipping reading in batch {batch_id} - "
                    f"missing printer_id or timestamp"
                )
                skipped += 1
                continue

            item = dict(reading)
            item["batch_id"] = batch_id

            try:
                table.put_item(Item=item)
                written += 1
            except Exception as exc:
                print(
                    f"Failed to write reading for "
                    f"{reading.get('printer_id')}: {exc}"
                )
                skipped += 1

    print(f"Lambda finished: {written} readings written, {skipped} skipped")

    return {
        "statusCode": 200,
        "body": json.dumps({"written": written, "skipped": skipped}),
    }