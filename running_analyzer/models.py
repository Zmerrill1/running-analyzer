from sqlmodel import SQLModel, Field
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
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    distance: float = Field(..., description="Distance Covered", ge=0)
    unit: DistanceUnit = Field(..., description="Unit of measurement (mi/km)")
    duration: float = Field(..., description="Duration in minutes", ge=0)
    heart_rate: int | None = Field(default=None, description="Average Heart Rate")
    elevation_gain: float | None = Field(default=None, description="Elevation gain")
    pace: float | None = Field(default=None, description="Pace in min per mile/km")
    run_type: RunType = Field(..., description="Type of run")
    location: str | None = Field(default=None, description="Run Location")
    notes: str | None = Field(default=None, description="Running Notes")
