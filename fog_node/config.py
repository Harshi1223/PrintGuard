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

# Replace after creating API Gateway

API_GATEWAY_URL = ""

AWS_REGION = "eu-west-1"

# =====================================================
# Health Thresholds
# =====================================================

NOZZLE_OVERHEAT_THRESHOLD = 240

BED_OVERHEAT_THRESHOLD = 90

LOW_FILAMENT_THRESHOLD = 15

HIGH_VIBRATION_THRESHOLD = 5

HIGH_HUMIDITY_THRESHOLD = 70