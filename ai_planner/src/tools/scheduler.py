# ai_planner/src/tools/scheduler.py
from datetime import datetime, timedelta, time
from typing import List
from shared.models.schemas import ScheduledTask, ProposedTimelineResponse
from ai_planner.src.agents.parser import ExtractedGoals
import uuid

# Mock database of activity specs (Sprint 2 will move this to PostgreSQL)
ACTIVITY_REGISTRY = {
    "run": {
        "prep_duration": 30,       # minutes needed before the run (e.g. wake up, dress)
        "activity_duration": 45,   # duration of the run itself
        "post_duration": 45,       # shower, cool down
        "alarm_on_prep": True,
        "prep_description": "Wake up and prepare for your morning run.",
        "post_description": "Shower and cool down after your run."
    },
    "breakfast": {
        "prep_duration": 30,       # cooking time
        "activity_duration": 30,   # eating time
        "post_duration": 0,
        "alarm_on_prep": True,
        "prep_description": "Start cooking. Prep details: {details}",
        "post_description": "Enjoy your meal!"
    }
}

def calculate_backward_schedule(goals: ExtractedGoals, target_date: datetime = None) -> List[ScheduledTask]:
    if not target_date:
        # Default to tomorrow
        target_date = datetime.now() + timedelta(days=1)
        
    timeline: List[ScheduledTask] = []
    
    for event in goals.events:
        activity_type = event.activity.lower()
        
        # If we don't know the activity, fall back to a generic default structure
        spec = ACTIVITY_REGISTRY.get(activity_type, {
            "prep_duration": 15,
            "activity_duration": 30,
            "post_duration": 0,
            "alarm_on_prep": True,
            "prep_description": "Prepare for your activity.",
            "post_description": "Wrap up your activity."
        })
        
        # Parse HH:MM string from LLM into a datetime object
        hours, minutes = map(int, event.target_time.split(":"))
        target_time = target_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        # 1. Calculate Prep Step (Backward from Start Time)
        prep_start = target_time - timedelta(minutes=spec["prep_duration"])
        prep_desc = spec["prep_description"].format(details=event.details or "")
        
        timeline.append(ScheduledTask(
            task_name=f"Prepare: {event.activity.capitalize()}",
            start_time=prep_start,
            end_time=target_time,
            duration_minutes=spec["prep_duration"],
            is_alarm_required=spec["alarm_on_prep"],
            description=prep_desc
        ))
        
        # 2. Calculate Main Event Step
        event_end = target_time + timedelta(minutes=spec["activity_duration"])
        timeline.append(ScheduledTask(
            task_name=event.activity.capitalize(),
            start_time=target_time,
            end_time=event_end,
            duration_minutes=spec["activity_duration"],
            is_alarm_required=False,
            description=f"Time scheduled for {event.activity}."
        ))
        
        # 3. Calculate Post Event Step (if any duration is specified)
        if spec["post_duration"] > 0:
            post_end = event_end + timedelta(minutes=spec["post_duration"])
            timeline.append(ScheduledTask(
                task_name=f"Post-{event.activity.capitalize()} Wrap-up",
                start_time=event_end,
                end_time=post_end,
                duration_minutes=spec["post_duration"],
                is_alarm_required=False,
                description=spec["post_description"]
            ))
            
    # Sort the timeline chronologically so the user sees their day in order
    timeline.sort(key=lambda task: task.start_time)
    
    return timeline