"""Tests for paths, encodings, and atomic rollback (EC-04, EC-11, AC1.04)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skillfactory.core import generate_skill
from skillfactory.spec import SkillSpec
from skillfactory.validator import validate_skill


class PathsAndEncodingTests(unittest.TestCase):
    def test_unicode_and_emojis(self):
        """EC-04: Unicode characters, accents, and emojis in description."""
        with tempfile.TemporaryDirectory() as tmp:
            spec = SkillSpec(
                name="unicode-skill",
                description="Café ☕ diff tool with emojis 🚀 and 技能 CJK text.",
                template_family="python-script",
            )
            res = generate_skill(spec, Path(tmp))
            skill_md = res.target_path / "SKILL.md"
            self.assertTrue(skill_md.exists())
            content = skill_md.read_text(encoding="utf-8")
            self.assertIn("Café ☕", content)
            self.assertIn("🚀", content)
            self.assertIn("技能", content)

            val = validate_skill(res.target_path)
            self.assertTrue(val.is_valid, f"Validation errors: {val.errors}")

    def test_spaces_in_destination_path(self):
        """EC-11: Destination path containing spaces."""
        with tempfile.TemporaryDirectory() as tmp:
            spaced_dir = Path(tmp) / "Folder With Spaces" / "Sub Dir"
            spaced_dir.mkdir(parents=True)

            spec = SkillSpec(
                name="spaced-skill",
                description="Testing spaces in destination directory path.",
                template_family="instructions-only",
            )
            res = generate_skill(spec, spaced_dir)
            self.assertTrue(res.target_path.exists())
            val = validate_skill(res.target_path)
            self.assertTrue(val.is_valid, f"Validation errors: {val.errors}")

    def test_atomic_rollback_on_failure(self):
        """AC1.04, EC-15: Fault injection leaves 0 orphan files in target directory."""
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp)
            spec = SkillSpec(
                name="faulty-skill",
                description="Testing fault injection during atomic generation.",
                template_family="python-script",
            )

            target_path = out_root / "faulty-skill"

            # Inject a failure inside write_manifest
            with patch("skillfactory.core.write_manifest", side_effect=IOError("Simulated disk full")):
                with self.assertRaises(IOError):
                    generate_skill(spec, out_root)

            # Target directory must NOT exist
            self.assertFalse(target_path.exists(), "Target directory should not exist after failure")

            # Check that no temporary staging folders (.tmp-*) remain in out_root
            tmp_folders = list(out_root.glob(".tmp-*"))
            self.assertEqual(tmp_folders, [], f"Expected 0 staging folders left behind, found {tmp_folders}")


if __name__ == "__main__":
    unittest.main()
