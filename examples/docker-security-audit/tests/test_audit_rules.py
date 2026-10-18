"""Structural and rule tests for docker-security-audit reference skill."""
import unittest
from pathlib import Path


class DockerSecurityAuditTests(unittest.TestCase):
    def setUp(self):
        self.skill_dir = Path(__file__).resolve().parent.parent

    def test_required_files_present(self):
        self.assertTrue((self.skill_dir / "SKILL.md").exists())
        self.assertTrue((self.skill_dir / "README.md").exists())
        self.assertTrue((self.skill_dir / "LICENSE").exists())

    def test_references_and_examples_exist(self):
        ref_dir = self.skill_dir / "references"
        ex_dir = self.skill_dir / "examples"
        self.assertTrue(ref_dir.is_dir() and any(ref_dir.iterdir()))
        self.assertTrue(ex_dir.is_dir() and any(ex_dir.iterdir()))

    def test_checklist_rules_structure(self):
        skill_md = (self.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("checklist", skill_md.lower())
        self.assertIn("docker", skill_md.lower())


if __name__ == "__main__":
    unittest.main()
