import typer
import plotext as plt
import numpy as np
from datetime import datetime
from pathlib import Path
from running_analyzer.db import RunRepository
from running_analyzer.models import Run, DistanceUnit, RunType
from running_analyzer.utils import (
    load_runs_from_csv,
    display_run_details,
    summarize_fit_data,
    parse_fit_file,
)
from rich.console import Console
from rich.table import Table
import json


app = typer.Typer()

repo = RunRepository()

console = Console()

FIT_FILE_EXTENSION = ".fit"


# persistant runninng of app. Need to work more, but doing it REPL style and prompts users for commands.
def command_loop():
    is_running = False

    def start():
        nonlocal is_running

        if is_running:
            typer.echo(
                "⚠️  The Running Data Analyzer is already running. Exiting duplicate session."
            )
            return

        is_running = True
        typer.echo(
            "Welcome to Running Data Analyzer! Type 'help' for commands or 'exit' to quit."
        )

        alias_map = {
            "add-run": ["ar"],
            "list-runs": ["lr"],
            "update-run": ["ur"],
            "best-run": ["br"],
            "run-stat best": ["rb"],
            "run-stat longest": ["rl"],
            "run-stat shortest": ["rs"],
            "run-stat slowest": ["rt"],
            "import-data": ["id"],
            "summary": ["sum"],
            "avg-pace": ["ap"],
            "weekly-summary": ["ws"],
            "monthly-summary": ["ms"],
            "plot-runs": ["pr"],
            "plot-pace": ["pp"],
            "plot-weekly-summary": ["pws"],
            "import-fit": ["if"],
            "list-fit": ["lf"],
        }

        all_aliases = {alias for aliases in alias_map.values() for alias in aliases}

        while True:
            command = typer.prompt(">>>")

            if command in ["exit", "quit"]:
                typer.echo("Goodbye!")
                is_running = False
                break
            elif command == "help":
                typer.echo("Available commands:")
                for cmd_name in app.registered_commands:
                    if cmd_name.name in all_aliases:
                        continue

                    aliases = alias_map.get(cmd_name.name, [])
                    alias_text = f" (Alias: {', '.join(aliases)})" if aliases else ""
                    typer.echo(
                        f" - {cmd_name.name}{alias_text} : {cmd_name.help or 'No Description'}"
                    )
            else:
                try:
                    args = command.strip().split()
                    if args:
                        app(args, standalone_mode=False)
                except Exception as e:
                    typer.echo(f"Error: {e}")

    return start


@app.command("run", help="Start the Running Data Analyzer")
def run():
    start_command = command_loop()
    start_command()


@app.command("hello", help="Say hello!")
def hello():
    typer.echo("👋 Hello from Running Data Analyzer!")


@app.command("add-run", help="Manually add a run to the database")
def add_run():
    date_str = typer.prompt(
        "Enter run date (YYYY-MM-DD) or leave blank for today",
        default=datetime.utcnow().strftime("%Y-%m-%d"),
    )
    date = datetime.strptime(date_str, "%Y-%m-%d")

    distance = typer.prompt("Enter distance", type=float)
    unit = typer.prompt(
        f"Enter unit ({', '.join([e.value for e in DistanceUnit])})",
        default=DistanceUnit.KILOMETERS.value,
    )
    duration = typer.prompt("Enter duration in minutes", type=float)

    heart_rate = typer.prompt("Enter heart rate (or leave blank)", default="", type=str)
    heart_rate = float(heart_rate) if heart_rate else None

    elevation_gain = typer.prompt(
        "Enter elevation gain (or leave blank)", default="", type=str
    )
    elevation_gain = float(elevation_gain) if elevation_gain else None

    run_type = typer.prompt(
        f"Enter run type ({', '.join([e.value for e in RunType])})",
        default=RunType.EASY.value,
    )
    location = typer.prompt("Enter location (or leave blank)", default="")
    notes = typer.prompt("Enter notes (or leave blank)", default="")

    run = Run.create_run(
        date=date,
        distance=distance,
        unit=DistanceUnit(unit),
        duration=duration,
        heart_rate=heart_rate,
        elevation_gain=elevation_gain,
        run_type=RunType(run_type),
        location=location if location else None,
        notes=notes if notes else None,
    )

    repo.add_run(run)
    typer.echo(
        f"✅ Successfully added run on {run.run_date} ({run.distance} {run.unit_display})"
    )


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


@app.command("update-run", help="Update a specific run's data. Add id # after command.")
def update_run(run_id: int):
    try:
        run = repo.get_run_by_id(run_id)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

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

    best = Run.best_run(runs)
    longest = Run.longest_run(runs)
    shortest = Run.shortest_run(runs)
    slowest = Run.slowest_run(runs)

    if best:
        typer.echo("\n🏆 Best Run:")
        typer.echo(
            f"  {best.run_date}: {best.distance:.2f} {unit} in {best.duration:.2f} mins (Pace: {best.calculated_pace:.2f})"
        )

    if longest:
        typer.echo("\n📏 Longest Run:")
        typer.echo(f"  {longest.run_date}: {longest.distance:.2f} {unit}")

    if shortest:
        typer.echo("\n📉 Shortest Run:")
        typer.echo(f"  {shortest.run_date}: {shortest.distance:.2f} {unit}")

    if slowest:
        typer.echo("\n🐢 Slowest Run:")
        typer.echo(
            f"  {slowest.run_date}: Pace of {slowest.calculated_pace:.2f} min/{unit}"
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


@app.command("weekly-summary", help="Show weekly running summary")
def weekly_summary():
    runs = repo.list_runs()
    if not runs:
        typer.echo("No runs found in the database")
        raise typer.Exit()

    weekly_data = Run.weekly_summary(runs)
    unit = runs[0].unit_display if runs else "unit"

    sorted_weeks = sorted(
        weekly_data.items(), key=lambda x: tuple(map(int, x[0].split("-")))
    )

    table = Table(title="📅 Weekly Running Summary")
    table.add_column("Week", justify="center", style="cyan")
    table.add_column("Total Distance", justify="right", style="green")
    table.add_column("Total Duration", justify="right", style="yellow")
    table.add_column("Average Pace", justify="right", style="magenta")

    for week, data in sorted_weeks:
        table.add_row(
            week,
            f"{data['total_distance']:.2f} {unit}",
            f"{data['total_duration']:.2f} mins",
            f"{data['avg_pace']:.2f} min/{unit}",
        )

    console.print(table)


@app.command("monthly-summary", help="Show weekly running summary")
def monthly_summary():
    runs = repo.list_runs()
    if not runs:
        typer.echo("No runs found in the database")
        raise typer.Exit()

    monthly_data = Run.monthly_summary(runs)
    unit = runs[0].unit_display if runs else "unit"

    sorted_months = sorted(
        monthly_data.items(), key=lambda x: tuple(map(int, x[0].split("-")))
    )

    table = Table(title="📅 Monthly Running Summary")
    table.add_column("Month", justify="center", style="cyan")
    table.add_column("Total Distance", justify="right", style="green")
    table.add_column("Total Duration", justify="right", style="yellow")
    table.add_column("Average Pace", justify="right", style="magenta")

    for month, data in sorted_months:
        table.add_row(
            month,
            f"{data['total_distance']:.2f} {unit}",
            f"{data['total_duration']:.2f} mins",
            f"{data['avg_pace']:.2f} min/{unit}",
        )

    console.print(table)


@app.command(
    "run-stat",
    help="Show details of a specific run stat (longest (rl), shortest (rs), slowest (rt), best (rb))",
)
def run_stat(stat: str):
    runs = repo.list_runs()
    if not runs:
        typer.echo("No runs found in database")
        raise typer.Exit()

    stat_map = {
        "longest": (Run.longest_run, "📏 Longest Run"),
        "shortest": (Run.shortest_run, "📉 Shortest Run"),
        "slowest": (Run.slowest_run, "🐢 Slowest Run"),
        "best": (Run.best_run, "🏆 Best Run"),
    }

    if stat not in stat_map:
        typer.echo("Invalid stat type. Choose from: longest, shortest, slowest, best")
        raise typer.Exit()

    run_func, emoji_title = stat_map[stat]
    selected_run = run_func(runs)
    if not selected_run:
        typer.echo(f"No valid {stat} run found.")
        raise typer.Exit()

    unit_str = selected_run.unit.value
    typer.echo(f"{emoji_title}:")
    typer.echo(f"Date: {selected_run.run_date}")
    typer.echo(f"Distance: {selected_run.distance:.2f} {unit_str}")
    typer.echo(f"Duration: {selected_run.duration:.2f} mins")
    typer.echo(f"Pace: {selected_run.calculated_pace:.2f} min/{unit_str}")


def validate_fit_file(fit_file: str) -> Path:
    path = Path(fit_file)

    if not path.exists():
        typer.echo("Error: File not found.")
        raise typer.Exit()

    if path.suffix.lower() != FIT_FILE_EXTENSION:
        typer.echo("Error: Only .fit files are supported.")
        raise typer.Exit()

    return path


@app.command(
    "import-fit",
    help="Import running data from a .fit file. Call function and use --help for list of unit/run_type",
)
def import_fit(
    fit_file: str,
    unit: DistanceUnit = typer.Option(
        "km",
        "--unit",
        "-u",
        help=f"Distance unit. Options: {', '.join([e.value for e in DistanceUnit])}",
    ),
    run_type: RunType = typer.Option(
        "Easy",
        "--run-type",
        "-r",
        help=f"Type of run. Options: {', '.join([e.value for e in RunType])}",
    ),
):
    path = validate_fit_file(fit_file)
    records = parse_fit_file(str(path))

    if not records:
        typer.echo("Error: No data found in the .fit file")
        raise typer.Exit(1)

    summary = summarize_fit_data(records)

    distance_m = summary["total_distance"]
    distance = distance_m / 1609.34 if unit == "mi" else distance_m / 1000

    run = Run(
        date=datetime.fromisoformat(summary["last_timestamp"]),
        distance=round(distance, 2),
        unit=DistanceUnit(unit),
        duration=summary["total_duration"],
        run_type=RunType(run_type),
    )

    repo = RunRepository()
    repo.add_run(run)

    typer.echo("\n Run data successfully imported into the database!")


@app.command("list-fit", help="List all raw data from a .fit file")
def list_fit(fit_file: str):
    path = validate_fit_file(fit_file)
    records = parse_fit_file(str(path))

    if not records:
        typer.echo("No data found in the FIT file")
    else:
        console.print_json(json.dumps(records[:10], indent=2))


# Plot/Chart Commands
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


@app.command("plot-weekly-summary", help="Show weekly distance summary as a bar chart")
def plot_weekly_summary():
    runs = repo.list_runs()
    if not runs:
        typer.echo("No runs found in database")
        raise typer.Exit()

    weekly_data = Run.weekly_summary(runs)

    sorted_weeks = sorted(
        weekly_data.keys(), key=lambda r: datetime.strptime(r + "-1", "%Y-%W-%w")
    )
    distances = [weekly_data[week]["total_distance"] for week in sorted_weeks]

    plt.clear_data()
    plt.title("Weekly Running Summary")
    plt.bar(sorted_weeks, distances, color="green")

    tick_step = max(1, len(sorted_weeks) // 6)
    selected_indices = range(0, len(sorted_weeks), tick_step)
    selected_labels = [sorted_weeks[i] for i in selected_indices]

    plt.xticks(selected_indices, selected_labels)
    plt.xlabel("Week")
    plt.ylabel("Total Distance")
    plt.show()


# Register aliases
app.command("ar")(add_run)
app.command("lr")(list_runs)
app.command("ur")(update_run)
app.command("rb")(lambda: run_stat("best"))
app.command("rl")(lambda: run_stat("longest"))
app.command("rs")(lambda: run_stat("shortest"))
app.command("rt")(lambda: run_stat("slowest"))
app.command("id")(import_data)
app.command("sum")(summary)
app.command("ap")(avg_pace)
app.command("ws")(weekly_summary)
app.command("ms")(monthly_summary)
app.command("pr")(plot_runs)
app.command("pp")(plot_pace)
app.command("pws")(plot_weekly_summary)
app.command("if")(import_fit)
app.command("lf")(list_fit)
