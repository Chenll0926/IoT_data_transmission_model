import paho.mqtt.client as mqtt
import requests
import json
import time
import csv
from datetime import datetime
import pandas as pd
import data_send
import ssl

retry_interval = 5
max_retries = 3
retry_count = 0

broker_add = "100.81.240.82"
# port = 1883
port=8883
topic = 'rasp/mqtt'
client_id = 'heartrate_sec_sensor'

heart_rate_data = data_send.Get_data.seconds_path['heartrate']

def on_connect(client, userdate, flags, rc, properties):
    if rc == 0:
        print('Connect to MQTT broker.')
    else:
        print("Connection failed.")

def on_disconnect(client, userdate, rc):
     if not rc == 0:
          print('Unexpect disconection.')
          client.reconnect()


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=client_id,
    clean_session=False
    )

client.tls_set(
    ca_certs='code/mqttssl/ca.crt',
    certfile='code/mqttssl/mqtt.crt',
    keyfile='code/mqttssl/mqtt.key',
    cert_reqs=ssl.CERT_NONE,
    tls_version=ssl.PROTOCOL_TLSv1_2,
    ciphers=None
)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect(
     host=broker_add,
     port=port,
     keepalive=60
)

client.loop_start()


while True:
    data_send.Get_data.mqtt_send_heartrate_data(client, topic, heart_rate_data)


   

