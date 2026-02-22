import pika
import json
import os

class RabbitMQQueue:

    def publish_job(self, data):
        url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        connection = pika.BlockingConnection(pika.URLParameters(url))
        channel = connection.channel()
        channel.queue_declare(queue='csv_processing', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='csv_processing',
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
