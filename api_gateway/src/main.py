import uuid
from fastapi import FastAPI, HTTPException, status
from shared.models.schemas import UserGoalRequest, ProposedTimelineResponse, ScheduledTask
from datetime import datetime, timezone

app = FastAPI(
    title="LifeSync AI - API Gateway",
    version="0.1.0",
    description="The secure entrypoint for the LifeSync AI ecosystem"
)

@app.get('/health')
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}

@app.post(
    "/api/v1/plan", 
    response_model=ProposedTimelineResponse, 
    status_code=status.HTTP_200_OK,
    summary="Generate a personalized timeline based on natural language input"
)
async def create_plan(request: UserGoalRequest):
    """
    Accepts raw user scheduling text and returns a structured timeline response.
    Currently acts as a mock endpoint validating data contracts.
    """
    try:
        # Mock timeline simulating the future output of the AI Planner service
        # Assumes the user asked to run at 9:00 AM and breakfast at 11:00 AM
        mock_timeline = [
            ScheduledTask(
                task_name="Wake Up (Alarm)",
                start_time=datetime(2026, 5, 10, 8, 30),
                end_time=datetime(2026, 5, 10, 8, 45),
                duration_minutes=15,
                is_alarm_required=True,
                description="Time to wake up and prep for your run."
            ),
            ScheduledTask(
                task_name="Morning Run",
                start_time=datetime(2026, 5, 10, 9, 0),
                end_time=datetime(2026, 5, 10, 9, 45),
                duration_minutes=45,
                is_alarm_required=False,
                description="Moderate outdoor run."
            ),
            ScheduledTask(
                task_name="Start Cooking Breakfast",
                start_time=datetime(2026, 5, 10, 10, 30),
                end_time=datetime(2026, 5, 10, 11, 0),
                duration_minutes=30,
                is_alarm_required=True,
                description="Start preparing syrnyky. Recipe: Mix cottage cheese, egg, flour, pan-fry 5 mins each side."
            ),
            ScheduledTask(
                task_name="Breakfast",
                start_time=datetime(2026, 5, 10, 11, 0),
                end_time=datetime(2026, 5, 10, 11, 30),
                duration_minutes=30,
                is_alarm_required=False,
                description="Enjoy your meal!"
            )
        ]
        
        response = ProposedTimelineResponse(
            request_id=str(uuid.uuid4()),
            status="calculated_mock",
            calculated_at=datetime.now(timezone.utc),
            timeline=mock_timeline
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing plan: {str(e)}"
        )
