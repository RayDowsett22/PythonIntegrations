"""Application configuration and local data paths."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

# Environment variables let developers point at their own CSV exports without
# changing source files or copying large production datasets into the project.
RUN_HISTORY_PATH = Path(
    os.getenv("RUN_HISTORY_CSV_PATH", DATA_DIR / "sample_run_history.csv")
).expanduser()
SCHEDULES_PATH = Path(
    os.getenv("SCHEDULES_CSV_PATH", DATA_DIR / "sample_schedules.csv")
).expanduser()

DATE_WINDOWS_DAYS = {
    "In the last day": 1,
    "In the last 7 days": 7,
    "In the last 30 days": 30,
    "In the last 90 days": 90,
    "All Time": None,
}
