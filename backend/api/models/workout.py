from datetime import date
from typing import Optional

from pydantic import BaseModel


class WorkoutBase(BaseModel):
    """Base workout model with shared attributes"""

    name: str
    distance: float  # in meters
    moving_time: float  # in seconds
    total_elevation_gain: float  # in meters
    type: str  # e.g., "Run", "Ride"
    start_date: date
    average_pace: float = 0
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None


class WorkoutCreate(WorkoutBase):
    """Model for creating a new workout"""

    strava_id: str
    user_id: str


class Workout(WorkoutBase):
    """Model for a workout with ID and additional fields"""

    id: int
    strava_id: str
    user_id: str

    model_config = {"from_attributes": True}
