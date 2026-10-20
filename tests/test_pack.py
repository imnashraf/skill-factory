"""Unit tests for Phase 15 Skill Pack subsystem."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillfactory.errors import SkillFactoryError
from skillfactory.pack import (
    get_pack,
    install_pack,
    load_packs,
    uninstall_pack,
    verify_pack,
)


class SkillPackTests(unittest.TestCase):
    def test_load_all_packs(self):
        packs = load_packs()
        self.assertEqual(len(packs), 5)
        pack_ids = {p.id for p in packs}
        expected = {
            "office-productivity",
            "finance-erp",
            "hr-workforce",
            "project-management",
            "developer-security",
        }
        self.assertEqual(pack_ids, expected)

    def test_get_pack_by_id_or_name(self):
        p1 = get_pack("finance-erp")
        self.assertIsNotNone(p1)
        self.assertEqual(p1.name, "Finance & ERP Pack")

        p2 = get_pack("Finance & ERP Pack")
        self.assertIsNotNone(p2)
        self.assertEqual(p2.id, "finance-erp")

        p_missing = get_pack("nonexistent-pack")
        self.assertIsNone(p_missing)

    def test_verify_packs(self):
        # Verify office-productivity pack
        res = verify_pack("office-productivity")
        self.assertTrue(res["all_clean"])
        self.assertEqual(res["total_skills"], 5)
        for s in res["results"]:
            self.assertTrue(s["valid"], f"Skill {s['skill']} was not valid")
            self.assertTrue(s["tests_passed"], f"Skill {s['skill']} tests failed")
            self.assertTrue(s["safety_clean"], f"Skill {s['skill']} safety not clean")

    def test_install_and_uninstall_pack_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp_proj:
            proj_dir = Path(tmp_proj)
            # Install finance-erp pack into claude-code
            install_res = install_pack(
                pack_id="finance-erp",
                target_platform="claude-code",
                scope="project",
                project_dir=proj_dir,
                yes=True,
            )
            self.assertEqual(install_res["status"], "success")
            self.assertEqual(install_res["installed_count"], 2)

            # Check that skills exist in .claude/skills/
            claude_skills = proj_dir / ".claude" / "skills"
            self.assertTrue((claude_skills / "financial-variance-analyzer").is_dir())
            self.assertTrue((claude_skills / "invoice-reconciliation").is_dir())

            # Uninstall pack
            uninst_res = uninstall_pack(
                pack_id="finance-erp",
                target_platform="claude-code",
                scope="project",
                project_dir=proj_dir,
            )
            self.assertEqual(uninst_res["status"], "success")
            self.assertEqual(uninst_res["uninstalled_count"], 2)
            self.assertFalse((claude_skills / "financial-variance-analyzer").exists())
            self.assertFalse((claude_skills / "invoice-reconciliation").exists())


if __name__ == "__main__":
    unittest.main()
