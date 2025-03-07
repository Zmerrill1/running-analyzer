from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
from collections import defaultdict, Counter


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
        try:
            return self.duration / self.distance
        except ZeroDivisionError:
            return 0

    @classmethod
    def summarize_runs(cls, runs: list[Run]) -> dict:
        total_runs = len(runs)
        total_distance = 0
        total_duration = 0

        for run in runs:
            total_distance += run.distance
            total_duration += run.duration

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
    def best_run(cls, runs: list[Run]) -> Optional[Run]:
        valid_runs = [run for run in runs if run.distance > 0]
        if not valid_runs:
            return None
        return min(valid_runs, key=lambda run: run.calculated_pace)

    @classmethod
    def average_pace(cls, runs: list[Run]) -> float:
        total_distance = sum(run.distance for run in runs)
        total_duration = sum(run.duration for run in runs)
        return total_duration / total_distance if total_distance else 0

    @property
    def unit_display(self) -> str:
        return self.unit.value if hasattr(self.unit, "value") else str(self.unit)

    @property
    def run_date(self) -> str:
        try:
            return self.date.strftime("%Y-%m-%d")
        except AttributeError:
            return str(self.date)

    @classmethod
    def slowest_run(cls, runs: list["Run"]) -> Optional["Run"]:
        valid_runs = [run for run in runs if run.distance > 0]
        return (
            max(valid_runs, key=lambda run: run.calculated_pace) if valid_runs else None
        )

    @classmethod
    def longest_run(cls, runs: list["Run"]) -> Optional["Run"]:
        return max(runs, key=lambda run: run.distance) if runs else None

    @classmethod
    def shortest_run(cls, runs: list["Run"]) -> Optional["Run"]:
        return min(runs, key=lambda run: run.distance) if runs else None

    @classmethod
    def weekly_summary(cls, runs: list["Run"]) -> dict:
        weeks = defaultdict(lambda: {"distance": 0, "duration": 0, "count": 0})

        for run in runs:
            week_num = run.date.strftime("%Y-%W")
            weeks[week_num]["distance"] += run.distance
            weeks[week_num]["duration"] += run.duration
            weeks[week_num]["count"] += 1

        return {
            week: {
                "total_distance": data["distance"],
                "total_duration": data["duration"],
                "avg_pace": (data["duration"] / data["distance"])
                if data["distance"] > 0
                else 0.0,
            }
            for week, data in weeks.items()
        }

    @classmethod
    def monthly_summary(cls, runs: list["Run"]) -> dict:
        months = defaultdict(lambda: {"distance": 0, "duration": 0, "count": 0})

        for run in runs:
            month_num = run.date.strftime("%Y-%m")
            months[month_num]["distance"] += run.distance
            months[month_num]["duration"] += run.duration
            months[month_num]["count"] += 1

        return {
            month: {
                "total_distance": data["distance"],
                "total_duration": data["duration"],
                "avg_pace": (data["duration"] / data["distance"])
                if data["distance"] > 0
                else 0.0,
            }
            for month, data in months.items()
        }

    @classmethod
    def run_type_distribution(cls, runs: list["Run"]) -> dict:
        return dict(Counter(run.run_type for run in runs))

    @classmethod
    def create_run(
        cls,
        date: datetime,
        distance: float,
        unit: DistanceUnit,
        duration: float,
        heart_rate: Optional[float] = None,
        elevation_gain: Optional[float] = None,
        run_type: RunType = RunType.EASY,
        location: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> "Run":
        return cls(
            date=date,
            distance=distance,
            unit=unit,
            duration=duration,
            heart_rate=heart_rate,
            elevation_gain=elevation_gain,
            run_type=run_type,
            location=location,
            notes=notes,
        )
