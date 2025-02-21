import typer
import csv
from sqlmodel import Session, select
from running_analyzer.db import get_engine
from running_analyzer.models import Run

app = typer.Typer()
engine = get_engine()


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@app.command()
def hello():
    typer.echo("👋 Hello from Running Data Analyzer!")


@app.command()
def list_runs():
    with Session(engine) as session:
        runs = session.exec(select(Run)).all()
        if not runs:
            typer.echo("No runs found in database")
            return
        for run in runs:
            typer.echo(f"{run.date} - {run.distance} {run.unit} in {run.duration} mins")


@app.command()
def import_data(csv_file: str):
    with open(csv_file, newline="") as file:
        reader = csv.DictReader(file)
        runs_to_add = []

        for row in reader:
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

    with Session(engine) as session:
        session.add_all(runs_to_add)
        session.commit()
        typer.echo(f"✅ Imported {len(runs_to_add)} runs into the database.")


if __name__ == "__main__":
    print("Running CLI...")  # Debugging line
    app()
