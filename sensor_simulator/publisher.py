import json
import time

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_TOPIC,
    MQTT_CLIENT_ID,
)


class MQTTPublisher:

    def __init__(self):

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=MQTT_CLIENT_ID,)
        self.client.on_connect = self.on_connect

        self.client.on_disconnect = self.on_disconnect

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

    
    def publish(self, data):

        payload = json.dumps(data)

        self.client.publish(
            MQTT_TOPIC,
            payload
        )