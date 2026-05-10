# api_gateway/src/services/planner_client.py
import os
import httpx
from fastapi import HTTPException, status
from shared.models.schemas import UserGoalRequest, ProposedTimelineResponse
from dotenv import load_dotenv

# Load .env variables from the root folder
load_dotenv()

# Get the internal address of the AI Planner microservice
AI_PLANNER_URL = os.getenv("AI_PLANNER_SERVICE_URL", "http://127.0.0.1:8001")

class AIPlannerClient:
    """
    HTTP Client responsible for communicating with the internal
    ai_planner microservice.
    """
    def __init__(self):
        self.base_url = AI_PLANNER_URL
        self.timeout = 30.0  # LLM parsing can take a few seconds, so we set a generous timeout

    async def generate_schedule(self, payload: UserGoalRequest) -> dict:
        """
        Sends the user's raw text to the ai_planner microservice
        and returns the computed timeline.
        """
        target_url = f"{self.base_url}/api/v1/planner/generate"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Forward the exact JSON payload to our AI Planner
                response = await client.post(target_url, json=payload.model_dump(mode="json"))
                
                # If the planner service returns an error, forward it to the gateway client
                if response.status_code != status.HTTP_200_OK:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"AI Planner service returned an error: {response.text}"
                    )
                
                return response.json()
                
            except httpx.RequestError as exc:
                # Catch connection errors (e.g., if the ai_planner microservice is offline)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"AI Planner microservice is currently unreachable: {str(exc)}"
                )
