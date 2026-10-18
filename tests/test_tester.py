"""Unit tests for subprocess test runner and result persistence (Phase 5, Task T5.01, AC5.01, AC5.05)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillfactory.tester import run_skill_tests


class TesterSubprocessTests(unittest.TestCase):
    def test_run_passing_tests(self):
        """AC5.01 & AC5.05: Subprocess executes passing tests and persists test-results.json."""
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "pass-skill"
            tests_dir = skill_dir / "tests"
            tests_dir.mkdir(parents=True)

            test_code = (
                "import unittest\n\n"
                "class SampleTest(unittest.TestCase):\n"
                "    def test_add(self):\n"
                "        self.assertEqual(1 + 1, 2)\n"
                "    def test_str(self):\n"
                "        self.assertTrue('hello'.startswith('h'))\n"
            )
            (tests_dir / "test_sample.py").write_text(test_code, encoding="utf-8")

            res = run_skill_tests(skill_dir, timeout=10.0, save_report=True)
            self.assertTrue(res.success)
            self.assertEqual(res.tests_run, 2)
            self.assertEqual(res.failures, 0)
            self.assertEqual(res.errors, 0)
            self.assertFalse(res.timed_out)

            # Verify report persistence (AC5.05)
            report_file = skill_dir / ".skillfactory" / "test-results.json"
            self.assertTrue(report_file.exists())
            report_data = json.loads(report_file.read_text(encoding="utf-8"))
            self.assertTrue(report_data["success"])
            self.assertEqual(report_data["tests_run"], 2)

    def test_run_failing_tests(self):
        """Detects failing tests and reports failures without crashing."""
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "fail-skill"
            tests_dir = skill_dir / "tests"
            tests_dir.mkdir(parents=True)

            test_code = (
                "import unittest\n\n"
                "class FailingTest(unittest.TestCase):\n"
                "    def test_wrong(self):\n"
                "        self.assertEqual(1, 2)\n"
            )
            (tests_dir / "test_fail.py").write_text(test_code, encoding="utf-8")

            res = run_skill_tests(skill_dir, timeout=10.0, save_report=True)
            self.assertFalse(res.success)
            self.assertEqual(res.tests_run, 1)
            self.assertEqual(res.failures, 1)

    def test_subprocess_timeout_handling(self):
        """AC5.01: Subprocess test runner times out cleanly and does not hang."""
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "timeout-skill"
            tests_dir = skill_dir / "tests"
            tests_dir.mkdir(parents=True)

            test_code = (
                "import time\n"
                "import unittest\n\n"
                "class HangingTest(unittest.TestCase):\n"
                "    def test_infinite(self):\n"
                "        time.sleep(5.0)\n"
            )
            (tests_dir / "test_hang.py").write_text(test_code, encoding="utf-8")

            res = run_skill_tests(skill_dir, timeout=0.5, save_report=True)
            self.assertFalse(res.success)
            self.assertTrue(res.timed_out)
            self.assertIn("timed out after 0.5 seconds", res.error_message)

    def test_no_tests_found(self):
        """Clean response when no tests/ directory or test files exist."""
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "empty-skill"
            skill_dir.mkdir()

            res = run_skill_tests(skill_dir)
            self.assertTrue(res.success)
            self.assertEqual(res.tests_run, 0)
            self.assertEqual(res.test_files_found, 0)


if __name__ == "__main__":
    unittest.main()
