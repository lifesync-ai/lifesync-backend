# ai_planner/src/main.py
from fastapi import FastAPI, HTTPException
from shared.models.schemas import UserGoalRequest, ProposedTimelineResponse
from ai_planner.src.agents.parser import extract_schedule_goals
from ai_planner.src.tools.scheduler import calculate_backward_schedule
import uuid
from datetime import datetime

app = FastAPI(
    title="LifeSync AI Planner Service",
    description="Internal microservice responsible for NLP parsing and backward scheduling math.",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    """Simple health check endpoint for monitoring."""
    return {"status": "healthy", "service": "ai_planner"}

@app.post("/api/v1/planner/generate", response_model=ProposedTimelineResponse)
def generate_schedule(payload: UserGoalRequest):
    """
    Endpoint that accepts raw text, parses it using local LLM (Ollama),
    queries DB specs, calculates backward schedule, and returns structured timeline.
    """
    try:
        # 1. Extract semantic goals from raw text via Ollama
        extracted_goals = extract_schedule_goals(payload.raw_text)
        
        # 2. Compute backward scheduling using PostgreSQL configurations
        # We default target date to tomorrow for now
        computed_tasks = calculate_backward_schedule(extracted_goals)
        
        # 3. Formulate the contract-compliant response
        return ProposedTimelineResponse(
            request_id=str(uuid.uuid4()),
            status="success",
            calculated_at=datetime.utcnow(),
            timeline=computed_tasks
        )
    except Exception as e:
        # Log internal errors and return 500
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate schedule: {str(e)}"
        )
