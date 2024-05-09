from awsiot import mqtt_connection_builder
import json
import time
from awscrt import mqtt, http
import threading
import encrypt


class AWSMQTTClient:

    def __init__(self, endpoint, port, cert, pri, ca, clientId, topic):
        self.topic = topic

        # build aws mqtt client
        self.aws_mqtt = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            port=port,
            cert_filepath=cert,
            pri_key_filepath=pri,
            ca_filepath=ca,
            client_id=clientId,
            clean_session=False,
            keep_alive_secs=30,
            on_connection_success=self.on_connection_succuess,
            on_connection_interrupted=self.on_connection_interrupted,
            on_connection_closed=self.on_connection_closed,
            on_connection_failure=self.on_connection_failure,
            on_connection_resumed=self.on_connection_resumed
        )

        connect_future = self.aws_mqtt.connect()
        connect_result = connect_future.result()
        print(f'Connect to AWS IoT core, session present: {connect_result["session_present"]}')

        for key in self.topic.keys():
            print(self.topic[key])
            subscribe_future, packet_id = self.aws_mqtt.subscribe(
                topic=self.topic[key], 
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self.on_message_received)
            print(f'Subscribe with {subscribe_future.result()}')
        subscribe_result = subscribe_future.result()
        print(f'Subscribe with {subscribe_result["topic"]} on AWS IoT.')

        self.message = None

    # connection callback functions
    def on_connection_succuess(self, connection, callback_data):
        assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
        print(f'Connection successful with return code: {callback_data.return_code}, session present: {callback_data.session_present}.')
    
    def on_connection_interrupted(self, connection, error, *kwargs):
        print(f'Connection interrupted, with error {error}.')

    def on_connection_closed(self, connection, callback_data):
        assert isinstance(callback_data, mqtt.OnConnectionClosedData)
        print(f'Connection closed.')
    
    def on_connection_failure(self, connection, callback_data):
        assert isinstance(callback_data, mqtt.OnConnectionFailureData)
        print(f'Connection failed with error code {callback_data.error}')

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        print(f'Connection resumed. Return code = {return_code}, session present = {session_present}')

    # operate aws mqtt client connect to aws iot core
    def make_aws_connection(self):
        self.connect_future = self.aws_mqtt.connect()
        connect_result = self.connect_future.result()
        print(connect_result['session_present'])
        print('Connected to AWS MQTT!')
        self.aws_mqtt.on_message

    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        print(f'topic:{topic}, payload:{payload}, qos:{qos} \n')
        
    def sub_aws_topic(self):
        for key in self.topic.keys():
            print(self.topic[key])
            subscribe_future, packet_id = self.aws_mqtt.subscribe(
                topic=self.topic[key], 
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self.on_message_received)
            print(f'Subscribe with {subscribe_future.result()}')

    def trans_msg(self, message, topic):
        self.message = message
        print(f'Received message {message.payload.decode()} from raspberry pi, with qos {message.qos}.\n')
        if not message == None:
            if topic == 'rasp/mqtt':
                data = self.message.payload.decode()
                data_id = json.loads(data)['Id']
                msg = encrypt.Encrypt.encrypt_msg(data, 'public_mqtt.pem')

                if 'Average' in json.loads(data):
                    self.aws_mqtt.publish(topic=f'aws/mqtt/{data_id}/average', payload=msg, qos=mqtt.QoS.AT_LEAST_ONCE)
                    print(f'Publishing message to AWS IoT with topic aws/mqtt/{data_id}/average: {msg}.')
                else:
                    print(f'Publishing message to AWS IoT with topic aws/mqtt/{data_id}: {msg}.')
                    self.aws_mqtt.publish(topic=f'aws/mqtt/{data_id}', payload=msg, qos=mqtt.QoS.AT_LEAST_ONCE)
            elif topic == 'rasp/coap':
                data = self.message.payload.decode()
                data_id = json.loads(data)['Id']

                print(f'Publishing message to AWS IoT with topic aws/coap/{data_id}: {self.message.payload.decode()}.')
                self.aws_mqtt.publish(topic=f'aws/coap/{data_id}', payload=self.message.payload.decode(), qos=mqtt.QoS.AT_LEAST_ONCE) 
            elif topic == 'rasp/http':
                print(f'Publishing message to AWS IoT with topic aws/http/info: {self.message.payload.decode()}.')
                self.aws_mqtt.publish(topic=f'aws/http/info', payload=self.message.payload.decode(), qos=mqtt.QoS.AT_LEAST_ONCE)
        else:
            print('Do not receive message.')
        self.message = None
