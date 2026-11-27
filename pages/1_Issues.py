"""Issue analysis page."""

import streamlit as st

from dashboard.branding import render_page_header
from dashboard.charts import issues_by_hour, issues_by_section
from dashboard.ui import get_filtered_runs, render_empty_state

st.set_page_config(page_title="Issues", page_icon="⚠️", layout="wide")
render_page_header("Issue analysis", "Explore warnings, failures, and other run issues.")
runs = get_filtered_runs()

if not render_empty_state(runs):
    chart_columns = st.columns(2)
    chart_columns[0].plotly_chart(issues_by_section(runs), width="stretch")
    chart_columns[1].plotly_chart(issues_by_hour(runs), width="stretch")

    issue_rows = runs.loc[
        runs["WarningCount"].gt(0)
        | runs["OtherNonInfoCount"].gt(0)
        | runs["APIFailure"]
    ].copy()
    st.subheader("Issue details")
    if issue_rows.empty:
        st.success("No warnings, non-information messages, or failed runs match these filters.")
    else:
        st.dataframe(
            issue_rows.sort_values("StartTime", ascending=False)[
                [
                    "StartTime",
                    "EndTime",
                    "TaskName",
                    "Section",
                    "WarningCount",
                    "OtherNonInfoCount",
                    "APIFailure",
                    "NonInfoMessages",
                ]
            ],
            width="stretch",
            hide_index=True,
        )
