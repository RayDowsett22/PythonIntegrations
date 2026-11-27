"""Overview page for the integration run-history dashboard."""

import streamlit as st

from dashboard.branding import render_page_header
from dashboard.metrics import calculate_kpis, format_duration
from dashboard.ui import get_filtered_runs, render_empty_state

st.set_page_config(page_title="API Integration Dashboard", page_icon="📊", layout="wide")
render_page_header(
    "API Integration Dashboard",
    "Run history, integration performance, and operational health.",
)

runs = get_filtered_runs()
if not render_empty_state(runs):
    kpis = calculate_kpis(runs)
    cards = st.columns(4)
    cards[0].metric(
        "Runs with results",
        f"{kpis.runs_with_results:,}",
        f"{kpis.results_percent:.1f}% of runs",
    )
    cards[1].metric(
        "Runs with warnings",
        f"{kpis.runs_with_warnings:,}",
        f"{kpis.warnings_percent:.1f}% of runs",
    )
    cards[2].metric(
        "Successful runs",
        f"{kpis.successful_runs:,}",
        f"{kpis.successful_percent:.1f}% of runs",
    )
    cards[3].metric(
        "Total runtime",
        format_duration(kpis.total_runtime_seconds),
        f"Avg: {format_duration(kpis.average_runtime_seconds)} per run",
    )

    st.subheader("Recent runs")
    recent = runs.sort_values("StartTime", ascending=False).head(15)
    st.dataframe(
        recent[
            [
                "StartTime",
                "TaskName",
                "Section",
                "TotalRunTimeSeconds",
                "ResultStoreRowCount",
                "WarningCount",
                "APIFailure",
            ]
        ],
        width="stretch",
        hide_index=True,
    )
