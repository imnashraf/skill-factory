"""Unit tests for Functional Evaluator and Non-AI Fallback Engine (Phase 16, Workstream 16D)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillfactory.ai.engine import AIAssistedEngine
from skillfactory.ai.evaluator import (
    audit_functional_correctness,
    generate_non_ai_implementation,
)
from skillfactory.ai.requirements import parse_natural_language_requirement
from skillfactory.ai.test_gen import generate_behavioral_tests
from skillfactory.core import generate_skill
from skillfactory.manifest import create_manifest, write_manifest


class TestEvaluatorAndFallback(unittest.TestCase):
    """Validates independent functional evaluation and deterministic fallback."""

    def test_generate_non_ai_implementation_diff(self):
        req = "Create a skill that compares two Excel files and highlights differences."
        spec = parse_natural_language_requirement(req, preferred_name="excel-diff")
        script = generate_non_ai_implementation(spec)

        self.assertIn("Tabular File Comparison", script)
        self.assertIn("diffs", script)
        self.assertIn("Path traversal", script)

    def test_non_ai_fallback_end_to_end_in_engine(self):
        engine = AIAssistedEngine(provider=None)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            req = "Create a skill that reviews project RAID logs."
            res = engine.build_skill(
                requirement=req,
                output_dir=tmp_path,
                preferred_name="raid-audit-tool",
                force_non_ai=True,
            )

            self.assertEqual(res.status, "fallback_success")
            self.assertEqual(res.skill_name, "raid-audit-tool")
            self.assertTrue(res.safety_clean)
            self.assertGreaterEqual(res.eval_score, 85)
            self.assertIn("Fallback Engine", res.explanation)

            created = Path(res.output_dir)
            self.assertTrue((created / "scripts" / "main.py").is_file())
            self.assertTrue((created / "tests" / "test_main.py").is_file())
            self.assertTrue((created / "references" / "spec.md").is_file())

            # Verify audit report
            self.assertIsNotNone(res.audit_report)
            self.assertEqual(res.audit_report["skill_name"], "raid-audit-tool")
            self.assertTrue(res.audit_report["security_clean"])
            self.assertTrue(res.audit_report["tests_passed"])
            self.assertGreaterEqual(res.audit_report["traceability_score"], 90)

    def test_audit_catches_missing_script(self):
        req = "Summarize meeting minutes"
        spec = parse_natural_language_requirement(req)

        with tempfile.TemporaryDirectory() as tmp:
            audit = audit_functional_correctness(Path(tmp), spec)
            self.assertFalse(audit.tests_passed)
            self.assertEqual(audit.grade, "Grade F")


if __name__ == "__main__":
    unittest.main()
