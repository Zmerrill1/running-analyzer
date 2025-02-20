from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DistanceUnit(str, Enum):
    MILES = "mi"
    KILOMETERS = "km"


class RunType(str, Enum):
    EASY = "Easy"
    LONG = "Long"
    INTERVAL = "Interval"
    TEMPO = "Tempo"
    RACE = "Race"
    RECOVERY = "Recovery"


class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    distance: float = Field(..., description="Distance Covered", ge=0)
    unit: DistanceUnit = Field(..., description="Unit of measurement (mi/km)")
    duration: float = Field(..., description="Duration in minutes", ge=0)
    heart_rate: Optional[int] = Field(default=None, description="Average Heart Rate")
    elevation_gain: Optional[float] = Field(default=None, description="Elevation gain")
    pace: Optional[float] = Field(default=None, description="Pace in min per mile/km")
    run_type: RunType = Field(..., description="Type of run")
    location: Optional[str] = Field(default=None, description="Run Location")
    notes: Optional[str] = Field(default=None, description="Running Notes")
