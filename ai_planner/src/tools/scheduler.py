# ai_planner/src/tools/scheduler.py
from datetime import datetime, timedelta
from typing import List
from shared.models.schemas import ScheduledTask
from shared.models.models import ActivitySpec
from shared.models.database import engine, SessionLocal
from ai_planner.src.agents.parser import ExtractedGoals

def calculate_backward_schedule(goals: ExtractedGoals, target_date: datetime = None) -> List[ScheduledTask]:
    """
    Takes parsed AI goals and queries PostgreSQL to retrieve activity configurations,
    calculating a precise chronological sequence of execution steps.
    """
    if not target_date:
        # Default to tomorrow if no specific date is provided
        target_date = datetime.now() + timedelta(days=1)
        
    timeline: List[ScheduledTask] = []
    
    # Establish a safe session connection to PostgreSQL
    db = SessionLocal()
    
    try:
        for event in goals.events:
            activity_type = event.activity.lower()
            
            # Query the database for this specific activity configuration
            spec = db.query(ActivitySpec).filter(
                ActivitySpec.activity_name == activity_type
            ).first()
            
            # Fallback configuration if the database doesn't have specs for the parsed activity
            if not spec:
                print(f"⚠️ Activity '{activity_type}' not found in database. Using dynamic defaults.")
                spec = ActivitySpec(
                    activity_name=activity_type,
                    prep_duration=15,
                    activity_duration=30,
                    post_duration=0,
                    alarm_on_prep=True,
                    prep_description="Prepare for your activity.",
                    post_description="Wrap up your activity."
                )
            
            # Parse the HH:MM target time returned by the LLM
            hours, minutes = map(int, event.target_time.split(":"))
            target_time = target_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            # 1. Calculate the Preparation Step (Moving backward in time)
            prep_start = target_time - timedelta(minutes=spec.prep_duration)
            # Safely inject details (like specific recipes) into the description template
            prep_desc = (spec.prep_description or "").format(details=event.details or "")
            
            timeline.append(ScheduledTask(
                task_name=f"Prepare: {event.activity.capitalize()}",
                start_time=prep_start,
                end_time=target_time,
                duration_minutes=spec.prep_duration,
                is_alarm_required=spec.alarm_on_prep,
                description=prep_desc
            ))
            
            # 2. Calculate the Core Activity Step (Moving forward in time)
            event_end = target_time + timedelta(minutes=spec.activity_duration)
            timeline.append(ScheduledTask(
                task_name=event.activity.capitalize(),
                start_time=target_time,
                end_time=event_end,
                duration_minutes=spec.activity_duration,
                is_alarm_required=False,
                description=f"Time scheduled for {event.activity}."
            ))
            
            # 3. Calculate the Post-Activity Wrap-up Step (Moving forward in time, if any)
            if spec.post_duration > 0:
                post_end = event_end + timedelta(minutes=spec.post_duration)
                timeline.append(ScheduledTask(
                    task_name=f"Post-{event.activity.capitalize()} Wrap-up",
                    start_time=event_end,
                    end_time=post_end,
                    duration_minutes=spec.post_duration,
                    is_alarm_required=False,
                    description=spec.post_description
                ))
                
        # Chronologically sort the schedule output
        timeline.sort(key=lambda task: task.start_time)
        
    finally:
        # Guarantee session closure to avoid memory leaks or locked DB connections
        db.close()
        
    return timeline