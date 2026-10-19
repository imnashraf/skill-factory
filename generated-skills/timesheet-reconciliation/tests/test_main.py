"""Tests for timesheet-reconciliation."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import format_markdown_report, reconcile_timesheets


class TestTimesheetReconciliation(unittest.TestCase):
    def test_timesheet_reconcile(self):
        timesheets = [
            {"employee_id": "EMP-01", "project_code": "PRJ-A", "hours": "20"},
            {"employee_id": "EMP-01", "project_code": "PRJ-A", "hours": "25"}, # total 45
            {"employee_id": "EMP-02", "project_code": "PRJ-B", "hours": "30"},
        ]
        budgets = [
            {"employee_id": "EMP-01", "project_code": "PRJ-A", "allocated_hours": "40"}, # overrun by 5
            {"employee_id": "EMP-02", "project_code": "PRJ-B", "allocated_hours": "40"}, # under by 10
        ]
        res = reconcile_timesheets(timesheets, budgets)
        self.assertEqual(res["total_budgeted_hours"], 80.0)
        self.assertEqual(res["total_logged_hours"], 75.0)
        self.assertEqual(res["overruns_count"], 1)
        self.assertEqual(res["under_allocations_count"], 1)

        md = format_markdown_report(res)
        self.assertIn("# Timesheet vs. Budget Reconciliation Report", md)
        self.assertIn("Over Allocation", md)


if __name__ == "__main__":
    unittest.main()
