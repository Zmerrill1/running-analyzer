# 🏃 Running Data Analyzer

A command-line tool for analyzing running data. Manually add data or upload from a CSV or FIT file. Supports basic data insights like distance, pace, and trends over time.

## Features

- 📊 Load and analyze running data from CSV or FIT files.

- 📏 Calculate total distance, average pace, and other key metrics.

- 📈 Identify trends and generate insights from past runs.

- 🖥️ Command-line interface (CLI) for easy use.


## Installation
You can install the Running Data Analyzer from PyPI using `uv`:
```
uv pip install running-data-analyzer
```

---

## 🚀 Usage
Once installed, you can use the CLI command `python -m running_analyzer run` to start the program. Or use `python -m running_analyzer -help` to list avaialable commands.

Using `run` will have the app continually running in the terminal. Use `help` to list out all the commands. 

### Example Output
```
🏃‍♂️ Run Summary:
  Total Runs: 105
  Total Distance: 1601.12 km
  Total Duration: 13437.33 mins
  Average Distance: 15.25 km
  Average Duration: 127.97 mins
  Average Pace: 8.39 min per km

🏆 Best Run:
  2025-03-06: 100.00 km in 35.00 mins (Pace: 0.35)

📏 Longest Run:
  2025-03-06: 100.00 km

📉 Shortest Run:
  2025-02-22: 1.01 km

🐢 Slowest Run:
  2024-12-22: Pace of 11.96 min/km
```

### CSV Format & Getting FIT File from Strava
When importing a CSV file, you should have the following columns:
```
Date,Distance,Unit,Duration (min),Heart Rate,Elevation Gain,Pace,Run Type,Location,Notes
2025-02-15,10.5,km,55,150,200,5:14,Tempo,Park,Good run
2025-02-10,8.0,mi,44,145,180,7:10,Long,Trail,Felt strong
```

Strava Guide: [Exporting Strava Data](https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export)

---

## 🛠️ Tech Stack
- Backend: [Typer](https://typer.tiangolo.com) (CLI framework), [SQLModel](https://sqlmodel.tiangolo.com) (ORM & DB modeling), [PostgreSQL](https://www.postgresql.org) (database), [Alembic](https://pypi.org/project/alembic/) (migrations)
- CLI & Utilities: [Rich](https://rich.readthedocs.io/en/stable/console.html) (console output), [Plotext](https://pypi.org/project/plotext/) (terminal plotting), [NumPy](https://www.google.com/search?client=safari&rls=en&q=numpy&ie=UTF-8&oe=UTF-8&safe=active) (data processing)
- Deployment: [PyPI](https://pypi.org) (package distribution)

## 🔥 Future Features

- 📅 Add support for GPX file imports
- 🏆 More visualizations
- 📝 API integration with Strava/Garmin


## 📄 License

This project is licensed under the MIT License.

## Acknowledgements

- [PyBites PDM Program](https://pybit.es/catalogue/the-pdm-program/)
- [Typer Documentation](https://typer.tiangolo.com)

---
Feel free to suggest any improvements or share your feedback by logging an issue against this repo!
