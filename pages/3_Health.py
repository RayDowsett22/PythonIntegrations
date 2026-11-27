"""Run health and success-rate page."""

import streamlit as st

from dashboard.branding import render_page_header
from dashboard.charts import failures_by_integration, success_trend
from dashboard.ui import get_filtered_runs, render_empty_state

st.set_page_config(page_title="Run health", page_icon="✅", layout="wide")
render_page_header("Run health", "Monitor successful runs and API failures.")
runs = get_filtered_runs()

if not render_empty_state(runs):
    chart_columns = st.columns(2)
    chart_columns[0].plotly_chart(success_trend(runs), width="stretch")
    chart_columns[1].plotly_chart(failures_by_integration(runs), width="stretch")

    st.subheader("Failed runs")
    failures = runs.loc[runs["APIFailure"]].sort_values("StartTime", ascending=False)
    if failures.empty:
        st.success("No failed runs match these filters.")
    else:
        st.dataframe(
            failures[
                [
                    "StartTime",
                    "EndTime",
                    "TaskName",
                    "Section",
                    "IsExpected",
                    "TotalRunTimeSeconds",
                    "NonInfoMessages",
                ]
            ],
            width="stretch",
            hide_index=True,
        )
