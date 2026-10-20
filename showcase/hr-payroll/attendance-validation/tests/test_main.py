#!/usr/bin/env python3
"""Automated unit and regression tests for Attendance CSV Validator (Demo 02)."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
import unittest

_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from main import (
    format_markdown_report,
    parse_timestamp_or_time,
    validate_attendance_records,
)


class TestAttendanceValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.demo_dir = Path(__file__).resolve().parent.parent
        self.inputs_dir = self.demo_dir / "sample-inputs"
        self.expected_dir = self.demo_dir / "expected-outputs"

    def test_parse_timestamp_and_overnight(self) -> None:
        """Verify time parsing and date-combining logic."""
        t1 = parse_timestamp_or_time("09:00:00", "2026-10-19")
        self.assertIsNotNone(t1)
        self.assertEqual(t1.hour, 9)
        self.assertEqual(t1.minute, 0)

        t_iso = parse_timestamp_or_time("2026-10-19 22:30:00")
        self.assertIsNotNone(t_iso)
        self.assertEqual(t_iso.hour, 22)

    def test_valid_attendance_dataset(self) -> None:
        """Verify clean dataset with 10 records passes 100%."""
        path = self.inputs_dir / "valid_attendance.csv"
        h_pre = hashlib.sha256(path.read_bytes()).hexdigest()

        reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
        records = list(reader)
        self.assertEqual(len(records), 10)

        result = validate_attendance_records(records)
        self.assertTrue(result["is_clean"])
        self.assertEqual(result["total_records"], 10)
        self.assertEqual(result["valid_records"], 10)
        self.assertEqual(result["anomalies_count"], 0)

        # File immutability check
        h_post = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(h_pre, h_post)

    def test_edge_cases_and_anomaly_detection(self) -> None:
        """Verify duplicate swipe, missing punches, short/excessive shift, and overnight handling."""
        path = self.inputs_dir / "edge_case_attendance.csv"
        reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
        records = list(reader)
        self.assertEqual(len(records), 8)

        result = validate_attendance_records(records)
        self.assertFalse(result["is_clean"])
        self.assertEqual(result["valid_records"], 3)
        self.assertEqual(result["anomalies_count"], 5)

        types = [a["type"] for a in result["anomalies"]]
        self.assertIn("DUPLICATE_SWIPE", types)
        self.assertIn("MISSING_CLOCK_OUT", types)
        self.assertIn("MISSING_CLOCK_IN", types)
        self.assertIn("EXCESSIVE_SHIFT_HOURS", types)
        self.assertIn("SHORT_SHIFT_ANOMALY", types)

    def test_invalid_records_and_missing_employee_id(self) -> None:
        """Verify detection of missing employee IDs and unparseable times."""
        path = self.inputs_dir / "invalid_attendance.csv"
        reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
        records = list(reader)

        result = validate_attendance_records(records)
        self.assertFalse(result["is_clean"])
        types = [a["type"] for a in result["anomalies"]]
        self.assertIn("MISSING_EMPLOYEE_ID", types)
        self.assertIn("INVALID_TIMESTAMP_FORMAT", types)

    def test_markdown_report_matches_expected(self) -> None:
        """Verify markdown output matches expected golden report."""
        path = self.inputs_dir / "valid_attendance.csv"
        expected_md = (self.expected_dir / "valid_attendance_report.md").read_text(encoding="utf-8")

        reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
        records = list(reader)
        data = validate_attendance_records(records)
        rendered_md = format_markdown_report(data)

        self.assertEqual(rendered_md.strip(), expected_md.strip())


if __name__ == "__main__":
    unittest.main()
