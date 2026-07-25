"""
PrintGuard Fog Node Configuration
"""

# =====================================================
# MQTT Configuration
# =====================================================

MQTT_BROKER = "localhost"

MQTT_PORT = 1883

MQTT_TOPIC = "printguard/sensors"

MQTT_CLIENT_ID = "printguard-fog-node"

# Topic the fog node publishes commands to (e.g. HALT) - the simulator
# listens on this same topic. Value must match sensor_simulator/config.py.
MQTT_COMMANDS_TOPIC = "printguard/commands"

# =====================================================
# Batch Configuration
# =====================================================

# Number of processed readings before creating a batch

BATCH_SIZE = 10

# =====================================================
# Retry Configuration
# =====================================================

MAX_RETRY_COUNT = 3

RETRY_INTERVAL = 5

# =====================================================
# Buffer File
# =====================================================

BUFFER_FILE = "buffer.json"

# =====================================================
# Logging
# =====================================================

LOG_FILE = "fog.log"

# =====================================================
# AWS Configuration
# =====================================================

AWS_REGION = "us-east-1"

# SQS queue the fog node publishes batches to directly (ingestion path).
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/503148390993/printguard-batches-queue"

# API Gateway base URL - used for the READ-side REST API that the
# dashboard consumes (GET /printers, GET /alerts, etc). Not used for
# ingestion - the fog node publishes straight to SQS instead, since
# ingestion doesn't need HTTP routing overhead.
API_GATEWAY_URL = "https://rrcpkz0lqb.execute-api.us-east-1.amazonaws.com/prod"

# =====================================================
# Health Thresholds (fallback - used only if a reading has
# no "material" field, or an unrecognized one)
# =====================================================

NOZZLE_OVERHEAT_THRESHOLD = 245

BED_OVERHEAT_THRESHOLD = 95

LOW_FILAMENT_THRESHOLD = 10

HIGH_VIBRATION_THRESHOLD = 5

HIGH_HUMIDITY_THRESHOLD = 70

# =====================================================
# Material-Aware Overheat Thresholds (additive)
# -----------------------------------------------------
# Different print materials have different normal operating
# temperatures - PLA runs cooler than ABS/PETG. Using one fixed
# global threshold for every material meant ABS/PETG printers could
# be flagged "Nozzle Overheat" while still within their own normal
# operating range. These values are each material's own overheat
# threshold, matching the ranges used in sensor_simulator/config.py.
# PLA's values match the previous fixed thresholds exactly, so PLA
# behaviour is unchanged; only ABS/PETG behaviour is corrected.
# =====================================================

DEFAULT_MATERIAL = "PLA"

MATERIAL_THRESHOLDS = {
    "PLA": {
        "nozzle_overheat": NOZZLE_OVERHEAT_THRESHOLD,
        "bed_overheat": BED_OVERHEAT_THRESHOLD,
    },
    "ABS": {
        "nozzle_overheat": 265,
        "bed_overheat": 120,
    },
    "PETG": {
        "nozzle_overheat": 260,
        "bed_overheat": 100,
    },
}