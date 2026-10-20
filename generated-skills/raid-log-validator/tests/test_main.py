"""Tests for raid-log-validator."""
from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import audit_raid_records, format_markdown_report  # type: ignore


class TestRaidLogValidator(unittest.TestCase):
    def test_audit_flow(self):
        records = [
            {"id": "R-01", "type": "RISK", "description": "Database migration timeout", "owner": "Alice", "status": "OPEN", "severity": "HIGH", "due_date": "2026-11-01"},
            {"id": "I-01", "type": "ISSUE", "description": "Broken API endpoint", "owner": "", "status": "OPEN", "severity": "CRITICAL", "due_date": "2026-10-01"}, # Missing owner, overdue
            {"id": "A-01", "type": "BAD_TYPE", "description": "Valid desc", "owner": "Bob", "status": "OPEN", "severity": "LOW", "due_date": "2026-11-15"}, # Bad type
        ]
        ref = date(2026, 10, 15)
        res = audit_raid_records(records, reference_date=ref)
        self.assertEqual(res["total_records"], 3)
        self.assertEqual(res["overdue_count"], 1)
        self.assertFalse(res["is_healthy"])

        md = format_markdown_report(res)
        self.assertIn("# RAID Register Audit Report", md)
        self.assertIn("Risks: 1", md)
        self.assertIn("I-01", md)


if __name__ == "__main__":
    unittest.main()
