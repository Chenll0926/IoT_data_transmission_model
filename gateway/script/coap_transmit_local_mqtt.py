import asyncio
from aiocoap import *
import paho.mqtt.client as mqtt
from aiocoap.resource import Resource, Site

# local mqtt info
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'rasp/coap'

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

mqtt_client.loop_start()

async def coap_server():
    class CoAPResource(Resource):
        async def render_post(self, request):
            payload = request.payload.decode('utf-8')
            print(f"Received CoAP message: {payload}")

            mqtt_client.publish(MQTT_TOPIC, payload)
            print(f'Transmit message {payload} to local MQTT topic {MQTT_TOPIC}')
            return Message(code=Code.CONTENT, payload=b"Forwarded to MQTT")

    root = Site()
    root.add_resource(['raspberry'], CoAPResource())

    await Context.create_server_context(root)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(coap_server())
    asyncio.get_event_loop().run_forever()