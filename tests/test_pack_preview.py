"""Unit tests for Skill Pack Preview, Lifecycle, and Conflict Detection (Phase 17, Workstream 17C)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillfactory.pack import get_pack, load_packs, preview_pack, update_pack


class TestPackPreviewAndLifecycle(unittest.TestCase):
    """Validates pack preview, conflict detection, and lifecycle operations."""

    def test_load_curated_packs(self) -> None:
        packs = load_packs()
        self.assertGreaterEqual(len(packs), 5)
        pack_ids = [p.id for p in packs]
        self.assertIn("office-productivity", pack_ids)
        self.assertIn("finance-erp", pack_ids)
        self.assertIn("developer-security", pack_ids)

    def test_preview_pack_no_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_proj:
            res = preview_pack(
                pack_id="office-productivity",
                target_platform="claude-code",
                scope="project",
                project_dir=Path(tmp_proj),
            )

            self.assertEqual(res["pack_id"], "office-productivity")
            self.assertEqual(res["target_platform"], "claude-code")
            self.assertFalse(res["conflicts_detected"])
            self.assertEqual(res["total_skills"], 5)
            self.assertEqual(len(res["skills"]), 5)

            for s in res["skills"]:
                self.assertFalse(s["conflict"])
                self.assertGreater(s["files_count"], 0)

    def test_preview_pack_with_conflict_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_proj:
            proj_dir = Path(tmp_proj)
            # Pre-create one of the skills in the target location
            target_claude_skill = proj_dir / ".claude" / "skills" / "excel-comparison"
            target_claude_skill.mkdir(parents=True, exist_ok=True)
            (target_claude_skill / "SKILL.md").write_text("pre-existing", encoding="utf-8")

            res = preview_pack(
                pack_id="office-productivity",
                target_platform="claude-code",
                scope="project",
                project_dir=proj_dir,
            )

            self.assertTrue(res["conflicts_detected"])
            excel_entry = next(s for s in res["skills"] if s["skill"] == "excel-comparison")
            self.assertTrue(excel_entry["conflict"])
            self.assertIsNotNone(excel_entry["conflict_path"])


if __name__ == "__main__":
    unittest.main()
