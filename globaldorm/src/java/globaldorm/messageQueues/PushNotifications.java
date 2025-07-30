/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm.messageQueues;

import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeoutException;

/**
 * Handles sending push notifications via RabbitMQ, primarily using a fanout exchange for broad distribution.
 *
 * @author I_NEE
 * @see <a href="https://www.rabbitmq.com/tutorials/tutorial-three-java.html">RabbitMQ Java Tutorial (Publish/Subscribe)</a>
 * @see <a href="https://www.rabbitmq.com/api-guide.html#exchanges-and-queues">RabbitMQ API Guide (Exchanges and Queues)</a>
 */
public class PushNotifications {

    private static enum EXCHANGE_TYPE {DIRECT, FANOUT, TOPIC, HEADERS};

    private static final String EXCHANGE_NAME = "hello";
    private static final String TOPIC_KEY_NAME = ""; // username1.username2...
    private static final String HOST = "localhost"; // default IP
    private static final String USERNAME = "guest"; // replace this
    private static final String PASSWORD = "guest"; // and this

    /**
     * Sends a message to a RabbitMQ fanout exchange, broadcasting it to all bound queues.
     *
     * @param message The content of the notification message.
     */
    public void pushNotificationFanout(String message) {
        Connection connection = null;
        Channel channel = null;
        try {
            // establish connection
            ConnectionFactory factory = new ConnectionFactory() {};
            factory.setHost(HOST);
            factory.setUsername(USERNAME);
            factory.setPassword(PASSWORD);

            connection = factory.newConnection();
            channel = connection.createChannel();

            // declare exchange (fanout)
            channel.exchangeDeclare(EXCHANGE_NAME, EXCHANGE_TYPE.FANOUT.toString().toLowerCase());

            // publish
            channel.basicPublish(
                EXCHANGE_NAME,
                TOPIC_KEY_NAME,
                new AMQP.BasicProperties.Builder()
                    .contentType("text/plain")
                    .deliveryMode(2)
                    .priority(1)
                    .userId(USERNAME)
                    .build(),
                message.getBytes(StandardCharsets.UTF_8)
            );

            System.out.println(" [x] Sent '" + TOPIC_KEY_NAME + ":" + message + "'");
        } catch (IOException | TimeoutException e) {
            System.out.println("Error occurred while sending message: " + e.getMessage());
        } finally {
            try {
                if (channel != null) channel.close();
                if (connection != null) connection.close();
            } catch (IOException | TimeoutException ex) {
                System.out.println("Error occurred while closing resources: " + ex.getMessage());
            }
        }
    }

    // Placeholder. Live chat is pending...
    public void liveSupportChat() {}
}
