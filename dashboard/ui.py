"""Small Streamlit helpers for loading data and presenting consistent UI."""

import pandas as pd
import streamlit as st

from dashboard.branding import apply_branding
from dashboard.data_sources import load_dashboard_data
from dashboard.filters import render_sidebar_filters


def get_filtered_runs() -> pd.DataFrame:
    apply_branding()
    runs = load_dashboard_data()
    if runs.empty:
        st.warning("The selected data files contain no run records.")
        return runs
    return render_sidebar_filters(runs)


def render_empty_state(runs: pd.DataFrame) -> bool:
    """Show an explanatory message when filters remove all records."""
    if runs.empty:
        st.info("No runs match the selected filters.")
        return True
    return False
