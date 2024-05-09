package fyp.mqtt;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import com.amazonaws.services.iot.client.AWSIotMqttClient;

public class LocalMQTT {

    public LocalMQTT(String broker, String clientId, String topic, AWSMQTT awsclient) {
        try {
            MqttClient client = new MqttClient(broker, clientId, new MemoryPersistence());
            MqttConnectOptions connOpts = new MqttConnectOptions();
            client.setCallback(new LocalCallback());
            client.connect(connOpts);

            client.subscribe(topic);

        } catch (MqttException me) {
            me.printStackTrace();
        }
    }
}