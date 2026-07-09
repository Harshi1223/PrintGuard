import json
import paho.mqtt.client as mqtt

from config import MQTT_BROKER
from config import MQTT_PORT
from config import MQTT_TOPIC


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

    def start(self):

        self.client.connect(
            MQTT_BROKER,
            MQTT_PORT
        )

        self.client.loop_forever()