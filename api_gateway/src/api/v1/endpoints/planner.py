# api_gateway/src/api/v1/endpoints/planner.py
import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from shared.models.schemas import UserGoalRequest
from shared.models.database import SessionLocal
from shared.models.models import TaskResult
from api_gateway.src.api.services import QueueService

router = APIRouter()

# Schema for the quick queue receipt
class TaskReceiptResponse(BaseModel):
    task_id: str
    status: str
    message: str

# Schema for checking the execution result
class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result_data: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None

# Dependencies
def get_queue_service() -> QueueService:
    return QueueService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/plan", 
    response_model=TaskReceiptResponse, 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueues a natural language planning request for async processing"
)
async def create_plan_async(
    request: UserGoalRequest,
    queue_service: QueueService = Depends(get_queue_service)
):
    """
    Accepts raw user text, generates a secure Tracking UUID, pushes the task 
    into the RabbitMQ message broker, and immediately returns a 202 status.
    """
    task_id = str(uuid.uuid4())
    
    await queue_service.publish_task(
        task_id=task_id,
        raw_text=request.raw_text,
        user_id=request.user_id
    )
    
    return TaskReceiptResponse(
        task_id=task_id,
        status="pending",
        message="Your day plan is being processed by our AI engine. Please track status using the task_id."
    )

@router.get(
    "/plan/{task_id}",
    response_model=TaskResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve the status and result of an asynchronous planning task"
)
def get_plan_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Checks the database for the status of a specific task_id.
    Returns the calculated timeline if the task succeeded.
    """
    task = db.query(TaskResult).filter(TaskResult.task_id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found."
        )
        
    return TaskResultResponse(
        task_id=task.task_id,
        status=task.status,
        result_data=task.result_data,
        error_message=task.error_message
    )
