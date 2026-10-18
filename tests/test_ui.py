"""Unit and integration tests for beginner experience and UI utilities (Phase 7, AC7.01..AC7.06)."""
from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skillfactory.cli import cmd_interactive_top_menu, main
from skillfactory.errors import SkillFactoryUserError, format_error
from skillfactory.ui_util import (
    colorize,
    format_box,
    format_header,
    format_msg,
    strip_ansi,
    supports_color,
)


class UiAndBeginnerExperienceTests(unittest.TestCase):
    def test_ac7_04_no_color_support(self):
        """AC7.04: Verify NO_COLOR=1 strips all ANSI codes while preserving semantic tags."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}, clear=False):
            self.assertFalse(supports_color())
            out_ok = format_msg("OK", "Operation successful")
            self.assertIn("[OK] Operation successful", out_ok)
            self.assertEqual(strip_ansi(out_ok), out_ok)
            self.assertNotIn("\033[", out_ok)

            out_err = format_msg("ERROR", "Something broke")
            self.assertIn("[ERROR] Something broke", out_err)
            self.assertNotIn("\033[", out_err)

    def test_ac7_04_term_dumb_disables_color(self):
        """AC7.04: TERM=dumb disables ANSI color codes."""
        with patch.dict(os.environ, {"TERM": "dumb"}, clear=True):
            self.assertFalse(supports_color())
            c_text = colorize("32", "hello")
            self.assertEqual(c_text, "hello")

    def test_ac7_04_semantic_tags_always_present(self):
        """AC7.04: Tags [OK], [ERROR], [WARN], [INFO] are always present regardless of color."""
        for level in ("OK", "ERROR", "WARN", "INFO"):
            out = format_msg(level, "Testing semantic signal")
            self.assertIn(f"[{level}] Testing semantic signal", strip_ansi(out))

    def test_ac7_02_three_part_error_formatting(self):
        """AC7.02: Error messages explain What, Why, and Next without raw stack traces."""
        err = SkillFactoryUserError(
            what="Failed to extract skill archive 'corrupt.zip'.",
            why="The archive is corrupted or contains an invalid central directory header.",
            next_step="Re-download the zip archive or regenerate it using 'skillfactory export'.",
            code="ERR_CORRUPT_ARCHIVE",
        )
        rendered = format_error(err)
        self.assertIn("What happened:", rendered)
        self.assertIn("Why it happened:", rendered)
        self.assertIn("What to do next:", rendered)
        self.assertIn("corrupt.zip", rendered)
        self.assertIn("ERR_CORRUPT_ARCHIVE", rendered)
        # Verify no raw traceback artifact in rendered message
        self.assertNotIn("Traceback (most recent call last):", rendered)

    def test_ac7_01_interactive_top_menu_display_and_exit(self):
        """AC7.01: Interactive menu displays numbered options [0-9] and exits cleanly on choice 0."""
        # Mock user entering '0'
        with patch("builtins.input", return_value="0"), patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            exit_code = cmd_interactive_top_menu()
            self.assertEqual(exit_code, 0)
            output = fake_out.getvalue()
            self.assertIn("Skill Factory — Agent Skills Generator & Manager", output)
            self.assertIn("[1] Create a new skill", output)
            self.assertIn("[2] Search local skill library", output)
            self.assertIn("[3] Validate an existing skill folder", output)
            self.assertIn("[4] Run skill automated tests", output)
            self.assertIn("[5] Evaluate skill quality score (0–100)", output)
            self.assertIn("[6] Scan skill for secrets and safety issues", output)
            self.assertIn("[7] Platform health doctor", output)
            self.assertIn("[8] Install a skill into an AI tool", output)
            self.assertIn("[9] List installed skills", output)
            self.assertIn("[0] Exit", output)
            self.assertIn("Goodbye!", output)

    def test_ac7_01_cli_menu_command(self):
        """AC7.01: Invoking 'skillfactory menu' runs interactive top menu."""
        with patch("builtins.input", return_value="0"), patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            exit_code = main(["menu"])
            self.assertEqual(exit_code, 0)
            self.assertIn("[1] Create a new skill", fake_out.getvalue())

    def test_ac7_03_quickstart_guides_exist_and_complete(self):
        """AC7.03: Quickstart guides exist for macOS, Windows, and Linux with required sections."""
        repo_root = Path(__file__).resolve().parent.parent
        guides = {
            "macos": repo_root / "docs" / "quickstart" / "macos.md",
            "windows": repo_root / "docs" / "quickstart" / "windows.md",
            "linux": repo_root / "docs" / "quickstart" / "linux.md",
        }
        for os_name, path in guides.items():
            self.assertTrue(path.exists(), f"Quickstart guide missing for {os_name}: {path}")
            content = path.read_text(encoding="utf-8")
            self.assertIn("Prerequisites", content)
            self.assertIn("Create Your First Skill", content)
            self.assertIn("Test", content)
            self.assertIn("Install", content)

    def test_ac7_05_beginner_glossary_covers_core_concepts(self):
        """AC7.05: Glossary covers >= 15 core concepts in simple language."""
        repo_root = Path(__file__).resolve().parent.parent
        glossary_path = repo_root / "docs" / "glossary.md"
        self.assertTrue(glossary_path.exists())
        content = glossary_path.read_text(encoding="utf-8")

        expected_concepts = [
            "Agent Skill",
            "SKILL.md",
            "YAML Frontmatter",
            "Progressive Disclosure",
            "Host-AI Mode",
            "Offline Mode",
            "SkillSpec",
            "Template Family",
            "Platform Adapter",
            "Discovery Path",
            "Project Scope",
            "Manifest",
            "Subprocess Test Runner",
            "AST Safety Scanner",
            "Quality Evaluation Score",
            "Portable Zip Package",
            "Rollback",
        ]
        self.assertGreaterEqual(len(expected_concepts), 15)
        for concept in expected_concepts:
            self.assertIn(concept, content, f"Glossary is missing definition for: {concept}")

    def test_ac7_06_beginner_e2e_workflow(self):
        """AC7.06: First-time beginner usability flow succeeds cleanly end-to-end."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Step 1: Create skill via non-interactive new
            rc_new = main([
                "new",
                "--name", "beginner-test-skill",
                "--description", "A beginner-friendly demonstration skill.",
                "--template", "checklist-review",
                "--output", str(tmp_path),
            ])
            self.assertEqual(rc_new, 0)
            skill_dir = tmp_path / "beginner-test-skill"

            # Step 2: Validate
            rc_val = main(["validate", str(skill_dir)])
            self.assertEqual(rc_val, 0)

            # Step 3: Test
            rc_test = main(["test", str(skill_dir)])
            self.assertEqual(rc_test, 0)

            # Step 4: Scan
            rc_scan = main(["scan", str(skill_dir)])
            self.assertEqual(rc_scan, 0)

            # Step 5: Eval
            rc_eval = main(["eval", str(skill_dir)])
            self.assertEqual(rc_eval, 0)


if __name__ == "__main__":
    unittest.main()
