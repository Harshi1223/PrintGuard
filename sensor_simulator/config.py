# ============================================================
# PrintGuard Configuration
# ============================================================

# ----------------------------
# Simulation
# ----------------------------

NUMBER_OF_PRINTERS = 3

SAMPLING_INTERVAL = 2

FAULT_PROBABILITY = 0.30

# ----------------------------
# Printer Temperatures
# ----------------------------

NORMAL_NOZZLE_TEMP = (195, 230)

NORMAL_BED_TEMP = (55, 75)

IDLE_TEMP = 25

# ----------------------------
# Fault Ranges
# ----------------------------

NOZZLE_OVERHEAT = (245, 265)

BED_OVERHEAT = (95, 110)

LOW_FILAMENT = (0, 10)

HIGH_VIBRATION = (5, 8)

HIGH_HUMIDITY = (70, 90)

# ----------------------------
# Environment
# ----------------------------

NORMAL_HUMIDITY = (35, 60)

NORMAL_VIBRATION = (0.2, 2.0)

NORMAL_FILAMENT_LEVEL = (0, 100)

# ----------------------------
# Print Jobs
# ----------------------------

PRINT_JOBS = [
    "Phone Stand",
    "Gear Housing",
    "Camera Bracket",
    "Valve Cover",
    "Drone Frame",
    "Prototype Wheel",
    "Robot Arm",
    "Medical Clamp"
]

MIN_LAYERS = 150

MAX_LAYERS = 400

# ----------------------------
# MQTT
# ----------------------------

MQTT_BROKER = "localhost"

MQTT_PORT = 1883

MQTT_TOPIC = "printguard/sensors"

MQTT_CLIENT_ID = "printguard-simulator"