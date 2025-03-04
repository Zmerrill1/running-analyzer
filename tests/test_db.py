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


"""
The issue with this test was that the session wasn't persisting when creating the second run.
To fix I explicitly set the session and added the runs.
Did a helper function to create the second run with new values, so there wouldn't be duplicates.
The test_list_runs that isn't commented out is much cleaner and uses the helper function.
Will delete this note and old test_list_runs later.
"""
# @freeze_time("2025-01-01")
# def test_list_runs(repo, add_run):
#     session = repo.session()

#     second_run = Run(
#         date=datetime(2025, 1, 2, 0, 1),
#         unit=DistanceUnit.MILES,
#         distance=5,
#         duration=60,
#         run_type=RunType.RECOVERY,
#         notes="Second run"
#     )

#     print("Before adding any runs:", repo.list_runs())

#     session.add(add_run)
#     session.commit()
#     session.refresh(add_run)
#     print("First run added:", add_run.model_dump())

#     session.add(second_run)
#     session.commit()
#     session.refresh(second_run)
#     print("Second run added:", second_run.model_dump())

#     runs = repo.list_runs()
#     print("Runs in DB:", [run.model_dump() for run in runs])

#     assert len(runs) == 2


@freeze_time("2025-01-01")
def test_list_runs2(repo, add_run):
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
