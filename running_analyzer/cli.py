import typer
from running_analyzer.db import get_engine, get_session, RunRepository
from running_analyzer.models import Run
from running_analyzer.utils import load_runs_from_csv, display_run_details

app = typer.Typer()
engine = get_engine()


def fetch_runs(repo: RunRepository) -> list[Run]:
    runs = repo.list_runs()
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
            typer.echo("Available commands:")
            for cmd_name in app.registered_commands:
                typer.echo(f" - {cmd_name.name} : {cmd_name.help or 'No Description'}")
        else:
            try:
                args = command.strip().split()
                if args:
                    app(args, standalone_mode=False)
            except Exception as e:
                typer.echo(f"Error: {e}")


@app.command("run", help="Start the Running Data Analyzer")
def run():
    command_loop()


@app.command("hello", help="Say hello!")
def hello():
    typer.echo("👋 Hello from Running Data Analyzer!")


@app.command("list-runs", help="List all runs")
def list_runs():
    with get_session() as session:
        repo = RunRepository(session)
        runs = fetch_runs(repo)
        for run in runs:
            typer.echo(
                f"{run.id}. {run.run_date} - {run.distance} {run.unit_display} in {run.duration} mins"
            )


# Todo: Fix value for Runtype when updating. Comes up with an invalid input value for enum error.
@app.command("update-run", help="Update a specific run's data. Add id # after command.")
def update_run(run_id: int):
    with get_session() as session:
        repo = RunRepository(session)
        run = repo.get_run_by_id(run_id)
        if not run:
            typer.echo(f"Run with id {run_id} not found.")
            raise typer.Exit()

        display_run_details(run)

        updated_data = {
            "date": typer.prompt("New date", default=str(run.date)),
            "distance": float(typer.prompt("New distance", default=str(run.distance))),
            "duration": float(
                typer.prompt("New duration (mins)", default=str(run.duration))
            ),
            "heart_rate": float(
                typer.prompt("New heart rate", default=str(run.heart_rate))
            ),
            "elevation_gain": float(
                typer.prompt("New elevation gain", default=str(run.elevation_gain))
            ),
            "pace": float(typer.prompt("New pace", default=str(run.pace))),
            "run_type": typer.prompt("New run type", default=run.run_type),
            "location": typer.prompt("New location", default=run.location),
            "notes": typer.prompt("New notes", default=run.notes),
        }

        repo.update_run(run, **updated_data)
        typer.echo(f"Run {run_id} updated successfully!")


@app.command("import-data", help="Import running data from CSV")
def import_data(csv_file: str):
    runs_to_add = load_runs_from_csv(csv_file)

    with get_session() as session:
        session.add_all(runs_to_add)
        session.commit()
        typer.echo(f"✅ Imported {len(runs_to_add)} runs into the database.")


# Todo: Add units for distance and pace
@app.command("summary", help="Summary of all runs")
def summary():
    with get_session() as session:
        repo = RunRepository(session)
        runs = repo.list_runs()

    if not runs:
        typer.echo("no runs found in the database")
        raise typer.Exit()

    summary = Run.summarize_runs(runs)

    typer.echo("🏃‍♂️ Run Summary:")
    typer.echo(f"  Total Runs: {summary['total_runs']}")
    typer.echo(f"  Total Distance: {summary['total_distance']}")
    typer.echo(f"  Total Duration: {summary['total_duration']} mins")
    typer.echo(f"  Average Distance: {summary['avg_distance']:.2f}")
    typer.echo(f"  Average Duration: {summary['avg_duration']:.2f} mins")
    typer.echo(f"  Average Pace: {summary['avg_pace']:.2f} min per unit")


@app.command("best-run", help="Best run details")
def best_run():
    with get_session() as session:
        repo = RunRepository(session)
        runs = repo.list_runs()

    best = Run.best_run(runs)
    if not best:
        typer.echo("No valid runs found with distance greater than zero")
        raise typer.Exit()

    unit_str = best.unit.value if best.unit and hasattr(best.unit, "value") else "unit"

    typer.echo("Best Run:")
    typer.echo(f"Date: {best.run_date}, Distance: {best.distance} {unit_str}")
    typer.echo(
        f"Duration: {best.duration} mins, Pace: {best.calculated_pace:.2f} min per {unit_str}"
    )


@app.command("avg-pace", help="Average pace overall")
def avg_pace():
    with get_session() as session:
        repo = RunRepository(session)
        runs = repo.list_runs()

    if not runs:
        typer.echo("No runs found in the database")
        raise typer.Exit()

    pace = Run.average_pace(runs)

    sample_run = runs[0]
    typer.echo(f"Average Pace: {pace:.2f} min per {sample_run.unit_display}")


if __name__ == "__main__":
    app()
