"""Tests for structured-notes-formatter."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

# Import from scripts/main.py
script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import format_markdown, parse_raw_notes


class TestStructuredNotesFormatter(unittest.TestCase):
    def test_parse_meeting_notes(self):
        sample = """# Q4 Strategy Alignment
Date: 2026-10-20
Attendees: Alice, Bob, Charlie
Discussed product launch goals for November.
Decision: Launch release candidate on Oct 25.
Action: Finalize user documentation (Owner: Alice)
Action: Verify automated tests @Bob
Reviewed marketing schedule.
"""
        data = parse_raw_notes(sample)
        self.assertEqual(data["title"], "Q4 Strategy Alignment")
        self.assertEqual(data["date"], "2026-10-20")
        self.assertEqual(data["attendees"], ["Alice", "Bob", "Charlie"])
        self.assertEqual(len(data["decisions"]), 1)
        self.assertEqual(len(data["actions"]), 2)
        self.assertEqual(data["actions"][0]["owner"], "Alice")
        self.assertEqual(data["actions"][1]["owner"], "Bob")

        md = format_markdown(data)
        self.assertIn("# Q4 Strategy Alignment", md)
        self.assertIn("**Attendees:** Alice, Bob, Charlie", md)
        self.assertIn("## Key Decisions", md)
        self.assertIn("## Action Items", md)


if __name__ == "__main__":
    unittest.main()
