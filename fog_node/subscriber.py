import json
import paho.mqtt.client as mqtt

from config import MQTT_BROKER
from config import MQTT_PORT
from config import MQTT_TOPIC
import config


class MQTTSubscriber:

    def __init__(self, callback):

        self.callback = callback

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="fog-node"
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties=None
    ):

        print("Connected to MQTT")

        client.subscribe(MQTT_TOPIC)

        print(f"Subscribed to {MQTT_TOPIC}")

    def on_message(
        self,
        client,
        userdata,
        msg
    ):

        data = json.loads(msg.payload.decode())

        self.callback(data)

    def publish_command(self, printer_id, command, reason=None):
        """
        Publishes a command (e.g. "HALT") back to the sensor simulator
        for a specific printer, on MQTT_COMMANDS_TOPIC. Uses the same
        already-connected client this subscriber is using for incoming
        sensor data - paho-mqtt clients support publishing and
        subscribing on one connection.
        """
        payload = json.dumps({
            "printer_id": printer_id,
            "command": command,
            "reason": reason,
        })
        self.client.publish(config.MQTT_COMMANDS_TOPIC, payload)

    def start(self):

        self.client.connect(
            MQTT_BROKER,
            MQTT_PORT
        )

        self.client.loop_forever()