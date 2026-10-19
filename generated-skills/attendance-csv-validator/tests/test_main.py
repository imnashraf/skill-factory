"""Tests for attendance-csv-validator."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import format_report_markdown, validate_attendance_records


class TestAttendanceValidator(unittest.TestCase):
    def test_validation_logic(self):
        records = [
            {"employee_id": "EMP-01", "date": "2026-10-20", "clock_in": "09:00", "clock_out": "17:00"}, # Valid
            {"employee_id": "EMP-02", "date": "2026-10-20", "clock_in": "09:00", "clock_out": ""},      # Missing out
            {"employee_id": "EMP-03", "date": "2026-10-20", "clock_in": "18:00", "clock_out": "09:00"}, # Negative
            {"employee_id": "EMP-04", "date": "2026-10-20", "clock_in": "06:00", "clock_out": "22:30"}, # > 14h
            {"employee_id": "EMP-01", "date": "2026-10-20", "clock_in": "09:00", "clock_out": "17:00"}, # Dup swipe
        ]
        res = validate_attendance_records(records)
        self.assertEqual(res["total_records"], 5)
        self.assertEqual(res["valid_records"], 1)
        self.assertEqual(res["anomaly_count"], 4)
        self.assertFalse(res["is_clean"])

        md = format_report_markdown(res)
        self.assertIn("# Attendance CSV Validation Report", md)
        self.assertIn("MISSING_CLOCK_OUT", md)
        self.assertIn("NEGATIVE_DURATION", md)
        self.assertIn("EXCESSIVE_OVERTIME_ANOMALY", md)
        self.assertIn("DUPLICATE_SWIPE", md)


if __name__ == "__main__":
    unittest.main()
