# ai_planner/src/worker.py
import os
import json
import asyncio
import aio_pika
from sqlalchemy.orm import Session
from shared.models.database import SessionLocal
from shared.models.models import TaskResult
from ai_planner.src.agents.parser import extract_schedule_goals
from ai_planner.src.tools.scheduler import calculate_backward_schedule

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

async def process_task(message: aio_pika.IncomingMessage):
    """
    Callback function triggered whenever a new task is received from RabbitMQ.
    """
    async with message.process():  # Automatically ACKs the message if no exception occurs
        db: Session = SessionLocal()
        payload = json.loads(message.body.decode("utf-8"))
        
        task_id = payload["task_id"]
        user_id = payload["user_id"]
        raw_text = payload["raw_text"]
        
        print(f"\n⚙️ [Worker] Starting task {task_id} for user {user_id}...")
        
        # 1. Register task in database as 'processing'
        task_record = db.query(TaskResult).filter(TaskResult.task_id == task_id).first()
        if not task_record:
            task_record = TaskResult(task_id=task_id, user_id=user_id, status="processing")
            db.add(task_record)
        else:
            task_record.status = "processing"
        db.commit()

        try:
            # 2. Extract goals using local Ollama (This can take some time!)
            print(f"🤖 [Worker] Processing NLP with Ollama...")
            extracted_goals = extract_schedule_goals(raw_text)
            
            # 3. Calculate backward schedule using database specs
            print(f"🧮 [Worker] Calculating backward scheduling math...")
            timeline = calculate_backward_schedule(extracted_goals)
            
            # 4. Serialize tasks to JSON-compatible list of dicts
            serialized_timeline = [task.model_dump(mode="json") for task in timeline]
            
            # 5. Save success result to DB
            task_record.status = "success"
            task_record.result_data = serialized_timeline
            db.commit()
            print(f"✅ [Worker] Task {task_id} completed successfully and saved to PostgreSQL!")
            
        except Exception as e:
            # Log any failure (Ollama offline, SQL errors, etc.) to the database
            db.rollback()
            task_record.status = "failed"
            task_record.error_message = str(e)
            db.commit()
            print(f"❌ [Worker] Task {task_id} failed: {str(e)}")
        finally:
            db.close()

async def main():
    """
    Main worker loop that establishes a connection to RabbitMQ
    and listens to the task queue.
    """
    print("🐇 Starting LifeSync AI Worker. Waiting for tasks...")
    
    # Establish connection
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    
    # Open channel
    channel = await connection.channel()
    
    # Prefetch count limits how many unacknowledged messages are sent to this worker at once
    await channel.set_qos(prefetch_count=1)
    
    # Declare the queue
    queue = await channel.declare_queue("planning_tasks", durable=True)
    
    # Start consuming tasks using our callback
    await queue.consume(process_task)
    
    # Keep the worker running indefinitely
    try:
        await asyncio.Future()
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
