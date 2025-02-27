import csv
from running_analyzer.models import Run
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
                    distance=row["distance"],
                    unit=row.get("unit", "km"),
                    duration=row["duration"],
                    heart_rate=row.get("heart_rate", 0),
                    elevation_gain=row.get("elevation_gain", 0),
                    pace=row.get("pace", 0),
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
    typer.echo(f"  Run Type: {run.run_type}")
    typer.echo(f"  Location: {run.location}")
    typer.echo(f"  Notes: {run.notes}")
