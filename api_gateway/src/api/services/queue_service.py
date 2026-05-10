# api_gateway/src/services/queue_service.py
import os
import json
import aio_pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

# Construct the AMQP connection URL
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

class QueueService:
    """
    Service responsible for publishing task messages to RabbitMQ asynchronously.
    """
    def __init__(self):
        self.url = RABBITMQ_URL
        self.queue_name = "planning_tasks"

    async def publish_task(self, task_id: str, raw_text: str, user_id: str):
        """
        Connects to RabbitMQ, ensures the queue exists, and publishes the task payload.
        """
        # 1. Establish connection to RabbitMQ
        connection = await aio_pika.connect_robust(self.url)
        
        async with connection:
            # 2. Create a channel
            channel = await connection.channel()
            
            # 3. Declare the queue (creates it if it doesn't exist yet)
            queue = await channel.declare_queue(
                self.queue_name, 
                durable=True  # Queue survives RabbitMQ restarts
            )
            
            # 4. Prepare the message payload
            payload = {
                "task_id": task_id,
                "user_id": user_id,
                "raw_text": raw_text
            }
            
            message_body = json.dumps(payload).encode("utf-8")
            
            # 5. Publish the message with persistent delivery mode
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # Message survives broker restarts
                ),
                routing_key=self.queue_name
            )
            
            print(f"📥 [RabbitMQ] Successfully published task {task_id} to queue '{self.queue_name}'")
