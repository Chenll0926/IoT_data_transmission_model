package fyp.mqtt;

import com.amazonaws.services.iot.client.AWSIotMessage;
import com.amazonaws.services.iot.client.AWSIotQos;
import com.amazonaws.services.iot.client.AWSIotTopic;

public class AWSTopicCallback extends AWSIotTopic{
    public AWSTopicCallback(String topic, AWSIotQos qos) {
        super(topic, qos);
    }

    @Override
    public void onMessage(AWSIotMessage message) {
        // called when a message is received
        System.out.println("Topic: " + message.getTopic() + " Payload: " + message.getStringPayload().toString() + " QoS: " + message.getQos());
    }

}
