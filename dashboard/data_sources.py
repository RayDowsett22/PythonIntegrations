"""CSV data source; a SQL Server adapter can be added behind this boundary later."""

from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.config import RUN_HISTORY_PATH, SCHEDULES_PATH
from dashboard.transforms import attach_sections, normalize_run_history


@st.cache_data(show_spinner="Loading integration run history...")
def load_dashboard_data(
    run_history_path: str | Path = RUN_HISTORY_PATH,
    schedules_path: str | Path = SCHEDULES_PATH,
) -> pd.DataFrame:
    """Read, validate, and combine the two CSV inputs, caching results in Streamlit."""
    run_path = Path(run_history_path).expanduser()
    schedule_path = Path(schedules_path).expanduser()
    for path in (run_path, schedule_path):
        if not path.is_file():
            raise FileNotFoundError(
                f"Data file not found: {path}. Set RUN_HISTORY_CSV_PATH or "
                "SCHEDULES_CSV_PATH, or restore the sample CSV files in data/."
            )

    run_history = normalize_run_history(pd.read_csv(run_path), run_path)
    schedules = pd.read_csv(schedule_path, dtype={"TaskID": "string"})
    return attach_sections(run_history, schedules, schedule_path)
