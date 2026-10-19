"""Unit tests for Community Submission Validation & Quarantine (Phase 17, Workstream 17D)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_submission import validate_submission
from skillfactory.core import generate_skill
from skillfactory.manifest import create_manifest, write_manifest
from skillfactory.spec import SkillSpec


class TestSubmissionValidation(unittest.TestCase):
    """Validates community skill screening under quarantine."""

    def test_clean_submission_passes_static_screening(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec = SkillSpec(
                name="community-clean-tool",
                description="Community contributed clean tool for text processing.",
                template_family="python-script",
                author="Community Contributor",
            )
            res = generate_skill(spec, tmp_path)
            skill_dir = res.target_path

            code, report_md = validate_submission(skill_dir, allow_untrusted_exec=False)
            self.assertEqual(code, 0, f"Clean skill should pass static screening: {report_md}")
            self.assertIn("AUTOMATED STATIC SCREENING PASSED", report_md)
            self.assertIn("Quarantine Barrier Enforced", report_md)

    def test_tampered_manifest_fails_screening(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec = SkillSpec(
                name="tampered-skill",
                description="Skill with modified file that does not match manifest.",
                template_family="python-script",
            )
            res = generate_skill(spec, tmp_path)
            skill_dir = res.target_path

            # Tamper with SKILL.md without updating manifest
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(skill_md.read_text(encoding="utf-8") + "\n# Tampered", encoding="utf-8")

            code, report_md = validate_submission(skill_dir, allow_untrusted_exec=False)
            self.assertEqual(code, 1, "Tampered skill must fail manifest check")
            self.assertIn("Manifest Integrity**: FAIL", report_md)
            self.assertIn("AUTOMATED SCREENING FAILED", report_md)

    def test_dangerous_ast_injection_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec = SkillSpec(
                name="malicious-skill",
                description="Skill containing forbidden eval execution.",
                template_family="python-script",
            )
            res = generate_skill(spec, tmp_path)
            skill_dir = res.target_path

            # Inject dangerous eval into scripts/main.py
            script_path = skill_dir / "scripts" / "main.py"
            script_path.write_text("import sys\neval(sys.argv[1])\n", encoding="utf-8")
            # Update manifest so manifest passes, but AST scan catches it
            m = create_manifest(skill_dir, spec, spec.template_family)
            write_manifest(skill_dir, m)

            code, report_md = validate_submission(skill_dir, allow_untrusted_exec=False)
            self.assertEqual(code, 1, "Dangerous AST must be rejected")
            self.assertIn("AST Safety Scan**: FAIL", report_md)
            self.assertIn("AST001", report_md)


if __name__ == "__main__":
    unittest.main()
