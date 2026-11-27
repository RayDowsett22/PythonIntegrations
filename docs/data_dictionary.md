# API Integration Dashboard Data Dictionary

This document describes the CSV inputs, normalized run-history fields, and
calculated values used by the dashboard. The default inputs are
`data/sample_run_history.csv` and `data/sample_schedules.csv`. CSV paths can be
overridden with the `RUN_HISTORY_CSV_PATH` and `SCHEDULES_CSV_PATH` environment
variables.

## Run history input

The run-history CSV must contain the required fields below. Additional source
columns are retained when loaded but are not currently used by dashboard
calculations unless listed as optional here.

| Field | Required | Data type | Meaning and handling |
| --- | --- | --- | --- |
| `TaskID` | Yes | Text | Integration identifier and join key to the schedules CSV. Whitespace at either end is removed. |
| `TaskName` | No | Text | Display name used to group integrations and performance metrics. If absent, the normalized value falls back to `TaskID`. |
| `ScriptName` | No | Text | Script identifier from the source export. Retained for reference; not currently used in KPI calculations. |
| `StartTime` | Yes | Date/time | Run start timestamp. Parsed day-first to support the existing exports. Invalid or missing values stop loading. Used by date filters and time-based charts. ISO 8601 input is recommended for new exports. |
| `EndTime` | Yes | Date/time | Run end timestamp. Parsed day-first. If `TotalRunTimeSeconds` is blank, a valid end time is required to derive runtime from the start time. |
| `IsExpected` | Yes | Boolean | Whether the run was expected. Parsed as a boolean and shown in the failed-runs table; it does not determine the success KPI. |
| `WarningCount` | Yes | Number | Number of warnings for the run. Blank values are treated as zero. If this column is absent, `WaningCount` is accepted as an alternate spelling. |
| `OtherNonInfoCount` | Yes | Number | Count of other non-information messages. Blank values are treated as zero. |
| `NonInfoMessages` | No | Text | Message details shown in issue and failed-run tables. If absent, it defaults to an empty string. |
| `TotalRunTimeSeconds` | Yes | Number | Run duration in seconds. If blank, calculated as `EndTime - StartTime`; loading fails if neither a runtime nor usable timestamps are available. |
| `ResultStoreRowCount` | Yes | Number | Number of rows written to the results store. Blank values are treated as zero. |
| `APIFailure` | Yes | Boolean | Whether the run failed at the API level. `true` means failed; `false` means successful for dashboard success metrics. |

Boolean fields accept `true`/`false`, `1`/`0`, `yes`/`no`, and `y`/`n`,
case-insensitively. Missing or unrecognized boolean values are rejected rather
than silently counted as success or failure. Non-numeric values in count or
runtime fields are also rejected.

## Schedules input

| Field | Required | Data type | Meaning and handling |
| --- | --- | --- | --- |
| `TaskID` | Yes | Text | Integration identifier matching `TaskID` in run history. |
| `Section` | Yes | Text | Business/process section used to group integrations in the issue analysis. |

The schedule data is joined to run history by `TaskID`. A non-empty `Section`
already present in run history takes precedence; otherwise, the section from
the schedules CSV is used. Missing or empty sections become `Uncategorized`.
Only the first schedules row for a duplicated `TaskID` is used, so each run
remains a single row. Prefer one schedule row per `TaskID`.

## Normalized and calculated fields

| Field or measure | Definition |
| --- | --- |
| `Section` | Section resolved from run history or schedule metadata, with `Uncategorized` as the fallback. |
| Runs with results | Count of runs where `ResultStoreRowCount > 0`. |
| Runs with warnings | Count of runs where `WarningCount > 0`. |
| Successful runs | Count of runs where `APIFailure` is false. Warnings and `IsExpected` do not change this classification. |
| Results, warnings, and success percentages | Corresponding run count divided by all runs remaining after filters, multiplied by 100. Returns 0% when there are no filtered runs. |
| Total runtime | Sum of `TotalRunTimeSeconds` over filtered runs. |
| Average runtime | Mean of `TotalRunTimeSeconds` over filtered runs. |
| `IssueCount` | For issue charts, `WarningCount + OtherNonInfoCount` per run. API failures appear in issue details but are not added to this count. |
| `Hour` | Hour of day (0–23) from `StartTime`; issue-by-time chart groups `IssueCount` by this hour. |
| Runtime `RunCount` | Number of run rows for an integration. |
| Runtime average / median / P95 | Mean, median, and 95th percentile of `TotalRunTimeSeconds` for an integration. |
| Daily successful-run percentage | For each start date, the percentage of runs where `APIFailure` is false. |
| Failures by integration | Count of run rows where `APIFailure` is true, grouped by `TaskName`. |

## Filters and page behavior

The time-period filter is applied to `StartTime` and is shared across pages
within the current Streamlit session:

| Selection | Included start times |
| --- | --- |
| In the last day | From the current time minus 24 hours through the current time |
| In the last 7 days | From the current time minus 7 days through the current time |
| In the last 30 days | From the current time minus 30 days through the current time |
| In the last 90 days | From the current time minus 90 days through the current time |
| All Time | All available run-history rows |

The date windows use the machine time where Streamlit is running. The
integration selector further narrows the rows used by the page. KPI percentages,
issue counts, and runtime summaries use the filtered rows.
