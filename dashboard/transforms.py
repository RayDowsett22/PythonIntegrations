"""Validation and normalization for run-history and schedule data."""

from pathlib import Path

import pandas as pd

RUN_COLUMNS = {
    "TaskID",
    "StartTime",
    "EndTime",
    "IsExpected",
    "WarningCount",
    "OtherNonInfoCount",
    "TotalRunTimeSeconds",
    "ResultStoreRowCount",
    "APIFailure",
}
SCHEDULE_COLUMNS = {"TaskID", "Section"}


def _require_columns(frame: pd.DataFrame, required: set[str], path: Path) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")


def _parse_boolean(values: pd.Series, column: str) -> pd.Series:
    """Parse common CSV boolean encodings and reject ambiguous values."""
    truthy = {"true", "1", "yes", "y"}
    falsy = {"false", "0", "no", "n"}

    def convert(value: object) -> bool:
        if pd.isna(value):
            raise ValueError(f"Missing boolean value in {column}")
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in truthy:
            return True
        if normalized in falsy:
            return False
        raise ValueError(f"Unrecognized boolean value in {column}: {value!r}")

    return values.map(convert).astype(bool)


def _parse_number(values: pd.Series, column: str) -> pd.Series:
    parsed = pd.to_numeric(values, errors="coerce")
    invalid = values.notna() & values.astype(str).str.strip().ne("") & parsed.isna()
    if invalid.any():
        examples = values.loc[invalid].astype(str).drop_duplicates().head(3).tolist()
        raise ValueError(f"Invalid numeric value(s) in {column}: {examples}")
    return parsed


def normalize_run_history(frame: pd.DataFrame, source: Path) -> pd.DataFrame:
    """Normalize source column types and add consistent dashboard fields."""
    frame = frame.copy()

    # Accept the occasional "WaningCount" typo from manually prepared exports.
    if "WarningCount" not in frame.columns and "WaningCount" in frame.columns:
        frame = frame.rename(columns={"WaningCount": "WarningCount"})
    _require_columns(frame, RUN_COLUMNS, source)

    frame["TaskID"] = frame["TaskID"].astype("string").str.strip()
    frame["StartTime"] = pd.to_datetime(
        frame["StartTime"], format="mixed", dayfirst=True, errors="coerce"
    )
    frame["EndTime"] = pd.to_datetime(
        frame["EndTime"], format="mixed", dayfirst=True, errors="coerce"
    )
    if frame["StartTime"].isna().any():
        count = int(frame["StartTime"].isna().sum())
        raise ValueError(f"{source} contains {count} row(s) with an invalid StartTime")

    for column in ("WarningCount", "OtherNonInfoCount", "ResultStoreRowCount"):
        frame[column] = _parse_number(frame[column], column).fillna(0)
    runtime = _parse_number(frame["TotalRunTimeSeconds"], "TotalRunTimeSeconds")
    missing_runtime = runtime.isna()
    runtime.loc[missing_runtime] = (
        frame.loc[missing_runtime, "EndTime"] - frame.loc[missing_runtime, "StartTime"]
    ).dt.total_seconds()
    if runtime.isna().any():
        count = int(runtime.isna().sum())
        raise ValueError(
            f"{source} contains {count} row(s) without a runtime or usable EndTime"
        )
    frame["TotalRunTimeSeconds"] = runtime
    frame["APIFailure"] = _parse_boolean(frame["APIFailure"], "APIFailure")
    frame["IsExpected"] = _parse_boolean(frame["IsExpected"], "IsExpected")

    if "TaskName" not in frame.columns:
        frame["TaskName"] = frame["TaskID"]
    if "NonInfoMessages" not in frame.columns:
        frame["NonInfoMessages"] = ""
    frame["NonInfoMessages"] = frame["NonInfoMessages"].fillna("").astype(str)

    return frame


def attach_sections(
    run_history: pd.DataFrame, schedules: pd.DataFrame, source: Path
) -> pd.DataFrame:
    """Attach one section per task without multiplying runs on duplicate schedules."""
    _require_columns(schedules, SCHEDULE_COLUMNS, source)
    schedule_sections = schedules.loc[:, ["TaskID", "Section"]].copy()
    schedule_sections["TaskID"] = schedule_sections["TaskID"].astype("string").str.strip()
    schedule_sections["Section"] = schedule_sections["Section"].fillna("").astype(str)
    schedule_sections = schedule_sections.drop_duplicates("TaskID", keep="first")
    schedule_sections = schedule_sections.rename(columns={"Section": "ScheduleSection"})

    merged = run_history.merge(schedule_sections, on="TaskID", how="left", validate="many_to_one")
    if "Section" in run_history.columns:
        existing_section = merged["Section"].replace("", pd.NA)
        merged["Section"] = existing_section.fillna(merged["ScheduleSection"])
        merged = merged.drop(columns="ScheduleSection")
    else:
        merged = merged.rename(columns={"ScheduleSection": "Section"})
    merged["Section"] = merged["Section"].replace("", "Uncategorized").fillna("Uncategorized")
    return merged
