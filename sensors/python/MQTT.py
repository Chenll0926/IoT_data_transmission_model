import paho.mqtt.client as mqtt
import requests
import json
import time
import csv
from datetime import datetime
import pandas as pd
import data_send
import ssl
import os
import threading

retry_interval = 5
max_retries = 3
retry_count = 0

broker_add = "100.81.240.82"
port = 1883
topic = 'rasp/mqtt'
client_id = 'heartrate_sec_sensor'

# heart_rate_data = data_send.Get_data.seconds_path['heartrate']
heartrate_data = [os.path.join('dataset/heartrate', file) for file in os.listdir('dataset/heartrate') if file.endswith('.csv')]

def on_connect(client, userdate, flags, rc, properties):
    if rc == 0:
        print('Connect to MQTT broker.')
    else:
        print("Connection failed.")

def on_disconnect(client, userdate, rc):
     if not rc == 0:
          print('Unexpect disconection.')
          client.reconnect()


def main():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
        clean_session=False
        )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(
        host=broker_add,
        port=port,
        keepalive=60
    )

    client.loop_start()

    threads = []

    for file in heartrate_data:
        thread = threading.Thread(target=data_send.Get_data.mqtt_send_heartrate_data, args=(client, topic, file))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()


# while True:
#     data_send.Get_data.mqtt_send_heartrate_data(client, topic, heart_rate_data)


   

