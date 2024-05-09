import asyncio
from aiohttp import web
import paho.mqtt.client as mqtt

# local mqtt info
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'rasp/http'

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

mqtt_client.loop_start()

async def handle_http_request(request):
    request_body = await request.text()
    print('Receive message: ', request_body)
    
    mqtt_client.publish(MQTT_TOPIC, request_body)
    print(f'Transmit message {request_body} to local MQTT topic {MQTT_TOPIC}.')
    
    return web.Response(text="Request forwarded to MQTT")

async def start_http_server():
    app = web.Application()
    app.router.add_post('/api/data', handle_http_request)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_http_server())
    loop.run_forever()