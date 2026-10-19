"""Tests for project-status-reporter."""
from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import format_markdown_report, generate_status_summary


class TestProjectStatusReporter(unittest.TestCase):
    def test_status_reporting(self):
        milestones = [
            {"id": "M1", "name": "Architecture Design", "owner": "Alex", "status": "COMPLETED", "due_date": "2026-10-01"},
            {"id": "M2", "name": "API Implementation", "owner": "Sam", "status": "IN_PROGRESS", "due_date": "2026-10-25"},
            {"id": "M3", "name": "Security Audit", "owner": "Ken", "status": "BLOCKED", "due_date": "2026-10-10"}, # Blocked & overdue
        ]
        ref = date(2026, 10, 15)
        res = generate_status_summary(milestones, reference_date=ref)
        self.assertEqual(res["total_milestones"], 3)
        self.assertEqual(res["completed"], 1)
        self.assertEqual(res["in_progress"], 1)
        self.assertEqual(res["blocked"], 1)
        self.assertEqual(res["overdue_count"], 1)
        self.assertEqual(res["overall_health"], "Red")

        md = format_markdown_report(res, project_title="Core Platform")
        self.assertIn("# Core Platform — Weekly Status Report", md)
        self.assertIn("Architecture Design", md)
        self.assertIn("**YES**", md)


if __name__ == "__main__":
    unittest.main()
