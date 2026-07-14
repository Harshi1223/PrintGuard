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
# Health Thresholds
# =====================================================

NOZZLE_OVERHEAT_THRESHOLD = 240

BED_OVERHEAT_THRESHOLD = 90

LOW_FILAMENT_THRESHOLD = 15

HIGH_VIBRATION_THRESHOLD = 5

HIGH_HUMIDITY_THRESHOLD = 70