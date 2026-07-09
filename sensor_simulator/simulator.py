import json
import random
import time
from datetime import datetime

from config import (
    NUMBER_OF_PRINTERS,
    SAMPLING_INTERVAL,
    FAULT_PROBABILITY,
    NOZZLE_OVERHEAT,
    BED_OVERHEAT,
    LOW_FILAMENT,
    HIGH_VIBRATION,
    HIGH_HUMIDITY,
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


class Printer:

    def __init__(self, printer_id):

        self.printer_id = printer_id

        # Printer State
        self.status = "Idle"

        # Sensor Values (Raw Sensors Only)
        self.nozzle_temp = 25.0
        self.bed_temp = 25.0
        self.filament_level = 100.0
        self.vibration = 0.1
        self.humidity = random.uniform(40, 50)

        # Print Job
        self.job_name = random.choice(PRINT_JOBS)
        self.progress = 0.0
        self.current_layer = 0
        self.total_layers = random.randint(180, 350)

        # Fault (used only for simulation)
        self.active_fault = None
        self.fault_duration = 0

        # Internal Counter
        self.print_counter = 0

    def update_status(self):

        if self.status == "Idle":

            if random.random() < 0.40:
                self.status = "Heating"

        elif self.status == "Heating":

            if self.nozzle_temp >= 200:
                self.status = "Printing"

        elif self.status == "Printing":

            self.print_counter += 1

            if self.progress >= 100:
                self.status = "Cooling"

        elif self.status == "Cooling":

            if self.nozzle_temp <= 35:

                self.status = "Idle"

                self.print_counter = 0

                self.filament_level = 100

                self.progress = 0

                self.current_layer = 0

                self.total_layers = random.randint(
                    180,
                    350
                )

                self.job_name = random.choice(
                    PRINT_JOBS
                )

    def update_sensor_values(self):

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

            self.nozzle_temp = min(
                215,
                self.nozzle_temp + 12
            )

            self.bed_temp = min(
                60,
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

            self.vibration = random.uniform(
                0.5,
                1.5
            )

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
            30,
            min(
                60,
                self.humidity
            )
        )
        
    def inject_fault(self):
        """
        Simulate temporary faults.
        These are used only to generate realistic sensor values.
        The Fog Node will independently detect the faults.
        """

        # Continue existing fault

        if self.fault_duration > 0:

            self.fault_duration -= 1

            if self.active_fault == "Nozzle Overheat":

                self.nozzle_temp = random.uniform(
                    *NOZZLE_OVERHEAT
                )

            elif self.active_fault == "Bed Overheat":

                self.bed_temp = random.uniform(
                    *BED_OVERHEAT
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

            "timestamp": datetime.utcnow().isoformat(),

            "status": self.status,

            "job_name": self.job_name,

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