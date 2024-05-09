import json
from datetime import datetime
import pandas as pd
import time
import random
import requests
from aiocoap import Message, Code, Context

class Get_data:
    daily_path = []
    seconds_path = []
    hourly_path = []
    miniute_path = []
    day_path = []
    weight_path = []
    personal_info_path = []

    with open('csv_file_path.json', 'r') as file:
        data = json.load(file)
        daily_path = data['daily']
        seconds_path = data['second']
        hourly_path = data['hourly']
        miniute_path = data['minute']
        day_path = data['day']
        weight_path = data['weight']
        personal_info_path = data['personal']

    def mqtt_send_heartrate_data(client, topic, file_path):
        df = pd.read_csv(file_path)
        df = df[['Time', 'Id', 'Value']]

        prev_timestamp = None

        for index, row in df.iterrows():
            current_timestamp = datetime.strptime(row['Time'], '%m/%d/%Y %I:%M:%S %p')
            if prev_timestamp is not None:
                interval = (current_timestamp - prev_timestamp).total_seconds()
                time.sleep(interval)
            client.publish(topic, row.to_json())
            prev_timestamp = current_timestamp
            print('Send data at ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '\n', row)

    def http_send_personal_data(url, file_path):
        df = pd.read_csv(file_path)
        
        for index, row in df.iterrows():
            interval = random.uniform(0, 120)
            requests.post(url, data=row.to_json(), headers={
                'Content-type': 'application/json'
            })
            time.sleep(interval)
            print('Send data at ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '\n', row)

    async def coap_send_sleep_data(uri, file_path):
        context = await Context.create_client_context()
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y %I:%M:%S %p')
        df = df.sort_values(by='date', ascending=True)

        prev_timestamp = None

        for index, row in df.iterrows():
            current_timestamp = row['date']
            if prev_timestamp is not None:
                interval = (current_timestamp - prev_timestamp).total_seconds()
                time.sleep(interval)
            requests = Message(code=Code.POST, payload=row.to_json().encode('utf8'), uri=uri)
            requests.opt.content_format = 50
            response = await context.request(requests).response
            prev_timestamp = current_timestamp
            print('Send data at ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '\n', row, '\n'
                  'Response code: ', response.code, ' Response payload: ', response.payload)

