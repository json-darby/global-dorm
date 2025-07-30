import pika
import threading
import time
import uuid  # timestamp based
# import queue

# USE CMD TERMINAL TO TEST, NETBEANS ONE DOESN'T WORK WITH PYTHON!!!


# RabbitMQSubscriber
class PushNotifications:
    """
    Manages RabbitMQ push notifications by subscribing to a fanout exchange.
    Receives and processes messages, and can put them into a message queue for other parts of the application.
    """
    def __init__(self, host='localhost', username='guest', password='guest', exchange_name='hello', message_queue=None):
        """
        Initialises the PushNotifications subscriber.

        - host: RabbitMQ server host.
        - username: Username for RabbitMQ authentication.
        - password: Password for RabbitMQ authentication.
        - exchange_name: The name of the fanout exchange to subscribe to.
        - message_queue: An optional queue to put received messages into.
        """
        self.host = host
        self.username = username
        self.password = password
        self.exchange_name = exchange_name
        self.queue_name = str(uuid.uuid4())  # queue_name - doing round robin!!!
        self.connection = None
        self.channel = None
        self.is_listening = False  # previous forever loop and to stop the message broker...
        self.message_queue = message_queue

    def create_connection(self):
        """Establishes a connection to the RabbitMQ server."""
        try:
            print("Connecting to RabbitMQ...")
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(host=self.host, credentials=credentials)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            print("Connection established.")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            raise

    def setup_queue_and_exchange(self):
        """Declares the fanout exchange and binds a unique queue to it to receive all messages."""
        # state the exchange and bind the queue to it
        try:
            self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
            # exclusive=False allows other consumers to connect to the same queue_name (though it's unique here)
            self.channel.queue_declare(queue=self.queue_name, durable=False, exclusive=False)
            self.channel.queue_bind(queue=self.queue_name, exchange=self.exchange_name)

#            print(f"Queue '{self.queue_name}' is ready to receive messages.")
            print("Push notifications are now active.")
        except Exception as e:
            print(f"Failed to declare exchange or queue: {e}")
            raise

    def message_received(self, ch, method, properties, body):
        """
        Callback function executed when a message is received from the RabbitMQ queue.
        Decodes the message and, if a message queue is provided, puts the message into it.
        """
        try:
            message = body.decode('utf-8')
            print(f"*** New Update... '{message}' ***")
            if self.message_queue:
                self.message_queue.put(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")

    def listen_for_messages(self):
        """
        Starts listening for messages from the RabbitMQ server in a separate thread.
        Sets up the queue and exchange before starting consumption.
        """
        self.create_connection()
        self.setup_queue_and_exchange()

        self.is_listening = True
        print("listening")  # for terminal testing

        consume_thread = threading.Thread(target=self._consume_messages)
        consume_thread.start()

    def _consume_messages(self):
        """
        Continuously consumes messages from the RabbitMQ channel.
        Runs in a separate thread.
        """
        # "private", seperate thread function of consume_messages
        try:
            while self.is_listening:
                if self.is_listening:
                    self.channel.basic_consume(
                        queue=self.queue_name,
                        on_message_callback=self.message_received,
                        auto_ack=False  # manual acknowledgment
                    )
                    self.channel.start_consuming()
                time.sleep(0.1) # Small delay to prevent tight loop when stop_consuming is called
        except pika.exceptions.AMQPError as e:
            print(f"AMQP error during message consumption: {e}")
        except Exception as e:
            print(f"Error in consuming messages: {e}")

    def stop_consuming(self):
        """Stops the message consumption process and closes the RabbitMQ connection and channel."""
        self.is_listening = False
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()

#            print("The push notifications feature is offline.")

# command line test - doesn't show in netbeans terminal
# cd Documents/NetBeansProjects/Client/src/
# py RabbitPushNotifications.py


'''
UPDATE UPDATE UPDATE UPDATE
'''

# subscriber = PushNotifications()
#
# subscriber.listen_for_messages()
#
# time.sleep(60)
# subscriber.stop_consuming()