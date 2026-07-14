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
# Materials (additive - if a reading has no "material" field,
# code always falls back to NORMAL_NOZZLE_TEMP / NOZZLE_OVERHEAT /
# etc above, unchanged)
# ----------------------------

MATERIALS = {
    "PLA": {
        "normal_nozzle_temp": (195, 230),
        "nozzle_overheat": (245, 265),
        "normal_bed_temp": (55, 75),
        "bed_overheat": (95, 110),
    },
    "ABS": {
        "normal_nozzle_temp": (220, 250),
        "nozzle_overheat": (265, 290),
        "normal_bed_temp": (95, 110),
        "bed_overheat": (120, 140),
    },
    "PETG": {
        "normal_nozzle_temp": (220, 250),
        "nozzle_overheat": (260, 280),
        "normal_bed_temp": (70, 90),
        "bed_overheat": (100, 120),
    },
}

DEFAULT_MATERIAL = "PLA"  # used if a job doesn't specify one

# ----------------------------
# Job Queue (additive - replaces "pick a random job forever"
# with "pull the next job from a shared queue, refill when empty")
# ----------------------------

JOB_QUEUE_SEED = [
    {"job_name": "Phone Stand", "material": "PLA"},
    {"job_name": "Gear Housing", "material": "ABS"},
    {"job_name": "Camera Bracket", "material": "PETG"},
    {"job_name": "Valve Cover", "material": "ABS"},
    {"job_name": "Drone Frame", "material": "PETG"},
    {"job_name": "Prototype Wheel", "material": "PLA"},
    {"job_name": "Robot Arm", "material": "PETG"},
    {"job_name": "Medical Clamp", "material": "PLA"},
]

# ----------------------------
# MQTT
# ----------------------------

MQTT_BROKER = "localhost"

MQTT_PORT = 1883

MQTT_TOPIC = "printguard/sensors"

MQTT_CLIENT_ID = "printguard-simulator"

MQTT_COMMANDS_TOPIC = "printguard/commands"