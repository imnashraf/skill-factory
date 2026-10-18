"""Tests for paths, encodings, and atomic rollback (EC-04, EC-11, AC1.04, AC8.02)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skillfactory.cli import main
from skillfactory.core import generate_skill
from skillfactory.packaging import export_skill_to_zip, import_skill_from_zip
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

    def test_ac8_02_full_workflow_in_path_with_spaces_and_emojis(self):
        """AC8.02: Full tool workflow functions in directory with spaces, emojis, and non-ASCII."""
        with tempfile.TemporaryDirectory() as tmp:
            weird_root = Path(tmp) / "work space 🚀 📁" / "测试 技能"
            weird_root.mkdir(parents=True, exist_ok=True)

            # 1. New
            rc_new = main([
                "new",
                "--name", "space-emoji-skill",
                "--description", "Handles weird folder names with spaces and emojis 🚀.",
                "--template", "checklist-review",
                "--output", str(weird_root),
            ])
            self.assertEqual(rc_new, 0)
            skill_dir = weird_root / "space-emoji-skill"
            self.assertTrue(skill_dir.exists())

            # 2. Validate
            self.assertEqual(main(["validate", str(skill_dir)]), 0)

            # 3. Test
            self.assertEqual(main(["test", str(skill_dir)]), 0)

            # 4. Scan
            self.assertEqual(main(["scan", str(skill_dir)]), 0)

            # 5. Eval
            self.assertEqual(main(["eval", str(skill_dir)]), 0)

            # 6. Export to zip inside weird path
            zip_dest = weird_root / "export archive 📦.zip"
            export_res = export_skill_to_zip(skill_dir, zip_dest)
            self.assertTrue(export_res.zip_path.exists())

            # 7. Import to another weird path
            import_dest = Path(tmp) / "import target 🎯"
            import_res = import_skill_from_zip(zip_dest, import_dest)
            self.assertTrue((import_dest / "space-emoji-skill").exists())

    def test_ac8_02_deeply_nested_long_path(self):
        """AC8.02: Resilient to deep directory structures (> 260 character path simulation)."""
        with tempfile.TemporaryDirectory() as tmp:
            # Build deeply nested folder
            sub_folders = ["level_" + str(i).zfill(4) + "_segment" for i in range(12)]
            deep_root = Path(tmp).joinpath(*sub_folders)
            deep_root.mkdir(parents=True, exist_ok=True)
            self.assertGreater(len(str(deep_root)), 200)

            spec = SkillSpec(
                name="deep-path-skill",
                description="Testing deep path resilience.",
                template_family="instructions-only",
            )
            res = generate_skill(spec, deep_root)
            self.assertTrue(res.target_path.exists())
            self.assertTrue((res.target_path / "SKILL.md").exists())
            val = validate_skill(res.target_path)
            self.assertTrue(val.is_valid)


if __name__ == "__main__":
    unittest.main()
