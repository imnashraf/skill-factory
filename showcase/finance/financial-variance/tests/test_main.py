#!/usr/bin/env python3
"""Automated unit and regression tests for Financial Variance Analyzer (Demo 01)."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

# Add script directory to sys.path
_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from main import (
    analyze_financial_variances,
    format_currency,
    format_markdown_report,
    format_signed_currency,
    parse_financial_csv,
    to_decimal,
)


class TestFinancialVarianceAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        self.demo_dir = Path(__file__).resolve().parent.parent
        self.inputs_dir = self.demo_dir / "sample-inputs"
        self.expected_dir = self.demo_dir / "expected-outputs"

    def test_to_decimal_conversion(self) -> None:
        """Verify safe decimal conversions and error handling."""
        self.assertEqual(to_decimal("150000.00"), Decimal("150000.00"))
        self.assertEqual(to_decimal("$1,234.56"), Decimal("1234.56"))
        self.assertEqual(to_decimal(""), Decimal("0.00"))
        self.assertEqual(to_decimal(None), Decimal("0.00"))
        with self.assertRaises(ValueError):
            to_decimal("invalid-amount")

    def test_currency_formatting(self) -> None:
        """Verify currency display formatting."""
        self.assertEqual(format_currency(Decimal("150000.00")), "$150,000.00")
        self.assertEqual(format_signed_currency(Decimal("12500.00")), "+$12,500.00")
        self.assertEqual(format_signed_currency(Decimal("-900.00")), "-$900.00")
        self.assertEqual(format_signed_currency(Decimal("0.00")), " $0.00")

    def test_valid_dataset_reconciliation(self) -> None:
        """Verify end-to-end reconciliation on valid sample inputs."""
        b_path = self.inputs_dir / "valid_budget.csv"
        a_path = self.inputs_dir / "valid_actuals.csv"

        # Check input file integrity hash before run
        b_hash_pre = hashlib.sha256(b_path.read_bytes()).hexdigest()
        a_hash_pre = hashlib.sha256(a_path.read_bytes()).hexdigest()

        b_records, b_err = parse_financial_csv(b_path, expected_type="budget")
        a_records, a_err = parse_financial_csv(a_path, expected_type="actual")
        self.assertEqual(b_err, [])
        self.assertEqual(a_err, [])
        self.assertEqual(len(b_records), 11)
        self.assertEqual(len(a_records), 11)

        result = analyze_financial_variances(
            b_records,
            a_records,
            threshold_pct=Decimal("10.0"),
            threshold_abs=Decimal("1000.00"),
        )

        self.assertEqual(result["total_budget"], Decimal("445000.00"))
        self.assertEqual(result["total_actual"], Decimal("475950.00"))
        self.assertEqual(result["total_variance_amount"], Decimal("30950.00"))
        self.assertEqual(result["total_variance_percent"], Decimal("7.0"))
        self.assertEqual(result["material_variances_count"], 6)

        # Check input files remained unchanged
        b_hash_post = hashlib.sha256(b_path.read_bytes()).hexdigest()
        a_hash_post = hashlib.sha256(a_path.read_bytes()).hexdigest()
        self.assertEqual(b_hash_pre, b_hash_post)
        self.assertEqual(a_hash_pre, a_hash_post)

    def test_edge_cases_zero_budget_and_boundaries(self) -> None:
        """Verify zero-budget allocations, unbudgeted spend, and exact threshold boundaries."""
        b_path = self.inputs_dir / "edge_case_budget.csv"
        a_path = self.inputs_dir / "edge_case_actuals.csv"

        b_records, _ = parse_financial_csv(b_path, expected_type="budget")
        a_records, _ = parse_financial_csv(a_path, expected_type="actual")

        result = analyze_financial_variances(
            b_records,
            a_records,
            threshold_pct=Decimal("10.0"),
            threshold_abs=Decimal("1000.00"),
        )

        items = {item["account"]: item for item in result["line_items"]}

        # Zero budget with actual spend -> Unbudgeted Spend (+100.0%)
        self.assertEqual(items["GL-9001"]["status"], "Unbudgeted Spend")
        self.assertEqual(items["GL-9001"]["variance_percent"], Decimal("100.0"))
        self.assertTrue(items["GL-9001"]["is_material"])

        # Budget with zero actual spend -> Unspent Budget (-100.0%)
        self.assertEqual(items["GL-9002"]["status"], "Unspent Budget")
        self.assertEqual(items["GL-9002"]["variance_percent"], Decimal("-100.0"))
        self.assertTrue(items["GL-9002"]["is_material"])

        # Zero budget and zero actual spend -> On Budget (0.0%)
        self.assertEqual(items["GL-9003"]["status"], "On Budget")
        self.assertEqual(items["GL-9003"]["variance_percent"], Decimal("0.0"))
        self.assertFalse(items["GL-9003"]["is_material"])

        # Exact matching amounts -> On Budget (0.0%)
        self.assertEqual(items["GL-9004"]["variance_amount"], Decimal("0.00"))
        self.assertFalse(items["GL-9004"]["is_material"])

        # Boundary below $1000 and below 10% -> immaterial
        self.assertEqual(items["GL-9005"]["variance_amount"], Decimal("999.99"))
        self.assertFalse(items["GL-9005"]["is_material"])

        # Boundary at exact $1000 -> material
        self.assertEqual(items["GL-9006"]["variance_amount"], Decimal("1000.00"))
        self.assertTrue(items["GL-9006"]["is_material"])

        # In budget only
        self.assertEqual(items["GL-9007"]["status"], "Unspent Budget")
        self.assertEqual(items["GL-9007"]["actual_source_line"], None)

        # In actuals only
        self.assertEqual(items["GL-9008"]["status"], "Unbudgeted Spend")
        self.assertEqual(items["GL-9008"]["budget_source_line"], None)

    def test_invalid_input_validation(self) -> None:
        """Verify malformed input detection."""
        inv_path = self.inputs_dir / "invalid_budget.csv"
        records, errors = parse_financial_csv(inv_path, expected_type="budget")
        self.assertGreaterEqual(len(errors), 2)
        self.assertTrue(any("missing account" in e for e in errors))
        self.assertTrue(any("Invalid monetary amount" in e for e in errors))

    def test_markdown_report_matches_expected(self) -> None:
        """Verify markdown report matches recorded expected output."""
        b_path = self.inputs_dir / "valid_budget.csv"
        a_path = self.inputs_dir / "valid_actuals.csv"
        expected_md = (self.expected_dir / "valid_variance_report.md").read_text(encoding="utf-8")

        b_records, _ = parse_financial_csv(b_path, expected_type="budget")
        a_records, _ = parse_financial_csv(a_path, expected_type="actual")
        data = analyze_financial_variances(b_records, a_records)
        rendered_md = format_markdown_report(data)

        self.assertEqual(rendered_md.strip(), expected_md.strip())


if __name__ == "__main__":
    unittest.main()
