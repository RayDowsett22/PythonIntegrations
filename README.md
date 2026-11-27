# API Integration Dashboard

A local, multipage Streamlit dashboard for exploring API integration run history
with Pandas and Plotly. It starts with synthetic CSV data and keeps data loading
separate from the pages so a SQL Server source can be added later.

See the [data dictionary](./docs/data_dictionary.md) for input field
definitions, normalization rules, and dashboard metric calculations.

## Set up the Python environment

Create and activate a virtual environment, then install the project dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the dashboard

```powershell
streamlit run app.py
```

The app uses `data/sample_run_history.csv` and `data/sample_schedules.csv` by
default. To use different CSV exports, set these environment variables before
starting Streamlit:

```powershell
$env:RUN_HISTORY_CSV_PATH = "C:\path\to\RunHistory.csv"
$env:SCHEDULES_CSV_PATH = "C:\path\to\Schedules.csv"
streamlit run app.py
```

The run-history CSV must contain `TaskID`, `StartTime`, `EndTime`, `IsExpected`,
`WarningCount`, `OtherNonInfoCount`, `TotalRunTimeSeconds`,
`ResultStoreRowCount`, and `APIFailure`. `WaningCount` is accepted as an
alternate spelling for `WarningCount`. The schedule CSV supplies `TaskID` and
`Section`. Empty warning, non-information, and result counts are treated as
zero; an empty runtime is derived from start/end timestamps where possible.
Boolean values must be explicit (`true`/`false`, `1`/`0`, `yes`/`no`, or `y`/`n`)
so an unknown API failure status cannot be counted as a successful run.

## Dashboard definitions

- **Runs with results:** `ResultStoreRowCount > 0`.
- **Runs with warnings:** `WarningCount > 0`.
- **Successful runs:** `APIFailure` is false.
- **Issues by section/time:** summed warning and other-non-info counts, grouped
  by the section and the run's start hour. Failed runs also appear in issue
  details.
- **Runtime:** source `TotalRunTimeSeconds`, aggregated as total, average,
  median, and 95th percentile where applicable.

The date period and integration selectors are shared across pages. “In the last
day” means the preceding 24 hours; all bounded periods are relative to the
current local time.

## Branding

The interface uses the navy, blue, orange, and light-gray palette from the
provided Bentley reference. Shared page banners, KPI cards, tables, and Plotly
charts use the same palette; the header uses a text wordmark rather than a
separate logo image asset.

## Project layout

- `app.py` provides the KPI overview.
- `pages/` contains issue, performance, and health views.
- `dashboard/` contains the CSV adapter, normalization, filters, metrics,
  chart builders, and shared UI helpers.
- `data/` contains small synthetic CSVs for local development.
- `tests/` contains focused tests for normalization, joins, and calculations.
