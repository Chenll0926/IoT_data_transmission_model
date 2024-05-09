import fyp.mqtt.AWSMQTT;
import fyp.mqtt.LocalMQTT;

public class LocalTrans {
    public static String localBroker = "tcp://localhost:1883";
    public static String localClientId = "rasp_pi_gateway";
    public static String localTopic = "rasp/mqtt";

    public static String clientEndpoint = "a32kdyeddrrikc-ats.iot.eu-west-2.amazonaws.com";
    public static String AWSClientId = "rasp_pi_gateway";
    public static String certificateFile = "project/aws_access/Raspberry_gateway.cert.pem";
    public static String privateKeyFile = "project/aws_access/Raspberry_gateway.private.key";

    public static void main(String[] args) throws Exception {
        AWSMQTT awsClient = new AWSMQTT(certificateFile, privateKeyFile, clientEndpoint, AWSClientId);
        LocalMQTT localClient = new LocalMQTT(localBroker, localClientId, localTopic, awsClient);

    }
}
