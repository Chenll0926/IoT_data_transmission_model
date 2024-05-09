package fyp.java;

import org.bouncycastle.asn1.pkcs.PrivateKeyInfo;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.openssl.PEMKeyPair;
import org.bouncycastle.openssl.PEMParser;
import org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.json.JSONObject;

import javax.net.ssl.*;
import java.io.*;
import java.security.*;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.Base64;

public class MQTTSslClient {
    private static final String BROKER_URL = "tcp://100.81.240.82:1883";
    private static final String CLIENT_ID = "heartrate_sec_sensor";
    private static final String TOPIC = "rasp/mqtt";
    private static final String CA_FILE_PATH = "mqtt/src/main/resources/mqttssl/ca.crt";
    private static final String CRT_FILE_PATH = "mqtt/src/main/resources/mqttssl/mqtt.crt";
    private static final String KEY_FILE_PATH = "mqtt/src/main/resources/mqttssl/mqtt.key";
    private static final String DATA_FILE_PATH = "mqtt/src/main/resources/heartrate";
    private static final int qos = 2;

    public static void main(String[] args) {

        HttpsURLConnection.setDefaultHostnameVerifier(new HostnameVerifier() {
            public boolean verify(String hostname, SSLSession session) {
                return true; // 不推荐，仅用于测试目的
            }
        });

        File[] files = getFileName(DATA_FILE_PATH);
        ExecutorService executor = Executors.newFixedThreadPool(files.length);

        MqttConnectOptions connOpts = new MqttConnectOptions();

//        try {
//            connOpts.setSocketFactory(getSocketFactory(CA_FILE_PATH, CRT_FILE_PATH, KEY_FILE_PATH, "880416"));
//        } catch (Exception e) {
//            throw new RuntimeException(e);
//        }

        try {
            MqttClient client = new MqttClient(BROKER_URL, CLIENT_ID, new MemoryPersistence());

            client.setCallback(new Callback());

            System.out.println("Connecting to broker: " + BROKER_URL);
            client.connect(connOpts);
            System.out.println("Connected to broker: " + BROKER_URL);

            client.subscribe(TOPIC, qos);
            System.out.println("Subscribed to topic: " + TOPIC);

            for (File file: files){
                executor.submit(() -> sendData(client, file));
            }

            executor.shutdown();

            while (!executor.isTerminated()){

            }

//            client.disconnect();
//            System.out.println("Disconnected from broker: " + BROKER_URL);
//            client.close();
//            System.exit(0);

        } catch (MqttException me) {
            System.out.println("reason " + me.getReasonCode());
            System.out.println("msg " + me.getMessage());
            System.out.println("loc " + me.getLocalizedMessage());
            System.out.println("cause " + me.getCause());
            System.out.println("excep " + me);
            me.printStackTrace();
        }
    }

    private static File[] getFileName(String filePath){
        File folder = new File(DATA_FILE_PATH);
        File[] files = folder.listFiles();
        return files;
    }

    private static void sendData(MqttClient client, File file) {
        boolean firstline = true;
        SimpleDateFormat dateFormat = new SimpleDateFormat("M/d/yyyy h:mm:ss a", Locale.US);
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            String line;
            Date prevTimestamp = null;
            while ((line = br.readLine()) != null) {
                if (firstline) {
                    firstline = false;
                    continue;
                }

                String[] parts = line.split(",");
                Date currentTimestamp = dateFormat.parse(parts[1]);
                if (prevTimestamp != null) {
                    long interval = currentTimestamp.getTime() - prevTimestamp.getTime();
                    Thread.sleep(interval);
                }

                JSONObject json = new JSONObject();
                json.put("Id", parts[0]);
                json.put("Time", parts[1]);
                json.put("Value", parts[2]);

//                MqttMessage message = new MqttMessage(line.getBytes());
                MqttMessage message = new MqttMessage(json.toString().getBytes());
                message.setQos(1);
                client.publish(TOPIC, message);
                System.out.println("Message published from " + file.getName() + ": " + line);
                prevTimestamp = currentTimestamp;
            }
        } catch (IOException | InterruptedException | ParseException | MqttException e) {
            e.printStackTrace();
        }
    }

    private static SSLSocketFactory getSocketFactory(final String caFilePath,
                                                     final String crtFilePath, final String keyFilePath, final String password)
            throws Exception {
        // 实现SSL Socket Factory
        Security.addProvider(new BouncyCastleProvider());

        // load ca certificate
        X509Certificate caCert = null;
        FileInputStream fis = new FileInputStream(caFilePath);
        BufferedInputStream bis = new BufferedInputStream(fis);
        CertificateFactory cf = CertificateFactory.getInstance("X.509");

        while (bis.available() > 0) {
            caCert = (X509Certificate) cf.generateCertificate(bis);
        }
//        X509Certificate caCert = (X509Certificate) cf.generateCertificate(caInput);

        // load client certificate
        bis = new BufferedInputStream(new FileInputStream((crtFilePath)));
        X509Certificate cert = null;
        while (bis.available() > 0) {
            cert = (X509Certificate) cf.generateCertificate(bis);
        }

        // load client private key
        PEMParser pemParser = new PEMParser(new FileReader(keyFilePath));
        Object object = pemParser.readObject();
        JcaPEMKeyConverter converter = new JcaPEMKeyConverter().setProvider("BC");
//        System.out.println(object instanceof PrivateKeyInfo);
        PrivateKey key = converter.getPrivateKey((PrivateKeyInfo) object);
        pemParser.close();

        // CA certificate is used to authenticate server
        KeyStore caKs = KeyStore.getInstance(KeyStore.getDefaultType());
        caKs.load(null, null);
        caKs.setCertificateEntry("ca", caCert);
        TrustManagerFactory tmf = TrustManagerFactory.getInstance("X509");
        tmf.init(caKs);

        // client key and certificates are sent to server
        KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());
        ks.load(null, null);
        ks.setCertificateEntry("certificate", cert);
        ks.setKeyEntry("private-key", key, password.toCharArray(),
                new java.security.cert.Certificate[]{cert});
        KeyManagerFactory kmf = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        kmf.init(null, password.toCharArray());

        // create SSL socket factory
        SSLContext context = SSLContext.getInstance("TLSv1.2");
        context.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);
        return context.getSocketFactory();
    }
}