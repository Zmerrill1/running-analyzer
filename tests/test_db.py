from datetime import datetime
import pytest
from freezegun import freeze_time

from running_analyzer.db import RunRepository
from running_analyzer.models import Run, DistanceUnit, RunType


@pytest.fixture(scope="function")
def repo():
    return RunRepository("sqlite:///:memory:", debug=True)

@pytest.fixture(scope="function")
@freeze_time("2025-01-01")
def add_run():
    return Run(
        date=datetime.now(),
        unit=DistanceUnit.MILES,
        distance=10,
        duration=60,
        run_type=RunType.LONG,
        notes="Good run",
    )

@freeze_time("2025-01-01")
def test_add_run(repo, add_run):
    run_obj = repo.add_run(add_run).model_dump()
    assert run_obj == {
        "date": datetime(2025, 1, 1, 0, 0),
        "distance": 10.0,
        "duration": 60.0,
        "elevation_gain": None,
        "run_type": RunType.LONG,
        "notes": "Good run",
        "unit": DistanceUnit.MILES,
        "id": 1,
        "heart_rate": None,
        "pace": None,
        "location": None,
    }


@freeze_time("2025-01-01")
def test_list_runs(repo, add_run):
    second_run = add_run.copy()
    repo.add_run(add_run)
    repo.add_run(second_run)
    runs = repo.list_runs()
    assert len(runs) == 2  # gives 1 while adding 2?
    runs_serialized = [
        run.model_dump() for run in runs
    ]
    # TODO: use a breakpoint to see the output and copy paste in assert here
