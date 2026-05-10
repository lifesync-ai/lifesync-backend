from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

# 1. Incoming payload from the user (Mobile Client -> API Gateway)
class UserGoalRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier of the user")
    raw_text: str = Field(
        ..., 
        description="Raw conversational text, e.g., 'I want to run tomorrow at 9 AM and eat breakfast at 11 AM'"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# 2. An individual task within the calculated backward schedule
class ScheduledTask(BaseModel):
    task_name: str = Field(..., description="Name of the activity (e.g., Wake Up, Prep Breakfast)")
    start_time: datetime = Field(..., description="Calculated start time")
    end_time: datetime = Field(..., description="Calculated end time")
    duration_minutes: int = Field(..., description="Duration of the task in minutes")
    is_alarm_required: bool = Field(default=False, description="Flag indicating if a physical device alarm should be set")
    description: Optional[str] = Field(None, description="Additional context, such as recipes or dynamic notes")

# 3. Final calculated schedule payload returned to the client
class ProposedTimelineResponse(BaseModel):
    request_id: str = Field(..., description="UUID of the planning request for tracking")
    status: str = Field("calculated", description="Status of the generation process")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timeline: List[ScheduledTask] = Field(..., description="Chronologically sorted execution steps")
