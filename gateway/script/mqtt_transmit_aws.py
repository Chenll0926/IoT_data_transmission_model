import aws_mqtt_client
import local_mqtt_client
import json
import asyncio
import asyncio

# get mqtt info
aws_info = []
local_info = []
with open('project/mqtt_client.json', 'r') as file:
    data = json.load(file)
    aws_info = data['aws']
    local_info = data['local']

topics = [tuple(item) for item in local_info['topic']]

# init aws and local mqtt client
aws = aws_mqtt_client.AWSMQTTClient(aws_info['endpoint'], aws_info['port'], aws_info['cert'], aws_info['private-key'],
                                    aws_info['root-ca'], aws_info['client-id'], aws_info['topic'])
mqtt_local = local_mqtt_client.LocalMQTTClient(local_info['broker'], local_info['port'], topics, aws)

mqtt_local.set_on_connect()    
mqtt_local.set_on_message()
# mqtt_local.aggregated_and_send()
mqtt_local.set_client_loop()
