"""
PrintGuard Lambda - Read API
------------------------------
Backs the dashboard's read-side REST API via API Gateway (Lambda proxy
integration). One function handles all routes, dispatching internally
on the request path - simpler to wire up in the console than four
separate functions.

Routes:
    GET /printers                  -> latest reading per printer
    GET /printers/{id}/history     -> recent readings for one printer
    GET /alerts                    -> printers currently showing an alert
    GET /health                    -> basic service/table status check

DynamoDB stores one item per reading (partition key: printer_id, sort
key: timestamp), not one item per printer - so "current status" means
"most recent item for that printer_id", computed here rather than
stored separately.
"""

import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get("TABLE_NAME", "PrintGuardReadings")
HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", "50"))

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def _decimal_default(obj):
    # DynamoDB returns numbers as Decimal; JSON doesn't know how to
    # serialise that natively, so convert to int/float on the way out.
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            # Allows the dashboard (served from a different origin/file)
            # to call this API directly from the browser.
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=_decimal_default),
    }


def _latest_reading_per_printer():
    """
    Scans the table and keeps only the most recent item per printer_id.
    A full scan is fine at this project's scale (a handful of printers);
    a production system with many printers would maintain a separate
    "latest status" table instead of scanning on every request.
    """

    response = table.scan()
    items = response.get("Items", [])

    latest = {}
    for item in items:
        printer_id = item.get("printer_id")
        if printer_id is None:
            continue
        current = latest.get(printer_id)
        if current is None or item["timestamp"] > current["timestamp"]:
            latest[printer_id] = item

    return list(latest.values())


def get_printers():
    printers = _latest_reading_per_printer()
    printers.sort(key=lambda p: p.get("printer_id", ""))
    return _response(200, {"printers": printers, "count": len(printers)})


def get_printer_history(printer_id):
    response = table.query(
        KeyConditionExpression=Key("printer_id").eq(printer_id),
        ScanIndexForward=False,  # newest first
        Limit=HISTORY_LIMIT,
    )
    items = response.get("Items", [])
    return _response(200, {"printer_id": printer_id, "history": items, "count": len(items)})


def get_alerts():
    printers = _latest_reading_per_printer()
    alerting = [
        {
            "printer_id": p.get("printer_id"),
            "timestamp": p.get("timestamp"),
            "fog_health_status": p.get("fog_health_status"),
            "fog_alerts": p.get("fog_alerts", []),
        }
        for p in printers
        if p.get("fog_alerts")
    ]
    return _response(200, {"alerts": alerting, "count": len(alerting)})


def get_health():
    try:
        item_count = table.item_count  # approximate, updated periodically by DynamoDB
        return _response(200, {
            "status": "ok",
            "table": TABLE_NAME,
            "approx_item_count": item_count,
        })
    except Exception as exc:
        return _response(500, {"status": "error", "message": str(exc)})


def lambda_handler(event, context):

    

    resource = event.get("resource", "")
    path_params = event.get("pathParameters") or {}

    try:
        if resource == "/printers":
            return get_printers()

        if resource == "/printers/{id}/history":
            printer_id = path_params.get("id")
            if not printer_id:
                return _response(400, {"error": "Missing printer id in path"})
            return get_printer_history(printer_id)

        if resource == "/alerts":
            return get_alerts()

        if resource == "/health":
            return get_health()

        return _response(404, {"error": f"Unknown route: {resource}"})

    except Exception as exc:
        print(f"Unhandled error processing {resource}: {exc}")
        return _response(500, {"error": "Internal server error"})