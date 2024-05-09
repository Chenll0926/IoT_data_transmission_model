import paho.mqtt.client as mqtt
import json
import datetime
import threading


class LocalMQTTClient:

    def __init__(self, broker, port, topic, aws_client):
        self.broker = broker
        self.port = port
        self.topic = topic

        self.client = mqtt.Client(
            client_id='Rasp', 
            clean_session=False)
        self.aws_client = aws_client

        self.received_msg = None

        self.client.connect(
            host=broker, 
            port=port, 
            keepalive=60)
        
        self.data_store = {}
        self.lock = threading.Lock()
        
        # self.client.on_subscribe = self.on_subscribe
        # self.client.on_message = self.on_message
        # self.client.loop_forever
        self.aggregated_and_send()
        

    def on_message(self, client, userdata, message):
        self.received_msg = json.loads(message.payload.decode())
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            f"Receive message '{message.payload.decode()}' on topic '{message.topic}' with QoS '{message.qos}' on raspberry pi.")
        
        if message.topic == 'rasp/mqtt':
            if 'Average' not in self.received_msg:
                with self.lock:
                    if self.received_msg['Id'] not in self.data_store:
                        self.data_store[self.received_msg['Id']] = []
                    self.data_store[self.received_msg['Id']].append((self.received_msg['Time'], self.received_msg['Value']))
            self.aws_client.trans_msg(message, message.topic)
        elif message.topic == 'rasp/coap':
            self.aws_client.trans_msg(message, message.topic)
        elif message.topic == 'rasp/http':
            self.aws_client.trans_msg(message, message.topic)

    def aggregated_and_send(self):
        with self.lock:
            for id, values in self.data_store.items():
                if values:
                    average = sum(value for _, value in values) / len(values)
                    msg = {
                        'Id': id,
                        'Type': 'Heart rate',
                        'Time': datetime.datetime.now().isoformat(),
                        'Average': average
                    }
                    self.client.publish('rasp/mqtt', json.dumps(msg))
            self.data_store.clear()
        self.start_aggregation_timer()

    def start_aggregation_timer(self):
        timer = threading.Timer(600, self.aggregated_and_send)
        timer.start()
        
    def on_subscribe(self, client, userdata, mid, rc, properties):
        print(f'Try to subscribe {self.topic} in raspberry pi.')
        self.client.subscribe(self.topic)
    
    def on_connect(self, client, userdata, flags, rc):
        print(f'Connect to raspberry pi broker {self.broker}')
        self.client.subscribe(self.topic)
    
    def set_on_subscribe(self):
        print(f'Try to subscribe {self.topic}')
        self.client.on_subscribe = self.on_subscribe

    def set_on_message(self):
        print('Set on message on mosquitto client')
        self.client.on_message = self.on_message

    def set_on_connect(self):
        print(f'Connect to raspberry pi client {self.broker}:{self.port}')
        self.client.on_connect = self.on_connect
    
    def set_client_loop(self):
        self.client.loop_forever()


    
