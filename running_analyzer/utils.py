import csv
from running_analyzer.models import Run
import logging

logging.basicConfig(level=logging.WARNING)


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Cannot convert {value!r} to float.")


def load_runs_from_csv(csv_file: str):
    runs_to_add = []
    invalid_rows = []
    with open(csv_file, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                run = Run(
                    date=row["date"],
                    distance=safe_float(row["distance"]),
                    unit=row.get("unit", "km"),
                    duration=safe_float(row["duration"]),
                    heart_rate=safe_float(row.get("heart_rate", 0)),
                    elevation_gain=safe_float(row.get("elevation_gain", 0)),
                    pace=safe_float(row.get("pace", 0)),
                    run_type=row.get("run_type", ""),
                    location=row.get("location", ""),
                    notes=row.get("notes", ""),
                )
                runs_to_add.append(run)
            except ValueError as e:
                logging.warning(f"Skipping row {row} due to error: {e}")
                invalid_rows.append(row)
    if invalid_rows:
        print("The following rows were skipped due to invalid data:")
        for invalid in invalid_rows:
            print(invalid)

    return runs_to_add
