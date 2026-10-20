"""Tests for financial-variance-analyzer."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import analyze_variances, format_report_markdown  # type: ignore


class TestFinancialVarianceAnalyzer(unittest.TestCase):
    def test_analyze_variances(self):
        budget = [
            {"account": "Engineering", "amount": "50000"},
            {"account": "Marketing", "amount": "20000"},
            {"account": "Legal", "amount": "10000"},
        ]
        actual = [
            {"account": "Engineering", "amount": "55000"}, # +10%, material
            {"account": "Marketing", "amount": "18000"}, # -10%, material
            {"account": "Legal", "amount": "10200"}, # +2%, not material
        ]
        res = analyze_variances(budget, actual, threshold_pct=10.0, threshold_abs=1500.0)
        self.assertEqual(res["total_budget"], 80000.0)
        self.assertEqual(res["total_actual"], 83200.0)
        self.assertEqual(res["total_variance_amount"], 3200.0)
        self.assertEqual(res["material_variances_count"], 2)

        md = format_report_markdown(res)
        self.assertIn("# Financial Variance Analysis Report", md)
        self.assertIn("Engineering", md)
        self.assertIn("**YES**", md)


if __name__ == "__main__":
    unittest.main()
