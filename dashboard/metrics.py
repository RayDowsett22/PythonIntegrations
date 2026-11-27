"""Reusable dashboard KPI and aggregation calculations."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RunKPIs:
    total_runs: int
    runs_with_results: int
    runs_with_warnings: int
    successful_runs: int
    total_runtime_seconds: float
    average_runtime_seconds: float

    @property
    def results_percent(self) -> float:
        return _percent(self.runs_with_results, self.total_runs)

    @property
    def warnings_percent(self) -> float:
        return _percent(self.runs_with_warnings, self.total_runs)

    @property
    def successful_percent(self) -> float:
        return _percent(self.successful_runs, self.total_runs)


def _percent(numerator: int, denominator: int) -> float:
    return numerator / denominator * 100 if denominator else 0.0


def calculate_kpis(runs: pd.DataFrame) -> RunKPIs:
    """Calculate KPIs using explicit row-level definitions."""
    total = len(runs)
    return RunKPIs(
        total_runs=total,
        runs_with_results=int(runs["ResultStoreRowCount"].gt(0).sum()),
        runs_with_warnings=int(runs["WarningCount"].gt(0).sum()),
        successful_runs=int((~runs["APIFailure"]).sum()),
        total_runtime_seconds=float(runs["TotalRunTimeSeconds"].sum()),
        average_runtime_seconds=float(runs["TotalRunTimeSeconds"].mean()) if total else 0.0,
    )


def format_duration(seconds: float) -> str:
    """Format seconds as a readable total, avoiding unnecessary zero units."""
    total_seconds = max(0, int(round(seconds)))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {remaining_seconds}s"
    return f"{remaining_seconds}s"


def summarize_performance(runs: pd.DataFrame) -> pd.DataFrame:
    """Aggregate run count and runtime statistics by integration."""
    return (
        runs.groupby("TaskName", dropna=False)
        .agg(
            RunCount=("TaskID", "size"),
            AverageRuntimeSeconds=("TotalRunTimeSeconds", "mean"),
            MedianRuntimeSeconds=("TotalRunTimeSeconds", "median"),
            P95RuntimeSeconds=("TotalRunTimeSeconds", lambda values: values.quantile(0.95)),
        )
        .sort_values("AverageRuntimeSeconds", ascending=False)
        .reset_index()
    )
