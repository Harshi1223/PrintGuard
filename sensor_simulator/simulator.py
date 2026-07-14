import json
import random
import time
from datetime import datetime, timezone

from config import (
    NUMBER_OF_PRINTERS,
    SAMPLING_INTERVAL,
    FAULT_PROBABILITY,
    NOZZLE_OVERHEAT,
    BED_OVERHEAT,
    LOW_FILAMENT,
    HIGH_VIBRATION,
    HIGH_HUMIDITY,
    MATERIALS,
    DEFAULT_MATERIAL,
    JOB_QUEUE_SEED,
)
from sensors import (
    NozzleTemperatureSensor,
    BedTemperatureSensor,
    FilamentLevelSensor,
    VibrationSensor,
    HumiditySensor,
)

PRINT_JOBS = [
    "Gear Housing",
    "Drone Frame",
    "Phone Stand",
    "Prototype Wheel",
    "Valve Cover",
    "Robot Arm",
    "Bearing Mount",
    "Camera Bracket",
    "Motor Casing",
    "Custom Enclosure",
]


class JobQueue:
    """
    Simple FIFO job queue shared by the whole farm - pulls the next job
    (name + material) for the next printer that finishes its current one.
    Refills itself (reshuffled) whenever it runs empty, so the farm never
    stalls waiting for work.
    """

    def __init__(self, seed_jobs):
        self._seed = seed_jobs
        self._queue = []
        self._refill()

    def _refill(self):
        batch = list(self._seed)
        random.shuffle(batch)
        self._queue.extend(batch)

    def next_job(self):
        if not self._queue:
            self._refill()
        return self._queue.pop(0)


# Shared across all Printer instances - one farm-wide queue, not one per printer.
JOB_QUEUE = JobQueue(JOB_QUEUE_SEED)


class Printer:

    def __init__(self, printer_id):

        self.printer_id = printer_id

        # Printer State
        self.status = "Idle"

        # Sensor definitions - ranges come from config.py, so editing
        # NORMAL_NOZZLE_TEMP / NORMAL_VIBRATION / etc. there actually
        # changes simulator behaviour instead of sitting unused.
        self.nozzle_sensor = NozzleTemperatureSensor()
        self.bed_sensor = BedTemperatureSensor()
        self.filament_sensor = FilamentLevelSensor()
        self.vibration_sensor = VibrationSensor()
        self.humidity_sensor = HumiditySensor()

        # Sensor Values (Raw Sensors Only)
        self.nozzle_temp = 25.0
        self.bed_temp = 25.0
        self.filament_level = self.filament_sensor.max_value
        self.vibration = 0.1
        self.humidity = self.humidity_sensor.generate_value()

        # Print Job - pulled from the shared farm queue instead of picked
        # randomly forever. Falls back safely to PRINT_JOBS/DEFAULT_MATERIAL
        # if anything about the queue/material lookup is ever unavailable.
        self._assign_next_job()

        self.progress = 0.0
        self.current_layer = 0
        self.total_layers = random.randint(180, 350)

        # Fault (used only for simulation)
        self.active_fault = None
        self.fault_duration = 0

        # Halt state (set externally by the fog node's HALT command).
        # Additive - printers start un-halted, and normal behaviour is
        # completely unaffected unless receive_halt_command() is called.
        self.halted_counter = 0

        # Internal Counter
        self.print_counter = 0

    def _assign_next_job(self):
        """
        Pulls the next job off the shared farm queue and sets this
        printer's material-specific thresholds accordingly. Wrapped in a
        try/except so that if JOB_QUEUE or MATERIALS is ever unavailable
        for any reason, the printer falls back to the original random
        job-name behaviour rather than crashing.
        """
        try:
            job = JOB_QUEUE.next_job()
            self.job_name = job["job_name"]
            self.material = job.get("material", DEFAULT_MATERIAL)
            self.material_thresholds = MATERIALS.get(
                self.material, MATERIALS[DEFAULT_MATERIAL]
            )
        except Exception:
            self.job_name = random.choice(PRINT_JOBS)
            self.material = DEFAULT_MATERIAL
            self.material_thresholds = MATERIALS.get(DEFAULT_MATERIAL)

    def receive_halt_command(self):
        """
        Called when the fog node sends a HALT command for this printer
        (a Critical-severity alert, e.g. Nozzle Overheat). Simulates the
        printer physically stopping: clears any in-progress fault (the
        dangerous condition is being addressed), stops printing, and
        starts cooling passively. Auto-resumes to Cooling after a short
        halted period, simulating an operator having intervened.
        """
        self.status = "Halted"
        self.halted_counter = 0
        self.active_fault = None
        self.fault_duration = 0
        self.vibration = 0.0

    def update_status(self):

        if self.status == "Halted":

            self.halted_counter += 1

            # Simulates an operator having addressed the issue after a
            # short window - printer moves to Cooling, then rejoins the
            # normal Idle/Heating/Printing/Cooling cycle as usual.
            if self.halted_counter >= 5:
                self.status = "Cooling"
                self.halted_counter = 0

            return

        if self.status == "Idle":

            if random.random() < 0.40:
                self.status = "Heating"

        elif self.status == "Heating":

            target_nozzle = (self.material_thresholds or {}).get(
                "normal_nozzle_temp", (self.nozzle_sensor.min_value, None)
            )[0]

            if self.nozzle_temp >= target_nozzle:
                self.status = "Printing"

        elif self.status == "Printing":

            self.print_counter += 1

            if self.progress >= 100:
                self.status = "Cooling"

        elif self.status == "Cooling":

            if self.nozzle_temp <= 35:

                self.status = "Idle"

                self.print_counter = 0

                self.filament_level = self.filament_sensor.max_value

                self.progress = 0

                self.current_layer = 0

                self.total_layers = random.randint(
                    180,
                    350
                )

                self._assign_next_job()

    def update_sensor_values(self):

        if self.status == "Halted":

            # Heater is off - nozzle/bed cool passively, same rate as
            # Cooling state. No vibration since the printer has stopped.
            self.nozzle_temp = max(25, self.nozzle_temp - 8)
            self.bed_temp = max(25, self.bed_temp - 4)
            self.vibration = 0.0

            self.humidity += random.uniform(-0.3, 0.3)
            self.humidity = max(
                self.humidity_sensor.min_value,
                min(self.humidity_sensor.max_value, self.humidity),
            )
            return

        if self.status == "Idle":

            self.nozzle_temp = max(
                25,
                self.nozzle_temp - 3
            )

            self.bed_temp = max(
                25,
                self.bed_temp - 2
            )

            self.vibration = 0.1

        elif self.status == "Heating":

            target_nozzle = (self.material_thresholds or {}).get(
                "normal_nozzle_temp", (self.nozzle_sensor.min_value, None)
            )[0]

            target_bed = (self.material_thresholds or {}).get(
                "normal_bed_temp", (self.bed_sensor.min_value, None)
            )[0]

            self.nozzle_temp = min(
                target_nozzle,
                self.nozzle_temp + 12
            )

            self.bed_temp = min(
                target_bed,
                self.bed_temp + 5
            )

            self.vibration = 0.3

        elif self.status == "Printing":

            self.nozzle_temp += random.uniform(-1, 1)

            self.bed_temp += random.uniform(-0.5, 0.5)

            self.filament_level = max(
                0,
                self.filament_level - random.uniform(
                    0.15,
                    0.50
                )
            )

            self.vibration = self.vibration_sensor.generate_value()

            self.progress = min(
                100,
                self.progress + random.uniform(
                    1.0,
                    3.0
                )
            )

            self.current_layer = int(
                (self.progress / 100)
                * self.total_layers
            )

        elif self.status == "Cooling":

            self.nozzle_temp = max(
                25,
                self.nozzle_temp - 8
            )

            self.bed_temp = max(
                25,
                self.bed_temp - 4
            )

            self.vibration = 0.2

        # Humidity changes slowly

        self.humidity += random.uniform(
            -0.3,
            0.3
        )

        self.humidity = max(
            self.humidity_sensor.min_value,
            min(
                self.humidity_sensor.max_value,
                self.humidity
            )
        )
        
    def inject_fault(self):
        """
        Simulate temporary faults.
        These are used only to generate realistic sensor values.
        The Fog Node will independently detect the faults.
        """

        # No new or continuing faults while halted - receive_halt_command()
        # already cleared any active fault; this guard just prevents a new
        # one from starting during the halted window.
        if self.status == "Halted":
            return

        # Continue existing fault

        if self.fault_duration > 0:

            self.fault_duration -= 1

            if self.active_fault == "Nozzle Overheat":

                nozzle_overheat_range = (self.material_thresholds or {}).get(
                    "nozzle_overheat", NOZZLE_OVERHEAT
                )
                self.nozzle_temp = random.uniform(
                    *nozzle_overheat_range
                )

            elif self.active_fault == "Bed Overheat":

                bed_overheat_range = (self.material_thresholds or {}).get(
                    "bed_overheat", BED_OVERHEAT
                )
                self.bed_temp = random.uniform(
                    *bed_overheat_range
                )

            elif self.active_fault == "Low Filament":

                self.filament_level = random.uniform(
                    *LOW_FILAMENT
                )

            elif self.active_fault == "High Vibration":

                self.vibration = random.uniform(
                    *HIGH_VIBRATION
                )

            elif self.active_fault == "High Humidity":

                self.humidity = random.uniform(
                    *HIGH_HUMIDITY
                )

            return

        # Recover from fault

        self.active_fault = None

        # Faults only happen while printing

        if self.status != "Printing":
            return

        # Random chance of a new fault

        if random.random() > FAULT_PROBABILITY:
            return

        self.active_fault = random.choice([

            "Nozzle Overheat",

            "Bed Overheat",

            "Low Filament",

            "High Vibration",

            "High Humidity"

        ])

        self.fault_duration = random.randint(3, 8)

    def generate_data(self):

        self.update_status()

        self.update_sensor_values()

        self.inject_fault()

        return {

            "printer_id": self.printer_id,

            "timestamp": datetime.now(timezone.utc).isoformat(),

            "status": self.status,

            "job_name": self.job_name,

            "material": getattr(self, "material", DEFAULT_MATERIAL),

            "progress": round(
                self.progress,
                1
            ),

            "current_layer": self.current_layer,

            "total_layers": self.total_layers,

            "nozzle_temperature": round(
                self.nozzle_temp,
                2
            ),

            "bed_temperature": round(
                self.bed_temp,
                2
            ),

            "filament_level": round(
                self.filament_level,
                2
            ),

            "vibration": round(
                self.vibration,
                2
            ),

            "humidity": round(
                self.humidity,
                2
            )

        }
        
class PrinterFarmSimulator:
    
    def __init__(self):

        self.printers = [

            Printer(f"Printer-{i+1}")

            for i in range(NUMBER_OF_PRINTERS)

        ]

    def get_printer(self, printer_id):
        for printer in self.printers:
            if printer.printer_id == printer_id:
                return printer
        return None

    def handle_command(self, printer_id, command, reason=None):
        """
        Called by MQTTPublisher when a command arrives from the fog node
        on printguard/commands. Currently only "HALT" is recognised;
        anything else is logged and ignored rather than causing an error.
        """
        printer = self.get_printer(printer_id)
        if printer is None:
            print(f"HALT command for unknown printer_id: {printer_id}")
            return

        if command == "HALT":
            print(f"Halting {printer_id} (reason: {reason})")
            printer.receive_halt_command()
        else:
            print(f"Ignoring unrecognised command '{command}' for {printer_id}")

    def generate_all_data(self):

        readings = []

        for printer in self.printers:

            readings.append(

                printer.generate_data()

            )

        return readings

    def start(self):

        while True:

            print("=" * 90)

            readings = self.generate_all_data()

            for reading in readings:

                print(

                    json.dumps(

                        reading,

                        indent=4

                    )

                )

            print("=" * 90)

            time.sleep(SAMPLING_INTERVAL)