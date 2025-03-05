import csv
from running_analyzer.models import Run
from datetime import datetime
from fitparse import FitFile
import logging
import typer

logging.basicConfig(level=logging.WARNING)


def load_runs_from_csv(csv_file: str):
    runs_to_add = []
    invalid_rows = []
    with open(csv_file, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                run = Run(
                    date=row["date"],
                    distance=float(row["distance"] or 0),
                    unit=row.get("unit", "km"),
                    duration=float(row["duration"] or 0),
                    heart_rate=float(row["heart_rate"] or 0),
                    elevation_gain=float(row["elevation_gain"] or 0),
                    pace=float(row["pace"] or 0),
                    run_type=row["run_type"],
                    location=row.get("location", ""),
                    notes=row.get("notes", ""),
                )
                runs_to_add.append(run)
            except (KeyError, ValueError) as e:
                logging.warning(f"Skipping row {row} due to error: {e}")
                invalid_rows.append(row)
    if invalid_rows:
        print("The following rows were skipped due to invalid data:")
        for invalid in invalid_rows:
            print(invalid)

    return runs_to_add


def display_run_details(run: Run):
    typer.echo("Current run details:")
    typer.echo(f"  Date: {run.date}")
    typer.echo(
        f"  Distance: {run.distance} {run.unit.value if hasattr(run.unit, 'value') else run.unit}"
    )
    typer.echo(f"  Duration: {run.duration} mins")
    typer.echo(f"  Heart Rate: {run.heart_rate}")
    typer.echo(f"  Elevation Gain: {run.elevation_gain}")
    typer.echo(f"  Pace: {run.pace}")
    typer.echo(f"  Run Type: {run.run_type.value}")
    typer.echo(f"  Location: {run.location}")
    typer.echo(f"  Notes: {run.notes}")


def parse_fit_file(file_path):
    """Parses a .fit file and extracts key running data."""
    fitfile = FitFile(file_path)

    records = []

    for record in fitfile.get_messages("record"):
        data = {}
        for data_field in record:
            value = data_field.value

            # Convert datetime objects to strings
            if isinstance(value, datetime):
                value = value.isoformat()

            data[data_field.name] = value

        records.append(data)

    return records


def summarize_fit_data(file_path):
    records = parse_fit_file(file_path)

    if records is None:
        raise ValueError("No data found in the .fit file")

    summary = {
        "total_records": len(records),
        "first_timestamp": records[0].get("timestamp", "N/A"),
        "last_timestamp": records[-1].get("timestamp", "N/A"),
        "total_distance": sum(r.get("distance", 0) for r in records if "distance" in r),
        "average_speed": sum(r.get("speed", 0) for r in records if "speed" in r)
        / len(records)
        if len(records)
        else 0,
    }

    return summary


def list_fit_data(file_path):
    records = parse_fit_file(file_path)

    if not records:
        return "No data found in the .fit file"

    return records
