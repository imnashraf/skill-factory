"""Unit and integration tests for interview engine and batch mode (T2.02, T2.03, AC2.02, AC2.03)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillfactory.cli import main
from skillfactory.interview import derive_skill_name, load_batch_answers
from skillfactory.validator import validate_skill


class InterviewTests(unittest.TestCase):
    def test_derive_skill_name(self):
        """Test name derivation from problem statements (FR-NL-04)."""
        # Normal sentence
        name1 = derive_skill_name("Compare two Excel spreadsheets and report differences")
        self.assertEqual(name1, "compare-two-excel-spreadsheets-and-report-differences")

        # Special characters, punctuation
        name2 = derive_skill_name("Convert JSON -> YAML & XML (v2.0)!")
        self.assertEqual(name2, "convert-json-yaml-xml-v2-0")

        # Windows reserved name
        name3 = derive_skill_name("CON")
        self.assertEqual(name3, "con-skill")

        # Platform reserved name
        name4 = derive_skill_name("synced")
        self.assertEqual(name4, "synced-skill")

        # Very long sentence (> 64 chars)
        long_sentence = "A very long problem description that should be truncated to sixty four characters maximum length"
        name5 = derive_skill_name(long_sentence)
        self.assertLessEqual(len(name5), 64)
        self.assertFalse(name5.endswith("-"))

    def test_batch_answers_cli_execution(self):
        """AC2.03: Batch interview --answers answers.json runs non-interactively."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            answers = {
                "problem": "Convert markdown documentation to styled HTML",
                "name": "md-to-html-batch",
                "description": "Convert markdown files to styled HTML reports with custom CSS.",
                "template_family": "file-transform",
                "inputs": ["source.md"],
                "outputs": ["dest.html"],
                "steps": [
                    "Read source markdown file",
                    "Parse markdown into HTML AST",
                    "Apply standard CSS stylesheet",
                    "Write output HTML file",
                ],
                "author": "Test Author",
                "license": "MIT",
            }
            answers_file = tmp_path / "answers.json"
            answers_file.write_text(json.dumps(answers, indent=2), encoding="utf-8")

            # Run CLI interview in batch mode
            exit_code = main([
                "interview",
                "--answers", str(answers_file),
                "--output", str(tmp_path),
            ])
            self.assertEqual(exit_code, 0)

            # Verify generated skill
            skill_dir = tmp_path / "md-to-html-batch"
            self.assertTrue(skill_dir.exists())
            self.assertTrue((skill_dir / "SKILL.md").exists())
            self.assertTrue((skill_dir / "scripts" / "main.py").exists())

            # Validate generated skill
            val_result = validate_skill(skill_dir)
            self.assertTrue(val_result.is_valid, f"Validation errors: {val_result.errors}")

    def test_batch_spec_only_mode(self):
        """Test --spec-only flag writing only the spec JSON file."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            answers = {
                "problem": "Audit Dockerfiles for security best practices",
                "name": "docker-security-audit",
                "description": "Inspect Dockerfiles and report vulnerabilities.",
                "template_family": "checklist-review",
            }
            answers_file = tmp_path / "answers.json"
            answers_file.write_text(json.dumps(answers), encoding="utf-8")

            exit_code = main([
                "interview",
                "--answers", str(answers_file),
                "--output", str(tmp_path),
                "--spec-only",
            ])
            self.assertEqual(exit_code, 0)

            spec_file = tmp_path / "docker-security-audit-spec.json"
            self.assertTrue(spec_file.exists())
            spec_data = json.loads(spec_file.read_text(encoding="utf-8"))
            self.assertEqual(spec_data["name"], "docker-security-audit")
            self.assertEqual(spec_data["template_family"], "checklist-review")


if __name__ == "__main__":
    unittest.main()
