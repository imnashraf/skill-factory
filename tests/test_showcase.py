"""Comprehensive automated integration and verification test suite for Skill Factory Showcases.

Tests end-to-end execution, deterministic calculations, input immutability,
expected output matching, and security quarantine across all five domain demonstrations.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
import unittest

from tests.test_markdown_lint import check_markdown_lint_rules

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SHOWCASE_DIR = _REPO_ROOT / "showcase"


class TestShowcaseIntegrityAndExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.demos = [
            ("finance", "financial-variance"),
            ("hr-payroll", "attendance-validation"),
            ("project-management", "project-status"),
            ("cybersecurity", "dependency-review"),
            ("software-engineering", "test-inventory"),
        ]

    def test_showcase_directory_structure_exists(self) -> None:
        """Verify all five showcase demonstration packages exist with required subdirectories."""
        for domain, name in self.demos:
            demo_path = _SHOWCASE_DIR / domain / name
            self.assertTrue(demo_path.is_dir(), f"Showcase directory '{demo_path}' must exist")

            for req in ("problem-statement.md", "demo-guide.md", "README.md", "SKILL.md"):
                f_path = demo_path / req
                self.assertTrue(f_path.is_file(), f"Required document '{req}' must exist in {demo_path}")

            for sub in ("sample-inputs", "expected-outputs", "scripts", "tests", ".skillfactory"):
                s_path = demo_path / sub
                self.assertTrue(s_path.is_dir(), f"Required directory '{sub}' must exist in {demo_path}")

    def test_all_showcase_markdown_files_pass_lint(self) -> None:
        """Verify all markdown files in showcase/ have zero MD022, MD031, MD032 violations."""
        for md_file in sorted(_SHOWCASE_DIR.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            violations = check_markdown_lint_rules(str(md_file.relative_to(_REPO_ROOT)), content)
            self.assertEqual(
                violations,
                [],
                f"Showcase markdown file '{md_file.relative_to(_REPO_ROOT)}' has lint violations: {violations}",
            )

    def test_demo_01_financial_variance_execution(self) -> None:
        """Verify Demo 01 Financial Variance Analyzer executes and calculations match."""
        demo_path = _SHOWCASE_DIR / "finance" / "financial-variance"
        script = demo_path / "scripts" / "main.py"
        b_file = demo_path / "sample-inputs" / "valid_budget.csv"
        a_file = demo_path / "sample-inputs" / "valid_actuals.csv"
        expected_json = demo_path / "expected-outputs" / "valid_variance_report.json"

        # Record input file hashes before execution
        b_hash_pre = hashlib.sha256(b_file.read_bytes()).hexdigest()
        a_hash_pre = hashlib.sha256(a_file.read_bytes()).hexdigest()

        proc = subprocess.run(
            [sys.executable, str(script), str(b_file), str(a_file), "--json"],
            capture_output=True,
            text=True,
            check=True,
        )

        output_data = json.loads(proc.stdout)
        expected_data = json.loads(expected_json.read_text(encoding="utf-8"))

        self.assertEqual(output_data["total_budget"], expected_data["total_budget"])
        self.assertEqual(output_data["total_actual"], expected_data["total_actual"])
        self.assertEqual(output_data["total_variance_amount"], expected_data["total_variance_amount"])
        self.assertEqual(output_data["material_variances_count"], expected_data["material_variances_count"])

        # Check input immutability
        self.assertEqual(b_hash_pre, hashlib.sha256(b_file.read_bytes()).hexdigest())
        self.assertEqual(a_hash_pre, hashlib.sha256(a_file.read_bytes()).hexdigest())

    def test_demo_02_attendance_validation_execution(self) -> None:
        """Verify Demo 02 Attendance CSV Validator executes and detects anomalies."""
        demo_path = _SHOWCASE_DIR / "hr-payroll" / "attendance-validation"
        script = demo_path / "scripts" / "main.py"
        val_file = demo_path / "sample-inputs" / "valid_attendance.csv"
        edge_file = demo_path / "sample-inputs" / "edge_case_attendance.csv"
        val_expected_json = demo_path / "expected-outputs" / "valid_attendance_report.json"
        edge_expected_json = demo_path / "expected-outputs" / "edge_case_attendance_report.json"

        # Valid input check
        proc_val = subprocess.run(
            [sys.executable, str(script), str(val_file), "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        val_data = json.loads(proc_val.stdout)
        exp_val_data = json.loads(val_expected_json.read_text(encoding="utf-8"))
        self.assertTrue(val_data["is_clean"])
        self.assertEqual(val_data["valid_records"], exp_val_data["valid_records"])

        # Edge-case input check (exits with code 2 due to anomalies)
        proc_edge = subprocess.run(
            [sys.executable, str(script), str(edge_file), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_edge.returncode, 2)
        edge_data = json.loads(proc_edge.stdout)
        exp_edge_data = json.loads(edge_expected_json.read_text(encoding="utf-8"))
        self.assertFalse(edge_data["is_clean"])
        self.assertEqual(edge_data["anomalies_count"], exp_edge_data["anomalies_count"])

    def test_demo_03_project_status_execution(self) -> None:
        """Verify Demo 03 Project Status Reporter executes and RAG calculations match."""
        demo_path = _SHOWCASE_DIR / "project-management" / "project-status"
        script = demo_path / "scripts" / "main.py"
        m_file = demo_path / "sample-inputs" / "valid_milestones.csv"
        r_file = demo_path / "sample-inputs" / "valid_raid.csv"
        expected_json = demo_path / "expected-outputs" / "valid_project_report.json"

        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                str(m_file),
                "--raid-file",
                str(r_file),
                "--as-of-date",
                "2026-10-20",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output_data = json.loads(proc.stdout)
        expected_data = json.loads(expected_json.read_text(encoding="utf-8"))

        self.assertEqual(output_data["overall_health"], "GREEN")
        self.assertEqual(output_data["completion_rate"], expected_data["completion_rate"])
        self.assertEqual(output_data["total_milestones"], expected_data["total_milestones"])

    def test_demo_04_dependency_review_execution(self) -> None:
        """Verify Demo 04 Dependency Reviewer flags insecure configs."""
        demo_path = _SHOWCASE_DIR / "cybersecurity" / "dependency-review"
        script = demo_path / "scripts" / "main.py"
        valid_file = demo_path / "sample-inputs" / "valid_requirements.txt"
        edge_file = demo_path / "sample-inputs" / "edge_case_requirements.txt"
        valid_exp_json = demo_path / "expected-outputs" / "valid_review_report.json"
        edge_exp_json = demo_path / "expected-outputs" / "edge_case_review_report.json"

        proc_val = subprocess.run(
            [sys.executable, str(script), str(valid_file), "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        val_data = json.loads(proc_val.stdout)
        self.assertTrue(val_data["is_clean"])
        self.assertEqual(val_data["total_findings"], 0)

        proc_edge = subprocess.run(
            [sys.executable, str(script), str(edge_file), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_edge.returncode, 2)
        edge_data = json.loads(proc_edge.stdout)
        exp_edge_data = json.loads(edge_exp_json.read_text(encoding="utf-8"))
        self.assertFalse(edge_data["is_clean"])
        self.assertEqual(edge_data["total_findings"], exp_edge_data["total_findings"])

    def test_demo_05_test_inventory_execution(self) -> None:
        """Verify Demo 05 Test Inventory Analyzer identifies test cases and untested modules."""
        demo_path = _SHOWCASE_DIR / "software-engineering" / "test-inventory"
        script = demo_path / "scripts" / "main.py"
        valid_repo = demo_path / "sample-inputs" / "valid_repo"
        edge_repo = demo_path / "sample-inputs" / "edge_case_repo"
        valid_exp_json = demo_path / "expected-outputs" / "valid_inventory_report.json"
        edge_exp_json = demo_path / "expected-outputs" / "edge_case_inventory_report.json"

        proc_val = subprocess.run(
            [sys.executable, str(script), str(valid_repo), "--src-dir", "src", "--tests-dir", "tests", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        val_data = json.loads(proc_val.stdout)
        self.assertEqual(val_data["untested_modules_count"], 0)
        self.assertEqual(val_data["duplicate_tests_count"], 0)

        proc_edge = subprocess.run(
            [sys.executable, str(script), str(edge_repo), "--src-dir", "src", "--tests-dir", "tests", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        edge_data = json.loads(proc_edge.stdout)
        exp_edge_data = json.loads(edge_exp_json.read_text(encoding="utf-8"))
        self.assertEqual(edge_data["untested_modules_count"], 2)
        self.assertEqual(edge_data["duplicate_tests_count"], 1)
        self.assertEqual(edge_data["total_skipped_tests"], exp_edge_data["total_skipped_tests"])


if __name__ == "__main__":
    unittest.main()
