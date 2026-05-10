# api_gateway/src/api/v1/endpoints/planner.py
from fastapi import APIRouter, Depends, status
from shared.models.schemas import UserGoalRequest, ProposedTimelineResponse
from api_gateway.src.api.services import AIPlannerClient

router = APIRouter()

# Dependency injection for our HTTP Client
def get_planner_client() -> AIPlannerClient:
    return AIPlannerClient()

@router.post(
    "/plan", 
    response_model=ProposedTimelineResponse, 
    status_code=status.HTTP_200_OK,
    summary="Generate a personalized timeline based on natural language input"
)
async def create_plan(
    request: UserGoalRequest,
    client: AIPlannerClient = Depends(get_planner_client)
):
    """
    Accepts raw user scheduling text, forwards it to the ai_planner microservice,
    and returns a dynamically calculated, validated schedule.
    """
    # Call our internal client service
    schedule_data = await client.generate_schedule(request)
    return schedule_data
