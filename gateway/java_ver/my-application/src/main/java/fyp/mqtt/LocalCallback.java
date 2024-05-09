package fyp.mqtt;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import com.amazonaws.services.iot.client.AWSIotException;

public class LocalCallback implements MqttCallback {

    public void connectionLost(Throwable cause) {
        System.out.println("connection lost: " + cause.getMessage());
    }

    public void messageArrived(String topic, MqttMessage message) throws AWSIotException{
        System.out.println("Received message: \n  topic: " + topic + "\n  Qos: " + message.getQos() + "\n  payload: " + new String(message.getPayload()));
        AWSMQTT.trans_aws("aws/mqtt/java", new String(message.getPayload()));
    }

    public void deliveryComplete(IMqttDeliveryToken token) {
        System.out.println("deliveryComplete");
    }
}

