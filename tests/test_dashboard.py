"""Focused tests for data normalization and dashboard calculations."""

import unittest
from pathlib import Path

import pandas as pd

from dashboard.branding import BLUE, ORANGE, PLOT_BACKGROUND
from dashboard.charts import issues_by_hour, issues_by_section
from dashboard.metrics import calculate_kpis, summarize_performance
from dashboard.transforms import attach_sections, normalize_run_history


class DashboardDataTests(unittest.TestCase):
    def test_normalization_accepts_warning_typo_and_csv_boolean_values(self) -> None:
        raw = pd.DataFrame(
            {
                "TaskID": ["task-1"],
                "StartTime": ["27/11/2026 09:00:00"],
                "EndTime": ["27/11/2026 09:01:00"],
                "IsExpected": ["TRUE"],
                "WaningCount": [1],
                "OtherNonInfoCount": [0],
                "TotalRunTimeSeconds": [60],
                "ResultStoreRowCount": [2],
                "APIFailure": ["0"],
            }
        )

        normalized = normalize_run_history(raw, Path("sample.csv"))

        self.assertEqual(normalized.loc[0, "WarningCount"], 1)
        self.assertFalse(normalized.loc[0, "APIFailure"])
        self.assertEqual(normalized.loc[0, "StartTime"].day, 27)

    def test_schedule_join_does_not_duplicate_runs(self) -> None:
        runs = pd.DataFrame({"TaskID": ["task-1"], "Section": [""]})
        schedules = pd.DataFrame(
            {"TaskID": ["task-1", "task-1"], "Section": ["Finance", "Older section"]}
        )

        merged = attach_sections(runs, schedules, Path("schedules.csv"))

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged.loc[0, "Section"], "Finance")

    def test_normalization_rejects_unknown_failure_status(self) -> None:
        raw = pd.DataFrame(
            {
                "TaskID": ["task-1"],
                "StartTime": ["2026-11-27 09:00:00"],
                "EndTime": ["2026-11-27 09:01:00"],
                "IsExpected": ["TRUE"],
                "WarningCount": [0],
                "OtherNonInfoCount": [0],
                "TotalRunTimeSeconds": [60],
                "ResultStoreRowCount": [0],
                "APIFailure": [""],
            }
        )

        with self.assertRaisesRegex(ValueError, "Unrecognized boolean value"):
            normalize_run_history(raw, Path("sample.csv"))

    def test_kpis_use_run_counts_and_failure_flag(self) -> None:
        runs = pd.DataFrame(
            {
                "ResultStoreRowCount": [5, 0, 1],
                "WarningCount": [1, 0, 2],
                "APIFailure": [False, True, False],
                "TotalRunTimeSeconds": [10, 20, 30],
            }
        )

        kpis = calculate_kpis(runs)

        self.assertEqual((kpis.total_runs, kpis.runs_with_results), (3, 2))
        self.assertEqual((kpis.runs_with_warnings, kpis.successful_runs), (2, 2))
        self.assertAlmostEqual(kpis.results_percent, 200 / 3)
        self.assertEqual(kpis.total_runtime_seconds, 60)
        self.assertEqual(kpis.average_runtime_seconds, 20)

    def test_performance_summary_groups_by_integration(self) -> None:
        runs = pd.DataFrame(
            {
                "TaskName": ["alpha", "alpha", "beta"],
                "TaskID": ["a", "a", "b"],
                "TotalRunTimeSeconds": [10.0, 30.0, 20.0],
            }
        )

        summary = summarize_performance(runs).set_index("TaskName")

        self.assertEqual(summary.loc["alpha", "RunCount"], 2)
        self.assertEqual(summary.loc["alpha", "AverageRuntimeSeconds"], 20.0)
        self.assertEqual(summary.loc["alpha", "P95RuntimeSeconds"], 29.0)

    def test_issue_charts_use_brand_palette_and_light_plot_canvas(self) -> None:
        runs = pd.DataFrame(
            {
                "Section": ["Finance"],
                "WarningCount": [1],
                "OtherNonInfoCount": [0],
                "StartTime": [pd.Timestamp("2026-11-27 09:00:00")],
            }
        )

        section_chart = issues_by_section(runs)
        hourly_chart = issues_by_hour(runs)

        self.assertEqual(section_chart.data[0].marker.color, BLUE)
        self.assertEqual(hourly_chart.data[0].marker.color, ORANGE)
        self.assertEqual(section_chart.layout.paper_bgcolor, PLOT_BACKGROUND)


if __name__ == "__main__":
    unittest.main()
