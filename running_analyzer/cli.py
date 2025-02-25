import typer
from sqlmodel import select
from running_analyzer.db import get_engine, get_session
from running_analyzer.models import Run
from running_analyzer.utils import load_runs_from_csv

app = typer.Typer()
engine = get_engine()


def fetch_runs() -> list[Run]:
    with get_session() as session:
        runs = session.exec(select(Run)).all()
    if not runs:
        typer.echo("No runs found in database")
        raise typer.Exit()
    return runs


# persistant runninng of app. Need to work more, but doing it REPL style and prompts users for commands.
def command_loop():
    typer.echo(
        "Welcome to Running Data Analyzer! Type 'help' for commands or 'exit' to quit."
    )

    while True:
        command = typer.prompt(">>>")

        if command in ["exit", "quit"]:
            typer.echo("Goodbye!")
            break
        elif command == "help":
            typer.echo(
                "Available commands:\n - hello\n - list-runs\n - update-run\n - import-data\n - summary\n - best-run\n - avg-pace"
            )


@app.command()
def run():
    command_loop()


@app.command()
def hello():
    typer.echo("👋 Hello from Running Data Analyzer!")


@app.command("list-runs")
def list_runs():
    runs = fetch_runs()
    for run in runs:
        typer.echo(f"{run.date} - {run.distance} {run.unit} in {run.duration} mins")


@app.command("update-run")
def update_run(run_id: int):
    with get_session() as session:
        run = session.get(Run, run_id)
        if not run:
            typer.echo(f"Run with id {run_id} not found.")
            raise typer.Exit()

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

        new_date = typer.prompt("New date", default=str(run.date))
        new_distance = typer.prompt("New distance", default=str(run.distance))
        new_duration = typer.prompt("New duration (mins)", default=str(run.duration))
        new_heart_rate = typer.prompt("New heart rate", default=str(run.heart_rate))
        new_elevation_gain = typer.prompt(
            "New elevation gain", default=str(run.elevation_gain)
        )
        new_pace = typer.prompt("New pace", default=str(run.pace))
        new_run_type = typer.prompt("New run type", default=run.run_type)
        new_location = typer.prompt("New location", default=run.location)
        new_notes = typer.prompt("New notes", default=run.notes)

        run.date = new_date
        run.distance = float(new_distance)
        run.duration = float(new_duration)
        run.heart_rate = float(new_heart_rate)
        run.elevation_gain = float(new_elevation_gain)
        run.pace = float(new_pace)
        run.run_type = new_run_type
        run.location = new_location
        run.notes = new_notes

        session.add(run)
        session.commit()
        typer.echo(f"Run {run_id} updated successfully!")


@app.command("import-data")
def import_data(csv_file: str):
    runs_to_add = load_runs_from_csv(csv_file)

    with get_session() as session:
        session.add_all(runs_to_add)
        session.commit()
        typer.echo(f"✅ Imported {len(runs_to_add)} runs into the database.")


@app.command("summary")
def summary():
    runs = fetch_runs()

    total_runs = len(runs)
    total_distance = sum(run.distance for run in runs)
    total_duration = sum(run.duration for run in runs)
    avg_distance = total_distance / total_runs
    avg_duration = total_duration / total_runs
    avg_pace = total_duration / total_distance if total_distance > 0 else 0

    typer.echo("🏃‍♂️ Run Summary:")
    typer.echo(f"  Total Runs: {total_runs}")
    typer.echo(f"  Total Distance: {total_distance}")
    typer.echo(f"  Total Duration: {total_duration} mins")
    typer.echo(f"  Average Distance: {avg_distance:.2f}")
    typer.echo(f"  Average Duration: {avg_duration:.2f} mins")
    typer.echo(f"  Average Pace: {avg_pace:.2f} min per unit")


@app.command("best-run")
def best_run():
    runs = fetch_runs()
    valid_runs = [run for run in runs if run.distance > 0]
    if not valid_runs:
        typer.echo("No valid runs found with distance greater than zero")
        raise typer.Exit()
    best = min(valid_runs, key=lambda run: run.duration / run.distance)
    best_pace = best.duration / best.distance

    unit_str = best.unit.value if hasattr(best.unit, "value") else str(best.unit)

    typer.echo("Best Run:")
    typer.echo(f"Date: {best.date}, Distance: {best.distance} {unit_str}")
    typer.echo(
        f"Duration: {best.duration} mins, Pace: {best_pace:.2f} min per {unit_str}"
    )


@app.command("avg-pace")
def avg_pace():
    runs = fetch_runs()
    total_distance = sum(run.distance for run in runs)
    total_duration = sum(run.duration for run in runs)

    sample_run = runs[0]
    unit_str = (
        sample_run.unit.value
        if hasattr(sample_run.unit.value, "value")
        else str(sample_run.unit.value)
    )

    if total_distance == 0:
        typer.echo("Total distance is 0, go on some runs!")
        raise typer.Exit()
    pace = total_duration / total_distance
    typer.echo(f"Average Pace: {pace:.2f} min per {unit_str}")


if __name__ == "__main__":
    app()
