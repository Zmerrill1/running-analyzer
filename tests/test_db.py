from datetime import datetime
import pytest
from freezegun import freeze_time

from running_analyzer.db import RunRepository
from running_analyzer.models import Run, DistanceUnit, RunType


@pytest.fixture(scope="function")
def repo():
    return RunRepository("sqlite:///:memory:", debug=True, create_db=True)


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


def create_run(**kwargs) -> Run:
    """Helper function to create a new Run instance with overridden values."""
    defaults = {
        "date": datetime(2025, 1, 2, 0, 1),
        "unit": DistanceUnit.MILES,
        "distance": 5,
        "duration": 60,
        "run_type": RunType.RECOVERY,
        "notes": "Second run",
    }
    defaults.update(kwargs)
    return Run(**defaults)


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
    """Test listing multiple runs after inserting them."""
    repo.add_run(add_run)
    second_run = create_run()  # Create a new, unique run
    repo.add_run(second_run)

    runs = repo.list_runs()
    assert len(runs) == 2

    expected_runs = [
        {
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
        },
        {
            "date": datetime(2025, 1, 2, 0, 1),
            "distance": 5.0,
            "duration": 60.0,
            "elevation_gain": None,
            "run_type": RunType.RECOVERY,
            "notes": "Second run",
            "unit": DistanceUnit.MILES,
            "id": 2,  # Ensure second run gets an ID
            "heart_rate": None,
            "pace": None,
            "location": None,
        },
    ]

    assert [run.model_dump() for run in runs] == expected_runs


def test_get_run_by_id(repo, add_run):
    run = repo.add_run(add_run)
    retrieved_run = repo.get_run_by_id(run.id)

    assert retrieved_run is not None
    assert retrieved_run.id == run.id
    assert retrieved_run.distance == run.distance


def test_delete_run(repo, add_run):
    run = repo.add_run(add_run)
    assert repo.get_run_by_id(run.id) is not None

    deleted = repo.delete_run(run.id)
    assert deleted is True
    assert repo.get_run_by_id(run.id) is None


def test_update_run(repo, add_run):
    run = repo.add_run(add_run)
    repo.update_run(run.id, distance=20, location="home", run_type=RunType.RACE)
    updated_run = repo.get_run_by_id(run.id)

    assert updated_run.distance == 20
    assert updated_run.location == "home"
    assert updated_run.run_type == "Race"


def test_list_runs_by_type(repo, add_run):
    repo.add_run(add_run)
    another_run = create_run(run_type=RunType.RECOVERY)
    repo.add_run(another_run)

    long_runs = repo.list_runs_by_type(RunType.LONG)
    assert len(long_runs) == 1
    assert long_runs[0].run_type == RunType.LONG


def test_list_runs_by_date_range(repo, add_run):
    repo.add_run(add_run)
    another_run = create_run(date=datetime(2025, 1, 17))
    repo.add_run(another_run)

    runs = repo.list_runs_by_date_range(datetime(2025, 1, 10), datetime(2025, 1, 18))
    assert len(runs) == 1
    assert runs[0].date == datetime(2025, 1, 17)


def test_get_best_run(repo, add_run):
    repo.add_run(add_run)
    slow_run = create_run(distance=10, duration=75)
    repo.add_run(slow_run)

    best_run = repo.get_best_run()
    assert best_run is not None
    assert best_run.duration == 60
