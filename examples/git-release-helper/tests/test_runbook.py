"""Structural and workflow tests for git-release-helper reference skill."""
import unittest
from pathlib import Path


class GitReleaseHelperTests(unittest.TestCase):
    def setUp(self):
        self.skill_dir = Path(__file__).resolve().parent.parent

    def test_required_files_present(self):
        self.assertTrue((self.skill_dir / "SKILL.md").exists())
        self.assertTrue((self.skill_dir / "README.md").exists())
        self.assertTrue((self.skill_dir / "LICENSE").exists())

    def test_runbook_references_exist(self):
        ref_dir = self.skill_dir / "references"
        ex_dir = self.skill_dir / "examples"
        self.assertTrue(ref_dir.is_dir() and any(ref_dir.iterdir()))
        self.assertTrue(ex_dir.is_dir() and any(ex_dir.iterdir()))

    def test_runbook_content_has_release_phases(self):
        skill_md = (self.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("release", skill_md.lower())
        self.assertIn("version", skill_md.lower())


if __name__ == "__main__":
    unittest.main()
