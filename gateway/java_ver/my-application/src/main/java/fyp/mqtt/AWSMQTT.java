package fyp.mqtt;

import com.amazonaws.services.iot.client.AWSIotMqttClient;
import com.amazonaws.services.iot.client.AWSIotException;
import com.amazonaws.services.iot.client.AWSIotMessage;
import com.amazonaws.services.iot.client.AWSIotQos;
import com.amazonaws.services.iot.client.AWSIotTimeoutException;
import com.amazonaws.services.iot.client.AWSIotTopic;
import com.amazonaws.services.iot.client.sample.sampleUtil.SampleUtil;
import com.amazonaws.services.iot.client.sample.sampleUtil.SampleUtil.KeyStorePasswordPair;

public class AWSMQTT {
    // private static String clientEndpoint = "a32kdyeddrrikc-ats.iot.eu-west-2.amazonaws.com";
    // private static String clientId = "rasp_pi_gateway";
    // private static String certificateFile = "project/aws_access/Raspberry_gateway.cert.pem";
    // private static String privateKeyFile = "project/aws_access/Raspberry_gateway.private.key";
    public static KeyStorePasswordPair pair;
    public static AWSIotMqttClient client;
    

    public AWSMQTT(String certificateFile, String privateKeyFile, String clientEndpoint, String clientId) throws Exception{
        pair = SampleUtil.getKeyStorePasswordPair(certificateFile, privateKeyFile);
        client = new AWSIotMqttClient(clientEndpoint, clientId, pair.keyStore, pair.keyPassword);

        AWSTopicCallback topic = new AWSTopicCallback("aws/mqtt/java", AWSIotQos.QOS1);
        client.subscribe(topic);

        client.connect();
    }

    public static void trans_aws(String topic, String message) throws AWSIotException{
        client.publish(topic, AWSIotQos.QOS1, message);
    }
}

