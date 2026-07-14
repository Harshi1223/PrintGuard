from publisher import MQTTPublisher
from simulator import PrinterFarmSimulator


def main():

    print("=" * 60)
    print("PrintGuard Sensor Simulator")
    print("=" * 60)

    simulator = PrinterFarmSimulator()

    publisher = MQTTPublisher(command_handler=simulator.handle_command)

    while True:

        for printer in simulator.printers:

            data = printer.generate_data()

            publisher.publish(data)

            print(data)

        print("-" * 60)

        import time
        time.sleep(2)


if __name__ == "__main__":
    main()