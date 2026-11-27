"""Integration performance comparison page."""

import streamlit as st

from dashboard.branding import render_page_header
from dashboard.charts import runtime_by_integration, runtime_trend
from dashboard.metrics import summarize_performance
from dashboard.ui import get_filtered_runs, render_empty_state

st.set_page_config(page_title="Performance", page_icon="⏱️", layout="wide")
render_page_header(
    "Integration performance",
    "Compare run durations across integrations and over time.",
)
runs = get_filtered_runs()

if not render_empty_state(runs):
    summary = summarize_performance(runs)
    chart_columns = st.columns(2)
    chart_columns[0].plotly_chart(runtime_by_integration(summary), width="stretch")
    chart_columns[1].plotly_chart(runtime_trend(runs), width="stretch")
    st.subheader("Runtime statistics")
    st.dataframe(
        summary,
        width="stretch",
        hide_index=True,
        column_config={
            "AverageRuntimeSeconds": st.column_config.NumberColumn(format="%.1f s"),
            "MedianRuntimeSeconds": st.column_config.NumberColumn(format="%.1f s"),
            "P95RuntimeSeconds": st.column_config.NumberColumn(format="%.1f s"),
        },
    )
