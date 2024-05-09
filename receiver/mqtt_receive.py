from awsiot import mqtt_connection_builder
from awscrt import mqtt
import time
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64
# import ssl
# from paho.mqtt import client as mqtt_client

endpoint = 'a32kdyeddrrikc-ats.iot.eu-west-2.amazonaws.com'
rootca = 'connect_device_package/root-CA.crt'
private_key = 'connect_device_package/fragment.private.key'
cert = 'connect_device_package/fragment.cert.pem'
decrypt_key = 'connect_device_package/private_mqtt.pem'

client_id = 'fragment'
topic = 'mqtt/fr/6775888955'

def decrypt_msg(receive_msg, private_key_path):
    msg = base64.b64decode(receive_msg)
    private_key = RSA.import_key(open(private_key_path).read())
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher_rsa.decrypt(msg)
    return decrypted_message.decode()

# connection callback functions
def on_connection_succuess(clientconnection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print(f'Connection successful with return code: {callback_data.return_code}, session present: {callback_data.session_present}.')
    
def on_connection_interrupted(clientconnection, error, *kwargs):
    print(f'Connection interrupted, with error {error}.')

def on_connection_closed(clientconnection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionClosedData)
    print(f'Connection closed.')
    
def on_connection_failure(clientconnection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print(f'Connection failed with error code {callback_data.error}')

def on_connection_resumed(clientconnection, return_code, session_present, **kwargs):
    print(f'Connection resumed. Return code = {return_code}, session present = {session_present}')

def on_message_received(topic, payload, dup, qos, retain, **kwargs):
        msg = decrypt_msg(payload, decrypt_key)
        print(f'topic:{topic}, payload:{msg}, qos:{qos} \n')

client = mqtt_connection_builder.mtls_from_path(
    endpoint=endpoint,
    port=8883,
    cert_filepath=cert,
    pri_key_filepath=private_key,
    ca_filepath=rootca,
    client_id=client_id,
    clean_session=False,
    keep_alive_secs=30,
    on_connection_success=on_connection_succuess,
    on_connection_interrupted=on_connection_interrupted,
    on_connection_closed=on_connection_closed,
    on_connection_failure=on_connection_failure,
    on_connection_resumed=on_connection_resumed
)

connect_future = client.connect()    
connect_result = connect_future.result()
print(f'Connect to AWS IoT core, session present: {connect_result["session_present"]}')

subscribe_future, packet_id = client.subscribe(
     topic=topic,
     qos=mqtt.QoS.AT_LEAST_ONCE,
     callback=on_message_received
)
print(f'Subscribe with {subscribe_future.result()}')

subscribe_result = subscribe_future.result()
print(f'Subscribe with {subscribe_result["topic"]} on AWS IoT.')

while True:
    time.sleep(1)
