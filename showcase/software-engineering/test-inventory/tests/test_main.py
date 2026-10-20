#!/usr/bin/env python3
"""Automated unit and regression tests for Test Inventory Analyzer (Demo 05)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
import unittest

_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from main import (
    analyze_test_inventory,
    format_markdown_report,
    infer_module_name,
)


class TestTestInventoryAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        self.demo_dir = Path(__file__).resolve().parent.parent
        self.inputs_dir = self.demo_dir / "sample-inputs"
        self.expected_dir = self.demo_dir / "expected-outputs"

    def test_infer_module_name(self) -> None:
        """Verify module naming conventions."""
        self.assertEqual(infer_module_name("test_auth.py"), "auth")
        self.assertEqual(infer_module_name("billing_test.py"), "billing")
        self.assertEqual(infer_module_name("custom_suite.py"), "custom_suite")

    def test_valid_repo_complete_mapping(self) -> None:
        """Verify valid synthetic repo has 100% test coverage mapping."""
        repo_path = self.inputs_dir / "valid_repo"
        data = analyze_test_inventory(repo_path, src_folder="src", tests_folder="tests")

        self.assertEqual(data["test_files_count"], 3)
        self.assertEqual(data["total_test_cases"], 4)
        self.assertEqual(data["source_modules_count"], 3)
        self.assertEqual(data["tested_modules_count"], 3)
        self.assertEqual(data["untested_modules_count"], 0)
        self.assertEqual(data["duplicate_tests_count"], 0)
        self.assertEqual(data["total_skipped_tests"], 0)

    def test_edge_case_untested_modules_and_duplicates(self) -> None:
        """Verify detection of untested modules, duplicate tests, and skipped suites."""
        repo_path = self.inputs_dir / "edge_case_repo"
        data = analyze_test_inventory(repo_path, src_folder="src", tests_folder="tests")

        self.assertEqual(data["test_files_count"], 2)
        self.assertEqual(data["total_test_cases"], 4)
        self.assertEqual(data["total_skipped_tests"], 1)
        self.assertEqual(data["source_modules_count"], 4)
        self.assertEqual(data["untested_modules_count"], 2)

        untested_names = [um["module_name"] for um in data["untested_modules"]]
        self.assertIn("analytics", untested_names)
        self.assertIn("reporting", untested_names)

        self.assertEqual(data["duplicate_tests_count"], 1)
        self.assertEqual(data["duplicate_tests"][0]["test_name"], "test_token_validation")

    def test_markdown_report_matches_expected(self) -> None:
        """Verify markdown report matches expected golden report."""
        repo_path = self.inputs_dir / "valid_repo"
        expected_md = (self.expected_dir / "valid_inventory_report.md").read_text(encoding="utf-8")

        data = analyze_test_inventory(repo_path, src_folder="src", tests_folder="tests")
        rendered_md = format_markdown_report(data)

        self.assertEqual(rendered_md.strip(), expected_md.strip())


if __name__ == "__main__":
    unittest.main()
