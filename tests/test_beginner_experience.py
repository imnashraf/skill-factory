"""Automated Usability & Beginner Experience Test Suite (Phase 12, Task T12.05, AC12.05).

Validates:
1. Guided environment diagnostics (skillfactory doctor --guided)
2. Interactive and streamlined skill scaffolding with intelligent defaults
3. Actionable 3-part error messaging with zero raw Python tracebacks
4. Conflict defense during installation
5. Full end-to-end beginner lifecycle (doctor -> new -> validate -> install -> uninstall)
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skillfactory.cli import main
from skillfactory.doctor import format_guided_setup, run_diagnostics
from skillfactory.interview import derive_skill_name, run_interactive_interview


class BeginnerExperienceTests(unittest.TestCase):
    """Test suite for Phase 12 Beginner-Friendly Experience."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_doctor_diagnostics_unit(self) -> None:
        """Verify run_diagnostics generates complete HealthReport data."""
        report = run_diagnostics(project_dir=self.work_path)
        self.assertTrue(report.python_compatible)
        self.assertTrue(report.project_writable)
        self.assertIsInstance(report.checks, list)
        self.assertTrue(len(report.checks) >= 3)

        formatted = format_guided_setup(report)
        self.assertIn("[1/4] Runtime & Prerequisite Check", formatted)
        self.assertIn("[2/4] Readiness Assessment", formatted)
        self.assertIn("[3/4] Recommended Action Items", formatted)
        self.assertIn("[4/4] Beginner Quick Commands", formatted)
        self.assertIn("skillfactory new", formatted)

    def test_cli_doctor_guided(self) -> None:
        """Verify `skillfactory doctor --guided` outputs guided diagnostics without error."""
        out_buf = io.StringIO()
        with patch("sys.stdout", out_buf):
            exit_code = main(["doctor", "--guided", "--project", str(self.work_path)])
        self.assertEqual(exit_code, 0)
        output = out_buf.getvalue()
        self.assertIn("Skill Factory — Guided Beginner Setup", output)
        self.assertIn("Runtime & Prerequisite Check", output)

    def test_cli_doctor_guided_json(self) -> None:
        """Verify `skillfactory doctor --guided --json` outputs structured machine-readable JSON."""
        out_buf = io.StringIO()
        with patch("sys.stdout", out_buf):
            exit_code = main(["doctor", "--guided", "--json", "--project", str(self.work_path)])
        self.assertEqual(exit_code, 0)
        data = json.loads(out_buf.getvalue())
        self.assertIn("is_ready", data)
        self.assertIn("python_version", data)
        self.assertIn("checks", data)

    def test_new_positional_name_and_default_description(self) -> None:
        """Verify beginners can create a skill using positional name without explicit --description."""
        out_dir = self.work_path / "skills"
        exit_code = main(["new", "auto-summarizer", "--output", str(out_dir)])
        self.assertEqual(exit_code, 0)

        created_skill = out_dir / "auto-summarizer"
        self.assertTrue(created_skill.exists())
        self.assertTrue((created_skill / "SKILL.md").exists())
        self.assertTrue((created_skill / "scripts" / "main.py").exists())

        # Check that description was automatically populated
        skill_text = (created_skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("auto summarizer", skill_text.lower())

    def test_missing_name_produces_3_part_actionable_error(self) -> None:
        """Verify running `new` without name non-interactively produces 3-part structured error."""
        err_buf = io.StringIO()
        with patch("sys.stderr", err_buf), patch("sys.stdin.isatty", return_value=False):
            exit_code = main(["new"])
        self.assertEqual(exit_code, 2)
        err_output = err_buf.getvalue()
        self.assertIn("What happened:", err_output)
        self.assertIn("Why it happened:", err_output)
        self.assertIn("What to do next:", err_output)
        self.assertNotIn("Traceback (most recent call last):", err_output)

    def test_interactive_interview_name_sanitization_loop(self) -> None:
        """Verify the interactive interview guides invalid names to valid kebab-case candidates."""
        # Simulated answers:
        # 1. problem: "organize messy download files"
        # 2. raw name: "My Invalid Name!" -> prompt asks accept cleaned -> "y"
        # 3. description: accept default
        # 4. scripts: "y"
        # 5. template: accept default
        # 6. inputs: ""
        # 7. outputs: ""
        # 8. step 1: "scan folder", step 2: ""
        # 9. author: "test"
        # 10. license: "MIT"
        # 11. platform: "all"
        answers = iter([
            "organize messy download files",
            "My Invalid Name!",
            "y",  # Accept sanitized name suggestion
            "",   # description default
            "y",  # requires scripts
            "",   # template default
            "",   # inputs
            "",   # outputs
            "scan folder",
            "",   # end steps
            "test",
            "MIT",
            "all",
        ])

        with patch("builtins.input", lambda _: next(answers)):
            spec = run_interactive_interview()

        self.assertEqual(spec.name, "my-invalid-name")
        self.assertEqual(spec.template_family, "python-script")

    def test_full_beginner_journey_end_to_end(self) -> None:
        """Verify full first-use journey: doctor -> new -> validate -> install -> uninstall."""
        proj_dir = self.work_path / "project"
        proj_dir.mkdir(parents=True, exist_ok=True)

        # 1. Doctor check
        code = main(["doctor", "--guided", "--project", str(proj_dir)])
        self.assertEqual(code, 0)

        # 2. Scaffolding new skill
        out_dir = proj_dir / "my-skills"
        code = main(["new", "daily-standup-helper", "--output", str(out_dir)])
        self.assertEqual(code, 0)
        skill_dir = out_dir / "daily-standup-helper"
        self.assertTrue(skill_dir.exists())

        # 3. Validate skill
        code = main(["validate", str(skill_dir)])
        self.assertEqual(code, 0)

        # 4. Install skill to project scope (resolves to .agents/skills for cursor)
        code = main([
            "install",
            str(skill_dir),
            "--target", "cursor",
            "--scope", "project",
            "--project", str(proj_dir),
        ])
        self.assertEqual(code, 0)
        installed_dest = proj_dir / ".agents" / "skills" / "daily-standup-helper"
        self.assertTrue(installed_dest.exists())
        self.assertTrue((installed_dest / "SKILL.md").exists())
        self.assertTrue((installed_dest / ".skillfactory" / "manifest.json").exists())

        # 5. Attempt duplicate install without --force (should fail cleanly with 3-part error)
        err_buf = io.StringIO()
        with patch("sys.stderr", err_buf):
            code_dup = main([
                "install",
                str(skill_dir),
                "--target", "cursor",
                "--scope", "project",
                "--project", str(proj_dir),
            ])
        self.assertEqual(code_dup, 1)
        self.assertIn("What happened:", err_buf.getvalue())
        self.assertIn("What to do next:", err_buf.getvalue())

        # 6. Uninstall cleanly
        code_uninst = main(["uninstall", "daily-standup-helper"])
        self.assertEqual(code_uninst, 0)
        self.assertFalse(installed_dest.exists())


if __name__ == "__main__":
    unittest.main()
