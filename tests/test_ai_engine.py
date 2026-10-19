"""Unit and integration tests for AI-Assisted Skill Creation (Phase 15, Workstream E)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillfactory.ai.engine import AIAssistedEngine, derive_spec_from_requirement
from skillfactory.ai.mock_provider import MockAIProvider
from skillfactory.ai.ollama import OllamaProvider
from skillfactory.ai.openai_compat import OpenAICompatibleProvider


class AIAssistedEngineTests(unittest.TestCase):
    def test_derive_spec_from_requirement(self):
        req = "Create a skill that parses invoice tables and flags discrepancies"
        spec = derive_spec_from_requirement(req)
        self.assertEqual(spec.name, "parses-invoice-tables")
        self.assertEqual(spec.template_family, "python-script")
        self.assertEqual(spec.license, "MIT")

        # Preferred name override
        spec2 = derive_spec_from_requirement(req, preferred_name="custom-invoice-checker")
        self.assertEqual(spec2.name, "custom-invoice-checker")

    def test_end_to_end_synthesis_passing(self):
        provider = MockAIProvider(mode="passing")
        engine = AIAssistedEngine(provider=provider, max_repairs=3)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            req = "Summarize meeting minutes and extract action items"
            res = engine.build_skill(req, output_dir=tmp_path, preferred_name="meeting-summarizer")

            self.assertEqual(res.status, "success")
            self.assertEqual(res.skill_name, "meeting-summarizer")
            self.assertTrue(res.safety_clean)
            self.assertEqual(res.repair_count, 0)
            self.assertGreaterEqual(res.eval_score, 90)
            self.assertEqual(res.grade, "Grade A")

            created_dir = Path(res.output_dir)
            self.assertTrue((created_dir / "SKILL.md").is_file())
            self.assertTrue((created_dir / "scripts" / "main.py").is_file())
            self.assertTrue((created_dir / "tests" / "test_main.py").is_file())
            self.assertTrue((created_dir / ".skillfactory" / "manifest.json").is_file())

    def test_self_repair_loop_recovery(self):
        # Starts with broken test, repairs it
        provider = MockAIProvider(mode="repair_needed")
        engine = AIAssistedEngine(provider=provider, max_repairs=3)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            req = "Process numbers with double multiplier"
            res = engine.build_skill(req, output_dir=tmp_path, preferred_name="multiplier-skill")

            self.assertEqual(res.status, "success")
            self.assertEqual(res.repair_count, 1)
            self.assertTrue(res.safety_clean)
            self.assertGreaterEqual(res.eval_score, 85)

    def test_ast_safety_interceptor_blocks_dangerous_code(self):
        # Provider outputs eval(), AST scanner must intercept before execution
        provider = MockAIProvider(mode="dangerous")
        engine = AIAssistedEngine(provider=provider, max_repairs=3)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            req = "Execute dynamic user expressions"
            res = engine.build_skill(req, output_dir=tmp_path, preferred_name="evil-skill")

            self.assertEqual(res.status, "safety_rejected")
            self.assertFalse(res.safety_clean)
            self.assertEqual(res.eval_score, 0)
            self.assertIn("AST Safety Scanner", res.explanation)
            self.assertIn("AST001", res.explanation)

    def test_provider_availability_contracts(self):
        ollama = OllamaProvider(base_url="http://127.0.0.1:9999")
        self.assertEqual(ollama.provider_id, "ollama")
        # Port 9999 is inactive, should report False safely without raising
        self.assertFalse(ollama.is_available())

        openai_compat = OpenAICompatibleProvider(base_url="http://127.0.0.1:9999/v1")
        self.assertEqual(openai_compat.provider_id, "openai-compat")
        self.assertFalse(openai_compat.is_available())


if __name__ == "__main__":
    unittest.main()
