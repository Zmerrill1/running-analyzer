import typer
import plotext as plt
import numpy as np
from datetime import datetime
from running_analyzer.db import RunRepository
from running_analyzer.models import Run
from running_analyzer.utils import load_runs_from_csv, display_run_details
from rich.console import Console
from rich.table import Table

app = typer.Typer()

repo = RunRepository()

console = Console()


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


@app.command("install-completion", help="Enable shell autocompletion")
def install_completion():
    typer.echo("Run the following command to enable autocompletion:")
    typer.echo("source <(running-analyzer --install-completion)")


@app.command("list-runs", help="List all runs")
def list_runs():
    runs = repo.list_runs()
    if not runs:
        console.print("No runs found. Go out and run!")
        raise typer.Exit()

    table = Table(title="🏃 Your Runs")
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Date", style="magenta")
    table.add_column("Distance", justify="right", style="green")
    table.add_column("Duration", justify="right", style="yellow")

    for run in runs:
        table.add_row(
            str(run.id),
            run.run_date,
            f"{run.distance} {run.unit_display}",
            f"{run.duration} mins",
        )

    console.print(table)
    # for run in runs:
    #     typer.echo(
    #         f"{run.id}. {run.run_date} - {run.distance} {run.unit_display} in {run.duration} mins"
    #     )


@app.command("update-run", help="Update a specific run's data. Add id # after command.")
def update_run(run_id: int):
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
        "run_type": typer.prompt("New run type", default=run.run_type.value),
        "location": typer.prompt("New location", default=run.location),
        "notes": typer.prompt("New notes", default=run.notes),
    }

    repo.update_run(run, **updated_data)
    typer.echo(f"Run {run_id} updated successfully!")


@app.command("import-data", help="Import running data from CSV")
def import_data(csv_file: str):
    runs_to_add = load_runs_from_csv(csv_file)

    with repo.session() as session:
        session.add_all(runs_to_add)
        session.commit()
        typer.echo(f"✅ Imported {len(runs_to_add)} runs into the database.")


@app.command("summary", help="Summary of all runs")
def summary():
    runs = repo.list_runs()

    if not runs:
        typer.echo("no runs found in the database")
        raise typer.Exit()

    summary = Run.summarize_runs(runs)

    unit = runs[0].unit_display if runs else "unit"

    typer.echo("🏃‍♂️ Run Summary:")
    typer.echo(f"  Total Runs: {summary['total_runs']}")
    typer.echo(f"  Total Distance: {summary['total_distance']:.2f} {unit}")
    typer.echo(f"  Total Duration: {summary['total_duration']:.2f} mins")
    typer.echo(f"  Average Distance: {summary['avg_distance']:.2f} {unit}")
    typer.echo(f"  Average Duration: {summary['avg_duration']:.2f} mins")
    typer.echo(f"  Average Pace: {summary['avg_pace']:.2f} min per {unit}")


@app.command("best-run", help="Best run details")
def best_run():
    best = repo.get_best_run()
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
    runs = repo.list_runs()

    if not runs:
        typer.echo("No runs found in the database")
        raise typer.Exit()

    pace = Run.average_pace(runs)

    sample_run = runs[0]
    typer.echo(f"Average Pace: {pace:.2f} min per {sample_run.unit_display}")


@app.command("plot-runs", help="Plot distance trend over time")
def plot_runs():
    runs = repo.list_runs()

    if not runs:
        typer.echo("No runs found in the database")
        raise typer.Exit()

    runs = sorted(runs, key=lambda r: datetime.strptime(r.run_date, "%Y-%m-%d"))

    # convert dates to numbers (for regression) and store formatted date labels for plotext
    dates_numeric = list(range(len(runs)))
    distances = [run.distance for run in runs]
    date_labels = [
        datetime.strptime(run.run_date, "%Y-%m-%d").strftime("%d/%m/%Y") for run in runs
    ]

    if len(dates_numeric) > 1:
        slope, intercept = np.polyfit(dates_numeric, distances, 1)
        trend_line = [slope * x + intercept for x in dates_numeric]

    plt.clear_data()
    plt.title("Running Distance Over Time")
    plt.plot(dates_numeric, distances, marker="dot", color="blue", label="Distance")

    if len(dates_numeric) > 1:
        plt.plot(dates_numeric, trend_line, color="red", label="Trend Line")

    plt.xlabel("Date")
    plt.ylabel("Distance")
    tick_step = max(1, len(dates_numeric) // 6)
    selected_indices = dates_numeric[::tick_step]
    selected_labels = date_labels[::tick_step]

    plt.xticks(selected_indices, selected_labels)
    plt.show()


@app.command("plot-pace", help="Plot pace trends over time")
def plot_pace():
    runs = repo.list_runs()

    if not runs:
        typer.echo("No runs found in the database")
        raise typer.Exit()

    runs = sorted(runs, key=lambda r: datetime.strptime(r.run_date, "%Y-%m-%d"))

    dates_numeric = list(range(len(runs)))
    paces = [run.calculated_pace for run in runs]
    date_labels = [
        datetime.strptime(run.run_date, "%Y-%m-%d").strftime("%d/%m/%Y") for run in runs
    ]

    if len(dates_numeric) > 1:
        slope, intercept = np.polyfit(dates_numeric, paces, 1)
        trend_line = [slope * x + intercept for x in dates_numeric]

    plt.clear_data()
    plt.title("Pace Over Time")
    plt.plot(dates_numeric, paces, marker="dot", color="red", label="Pace")

    if len(dates_numeric) > 1:
        plt.plot(dates_numeric, trend_line, color="blue", label="Trend Line")

    tick_step = max(1, len(dates_numeric) // 6)
    selected_indices = dates_numeric[::tick_step]
    selected_labels = date_labels[::tick_step]

    plt.xticks(selected_indices, selected_labels)
    plt.xlabel("Date")
    plt.ylabel("Pace (min per mile/km)")
    plt.show()


# Command Aliases for most common commands
@app.command("lr", help="Alias for list-runs")
def list_runs_alias():
    list_runs()


@app.command("ur", help="Alias for update-run")
def update_run_alias():
    update_run()


@app.command("br", help="Alias for best-run")
def best_run_alias():
    best_run()
