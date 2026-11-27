"""Plotly chart constructors shared by dashboard pages."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from dashboard.branding import BLUE, INK, NAVY, ORANGE, PLOT_BACKGROUND


def _apply_brand_theme(figure: go.Figure) -> go.Figure:
    """Keep charts readable on the light canvas and use the shared palette."""
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor=PLOT_BACKGROUND,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"family": "Arial, sans-serif", "color": INK},
        title={"font": {"color": NAVY, "size": 17}},
        margin={"l": 16, "r": 16, "t": 52, "b": 24},
    )
    figure.update_xaxes(gridcolor="#E7ECF0", zerolinecolor="#C7D1DA")
    figure.update_yaxes(gridcolor="#E7ECF0", zerolinecolor="#C7D1DA")
    return figure


def issues_by_section(runs: pd.DataFrame) -> go.Figure:
    issue_runs = runs.assign(
        IssueCount=runs["WarningCount"] + runs["OtherNonInfoCount"]
    )
    summary = (
        issue_runs.groupby("Section", as_index=False)["IssueCount"]
        .sum()
        .sort_values("IssueCount", ascending=False)
    )
    figure = px.bar(
        summary,
        x="IssueCount",
        y="Section",
        orientation="h",
        title="Issues by section",
        color_discrete_sequence=[BLUE],
    )
    return _apply_brand_theme(figure)


def issues_by_hour(runs: pd.DataFrame) -> go.Figure:
    issue_runs = runs.assign(
        IssueCount=runs["WarningCount"] + runs["OtherNonInfoCount"],
        Hour=runs["StartTime"].dt.hour,
    )
    summary = issue_runs.groupby("Hour", as_index=False)["IssueCount"].sum()
    hours = pd.DataFrame({"Hour": range(24)}).merge(summary, on="Hour", how="left")
    hours["IssueCount"] = hours["IssueCount"].fillna(0)
    figure = px.bar(
        hours,
        x="Hour",
        y="IssueCount",
        title="Issues by run start hour",
        color_discrete_sequence=[ORANGE],
    )
    figure.update_xaxes(tickmode="linear", dtick=3, tickformat="02d")
    return _apply_brand_theme(figure)


def runtime_by_integration(summary: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        summary.sort_values("AverageRuntimeSeconds"),
        x="AverageRuntimeSeconds",
        y="TaskName",
        orientation="h",
        title="Average runtime by integration",
        labels={"AverageRuntimeSeconds": "Average runtime (seconds)", "TaskName": "Integration"},
        color_discrete_sequence=[BLUE],
    )
    return _apply_brand_theme(figure)


def runtime_trend(runs: pd.DataFrame) -> go.Figure:
    daily = runs.assign(Date=runs["StartTime"].dt.floor("D")).groupby(
        "Date", as_index=False
    )["TotalRunTimeSeconds"].mean()
    figure = px.line(
        daily,
        x="Date",
        y="TotalRunTimeSeconds",
        markers=True,
        title="Average runtime over time",
        labels={"TotalRunTimeSeconds": "Average runtime (seconds)"},
        color_discrete_sequence=[BLUE],
    )
    figure.update_traces(line={"width": 3}, marker={"size": 7})
    return _apply_brand_theme(figure)


def success_trend(runs: pd.DataFrame) -> go.Figure:
    daily = runs.assign(
        Date=runs["StartTime"].dt.floor("D"),
        Successful=~runs["APIFailure"],
    ).groupby("Date", as_index=False)["Successful"].mean()
    daily["Successful"] = daily["Successful"] * 100
    figure = px.line(
        daily,
        x="Date",
        y="Successful",
        markers=True,
        title="Successful runs over time",
        labels={"Successful": "Successful runs (%)"},
        range_y=[0, 100],
        color_discrete_sequence=[BLUE],
    )
    figure.update_traces(line={"width": 3}, marker={"size": 7})
    return _apply_brand_theme(figure)


def failures_by_integration(runs: pd.DataFrame) -> go.Figure:
    failures = (
        runs.loc[runs["APIFailure"]]
        .groupby("TaskName", as_index=False)
        .size()
        .rename(columns={"size": "FailureCount"})
        .sort_values("FailureCount", ascending=False)
    )
    figure = px.bar(
        failures,
        x="TaskName",
        y="FailureCount",
        title="Failures by integration",
        color_discrete_sequence=[ORANGE],
    )
    return _apply_brand_theme(figure)
