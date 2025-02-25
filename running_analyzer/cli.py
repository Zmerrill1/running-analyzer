import typer
from sqlmodel import select
from running_analyzer.db import get_engine, get_session
from running_analyzer.models import Run
from running_analyzer.utils import load_runs_from_csv

app = typer.Typer()
engine = get_engine()


@app.command()
def hello():
    typer.echo("👋 Hello from Running Data Analyzer!")


@app.command()
def list_runs():
    with get_session() as session:
        runs = session.exec(select(Run)).all()
        if not runs:
            typer.echo("No runs found in database")
            return
        for run in runs:
            typer.echo(f"{run.date} - {run.distance} {run.unit} in {run.duration} mins")


@app.command()
def import_data(csv_file: str):
    runs_to_add = load_runs_from_csv(csv_file)

    with get_session() as session:
        session.add_all(runs_to_add)
        session.commit()
        typer.echo(f"✅ Imported {len(runs_to_add)} runs into the database.")


if __name__ == "__main__":
    print("Running CLI...")
    app()
