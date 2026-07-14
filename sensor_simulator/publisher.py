import json
import time

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_TOPIC,
    MQTT_CLIENT_ID,
    MQTT_COMMANDS_TOPIC,
)


class MQTTPublisher:

    def __init__(self, command_handler=None):
        # command_handler(printer_id, command, reason) - called whenever a
        # command (e.g. "HALT") arrives on MQTT_COMMANDS_TOPIC from the fog
        # node. Optional - if not provided, incoming commands are ignored,
        # so this stays backward compatible with any code not using it.
        self.command_handler = command_handler

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=MQTT_CLIENT_ID,)
        self.client.on_connect = self.on_connect

        self.client.on_disconnect = self.on_disconnect

        self.client.on_message = self.on_message

        self.connect()

    

    def connect(self):

        while True:

            try:

                print("Connecting to MQTT Broker...")

                self.client.connect(
                    MQTT_BROKER,
                    MQTT_PORT,
                    keepalive=60
                )

                self.client.loop_start()

                break

            except OSError as e:
                # Catch expected connection-related errors only
                print("Connection Failed:", e)
                print("Retrying in 5 seconds...")
                time.sleep(5)

    

    def on_connect(
        self,
        client,
        userdata,
        flags,
        rc,
        properties=None,
    ):

        if rc == 0:

            print("Connected to MQTT Broker")

            client.subscribe(MQTT_COMMANDS_TOPIC)

            print(f"Listening for commands on {MQTT_COMMANDS_TOPIC}")

        else:

            print("MQTT Connection Error:", rc)

    

    def on_disconnect(
        self,
        client,
        userdata,
        rc,
        properties=None,
    ):

        print("Disconnected from MQTT")

    def on_message(
        self,
        client,
        userdata,
        msg,
    ):

        if self.command_handler is None:
            return

        try:
            payload = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"Ignoring malformed command message: {exc}")
            return

        printer_id = payload.get("printer_id")
        command = payload.get("command")
        reason = payload.get("reason")

        if not printer_id or not command:
            print(f"Ignoring incomplete command message: {payload}")
            return

        print(f"Received command: {command} for {printer_id} (reason: {reason})")

        self.command_handler(printer_id, command, reason)

    
    def publish(self, data):

        payload = json.dumps(data)

        self.client.publish(
            MQTT_TOPIC,
            payload
        )