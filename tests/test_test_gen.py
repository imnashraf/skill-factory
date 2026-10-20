"""Unit tests for Behavioral Test Generator (Phase 16, Workstream 16C)."""
from __future__ import annotations

import ast
import unittest

from skillfactory.ai.requirements import parse_natural_language_requirement
from skillfactory.ai.test_gen import generate_behavioral_tests


class TestTestGenerator(unittest.TestCase):
    """Validates automated synthesis of behavioral unit tests."""

    def test_generate_behavioral_tests_ast_validity(self):
        req = "Create a skill that compares two Excel files and highlights differences."
        spec = parse_natural_language_requirement(req, preferred_name="excel-comparison")

        code = generate_behavioral_tests(spec)

        # 1. Must parse cleanly without syntax errors
        tree = ast.parse(code)
        self.assertIsInstance(tree, ast.Module)

        # 2. Must contain TestCase class
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        self.assertTrue(any(c.name == "TestExcelComparisonBehavior" for c in classes))

        # 3. Must contain test methods mapped to acceptance criteria
        methods = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        self.assertTrue(any(m.startswith("test_ac_1") for m in methods))
        self.assertTrue(any(m.startswith("test_ac_2") for m in methods))
        self.assertTrue(any("security" in m for m in methods))

    def test_traceability_to_all_acceptance_criteria(self):
        req = "Create a skill that checks invoice discrepancies."
        spec = parse_natural_language_requirement(req, preferred_name="invoice-checker")

        code = generate_behavioral_tests(spec)
        for idx in range(1, len(spec.acceptance_criteria) + 1):
            self.assertIn(f"test_ac_{idx}", code)


if __name__ == "__main__":
    unittest.main()
