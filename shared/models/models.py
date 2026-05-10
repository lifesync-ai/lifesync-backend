# shared/models/models.py
from sqlalchemy import Column, String, Integer, Boolean, Text
from shared.models.database import Base

class ActivitySpec(Base):
    """
    ORM Model representing the scheduling configuration for specific user activities.
    This replaces our previous hardcoded dictionary mock (ACTIVITY_REGISTRY).
    """
    __tablename__ = "activity_specs"

    # The unique name of the activity (e.g., "run", "breakfast")
    activity_name = Column(String(50), primary_key=True, nullable=False)
    
    # Time durations represented in minutes
    prep_duration = Column(Integer, default=0, nullable=False)      # Time needed before (e.g., cooking, getting dressed)
    activity_duration = Column(Integer, default=0, nullable=False)  # Duration of the main task itself
    post_duration = Column(Integer, default=0, nullable=False)      # Time needed after (e.g., showering, cleaning up)
    
    # Device configuration
    alarm_on_prep = Column(Boolean, default=False, nullable=False)  # Whether a device alarm is required at prep start
    
    # Dynamically formatted descriptions
    prep_description = Column(Text, nullable=True)                  # Instructional text for preparation
    post_description = Column(Text, nullable=True)                  # Instructional text for wrapping up