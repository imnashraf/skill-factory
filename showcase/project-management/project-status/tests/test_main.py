#!/usr/bin/env python3
"""Automated unit and regression tests for Project Status Reporter (Demo 03)."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
import unittest

_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from main import (
    calculate_project_status,
    format_markdown_report,
    parse_milestones_csv,
    parse_raid_csv,
)


class TestProjectStatusReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.demo_dir = Path(__file__).resolve().parent.parent
        self.inputs_dir = self.demo_dir / "sample-inputs"
        self.expected_dir = self.demo_dir / "expected-outputs"
        self.ref_date = date(2026, 10, 20)

    def test_valid_project_dataset(self) -> None:
        """Verify on-schedule valid project yields GREEN status."""
        m_path = self.inputs_dir / "valid_milestones.csv"
        r_path = self.inputs_dir / "valid_raid.csv"

        m_hash_pre = hashlib.sha256(m_path.read_bytes()).hexdigest()
        r_hash_pre = hashlib.sha256(r_path.read_bytes()).hexdigest()

        milestones, m_err = parse_milestones_csv(m_path)
        raid_items, r_err = parse_raid_csv(r_path)

        self.assertEqual(m_err, [])
        self.assertEqual(r_err, [])
        self.assertEqual(len(milestones), 6)
        self.assertEqual(len(raid_items), 5)

        data = calculate_project_status(milestones, raid_items, reference_date=self.ref_date)
        self.assertEqual(data["overall_health"], "GREEN")
        self.assertEqual(data["completed_count"], 2)
        self.assertEqual(data["blocked_count"], 0)
        self.assertEqual(data["overdue_count"], 0)
        self.assertEqual(data["critical_risks_count"], 0)
        self.assertEqual(len(data["action_summary"]), 0)

        # File immutability check
        m_hash_post = hashlib.sha256(m_path.read_bytes()).hexdigest()
        r_hash_post = hashlib.sha256(r_path.read_bytes()).hexdigest()
        self.assertEqual(m_hash_pre, m_hash_post)
        self.assertEqual(r_hash_pre, r_hash_post)

    def test_edge_case_yields_red_and_action_summary(self) -> None:
        """Verify blocked milestones, overdue dates, and critical risks yield RED status."""
        m_path = self.inputs_dir / "edge_case_milestones.csv"
        r_path = self.inputs_dir / "edge_case_raid.csv"

        milestones, _ = parse_milestones_csv(m_path)
        raid_items, _ = parse_raid_csv(r_path)

        data = calculate_project_status(milestones, raid_items, reference_date=self.ref_date)
        self.assertEqual(data["overall_health"], "RED")
        self.assertEqual(data["blocked_count"], 1)
        self.assertEqual(data["overdue_count"], 2)
        self.assertEqual(data["critical_risks_count"], 1)
        self.assertGreaterEqual(len(data["action_summary"]), 4)

        action_types = [a["type"] for a in data["action_summary"]]
        self.assertIn("BLOCKED_MILESTONE", action_types)
        self.assertIn("CRITICAL_RISK", action_types)
        self.assertIn("HIGH_RISK", action_types)
        self.assertIn("ACTIVE_ISSUE", action_types)

    def test_invalid_milestones_csv(self) -> None:
        """Verify validation errors for unparseable dates, bad statuses, and out-of-range percentages."""
        m_path = self.inputs_dir / "invalid_milestones.csv"
        _, errors = parse_milestones_csv(m_path)
        self.assertGreaterEqual(len(errors), 4)
        self.assertTrue(any("invalid date" in e for e in errors))
        self.assertTrue(any("invalid milestone status" in e for e in errors))
        self.assertTrue(any("out of range" in e for e in errors))
        self.assertTrue(any("missing milestone ID" in e for e in errors))

    def test_markdown_report_matches_expected(self) -> None:
        """Verify markdown report matches expected golden report."""
        m_path = self.inputs_dir / "valid_milestones.csv"
        r_path = self.inputs_dir / "valid_raid.csv"
        expected_md = (self.expected_dir / "valid_project_report.md").read_text(encoding="utf-8")

        milestones, _ = parse_milestones_csv(m_path)
        raid_items, _ = parse_raid_csv(r_path)
        data = calculate_project_status(milestones, raid_items, reference_date=self.ref_date)
        rendered_md = format_markdown_report(data, project_name="Enterprise Delivery Program")

        self.assertEqual(rendered_md.strip(), expected_md.strip())


if __name__ == "__main__":
    unittest.main()
