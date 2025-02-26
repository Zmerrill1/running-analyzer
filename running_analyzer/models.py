from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional


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
    __tablename__ = "run"

    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    distance: float = Field(..., description="Distance Covered", ge=0)
    unit: DistanceUnit = Field(..., description="Unit of measurement (mi/km)")
    duration: float = Field(..., description="Duration in minutes", ge=0)
    heart_rate: float | None = Field(default=None, description="Average Heart Rate")
    elevation_gain: float | None = Field(default=None, description="Elevation gain")
    pace: float | None = Field(default=None, description="Pace in min per mile/km")
    run_type: RunType = Field(..., description="Type of run")
    location: str | None = Field(default=None, description="Run Location")
    notes: str | None = Field(default=None, description="Running Notes")

    @property
    def calculated_pace(self) -> float:
        return self.duration / self.distance if self.distance else 0

    @classmethod
    def summarize_runs(cls, runs: list["Run"]) -> dict:
        total_runs = len(runs)
        total_distance = sum(run.distance for run in runs)
        total_duration = sum(run.duration for run in runs)
        avg_distance = total_distance / total_runs
        avg_duration = total_duration / total_runs
        avg_pace = total_duration / total_distance if total_distance > 0 else 0

        return {
            "total_runs": total_runs,
            "total_distance": total_distance,
            "total_duration": total_duration,
            "avg_distance": avg_distance,
            "avg_duration": avg_duration,
            "avg_pace": avg_pace,
        }

    @classmethod
    def best_run(cls, runs: list["Run"]) -> Optional["Run"]:
        valid_runs = [run for run in runs if run.distance > 0]
        if not valid_runs:
            return None
        return min(valid_runs, key=lambda run: run.calculated_pace)

    @classmethod
    def average_pace(cls, runs: list["Run"]) -> float:
        total_distance = sum(run.distance for run in runs)
        total_duration = sum(run.duration for run in runs)
        return total_duration / total_distance if total_distance else 0

    @property
    def unit_display(self) -> str:
        return self.unit.value if hasattr(self.unit, "value") else str(self.unit)

    @property
    def run_date(self) -> str:
        return (
            self.date.strftime("%Y-%m-%d")
            if isinstance(self.date, datetime)
            else self.date
        )
