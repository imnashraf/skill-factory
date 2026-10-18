"""Unit tests for skillfactory/validator.py (T1.07, AC1.07, verifying DEF-02)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillfactory.validator import validate_skill, validate_skill_name
from skillfactory.yaml_util import dump_frontmatter


class ValidatorTests(unittest.TestCase):
    def test_validate_skill_name_valid(self):
        self.assertEqual(validate_skill_name("my-skill"), [])
        self.assertEqual(validate_skill_name("pdf2text"), [])
        self.assertEqual(validate_skill_name("test-123-abc"), [])

    def test_def02_windows_reserved_names(self):
        """DEF-02: Ensure Windows reserved names are rejected."""
        reserved = ["con", "prn", "aux", "nul", "com1", "com9", "lpt1", "lpt9"]
        for name in reserved:
            errors = validate_skill_name(name)
            self.assertTrue(
                any("reserved by Windows" in e for e in errors),
                f"Expected Windows reserved error for {name}",
            )

    def test_def02_platform_reserved_names(self):
        """DEF-02: Ensure platform reserved names are rejected."""
        errors = validate_skill_name("synced")
        self.assertTrue(any("reserved by target platforms" in e for e in errors))

    def test_validate_valid_skill_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "good-skill"
            skill_dir.mkdir()
            frontmatter = dump_frontmatter({
                "name": "good-skill",
                "description": "A well-formed test skill.",
            })
            (skill_dir / "SKILL.md").write_text(frontmatter + "\n# good-skill\n\nContent.\n", encoding="utf-8")
            res = validate_skill(skill_dir)
            self.assertTrue(res.is_valid, f"Validation errors: {res.errors}")
            self.assertEqual(res.errors, [])

    def test_validate_missing_skill_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "empty-skill"
            skill_dir.mkdir()
            res = validate_skill(skill_dir)
            self.assertFalse(res.is_valid)
            self.assertTrue(any("Missing required 'SKILL.md'" in e for e in res.errors))

    def test_validate_mismatched_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "folder-name"
            skill_dir.mkdir()
            frontmatter = dump_frontmatter({
                "name": "other-name",
                "description": "Mismatched name skill",
            })
            (skill_dir / "SKILL.md").write_text(frontmatter + "\n# Test\n", encoding="utf-8")
            res = validate_skill(skill_dir)
            self.assertFalse(res.is_valid)
            self.assertTrue(any("must match parent directory" in e for e in res.errors))

    def test_validate_broken_relative_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "broken-link-skill"
            skill_dir.mkdir()
            frontmatter = dump_frontmatter({
                "name": "broken-link-skill",
                "description": "Skill with broken link",
            })
            body = "\n# Skill\n\nSee [the missing script](scripts/missing.py) for details.\n"
            (skill_dir / "SKILL.md").write_text(frontmatter + body, encoding="utf-8")
            res = validate_skill(skill_dir)
            self.assertFalse(res.is_valid)
            self.assertTrue(any("Referenced file does not exist" in e for e in res.errors))

    def test_validate_absolute_path_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "abs-link-skill"
            skill_dir.mkdir()
            frontmatter = dump_frontmatter({
                "name": "abs-link-skill",
                "description": "Skill with absolute path link",
            })
            body = "\n# Skill\n\nSee [bad path](/Users/foo/bar.txt) for details.\n"
            (skill_dir / "SKILL.md").write_text(frontmatter + body, encoding="utf-8")
            res = validate_skill(skill_dir)
            self.assertFalse(res.is_valid)
            self.assertTrue(any("Hardcoded absolute path" in e for e in res.errors))


if __name__ == "__main__":
    unittest.main()
