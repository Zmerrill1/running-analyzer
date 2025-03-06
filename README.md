# Running Data Analyzer

A command-line tool for analyzing running data. Manually add data or upload from a CSV or FIT file. Supports basic data insights like distance, pace, and trends over time.

## Features

Load and analyze running data from CSV or FIT files.

Calculate total distance, average pace, and other key metrics.

Identify trends and generate insights from past runs.

Command-line interface (CLI) for easy use.


## Installation
You can install the Running Data Analyzer from PyPI using `uv`:
```
uv pip install running-data-analyzer
```

## Usage
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
