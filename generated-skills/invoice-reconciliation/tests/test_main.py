"""Tests for invoice-reconciliation."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import format_markdown_report, reconcile_invoices  # type: ignore


class TestInvoiceReconciliation(unittest.TestCase):
    def test_reconcile_flow(self):
        invoices = [
            {"invoice_number": "INV-101", "po_number": "PO-900", "vendor": "Acme Corp", "amount": "1200.00"},
            {"invoice_number": "INV-102", "po_number": "PO-901", "vendor": "Beta Ltd", "amount": "450.00"},
            {"invoice_number": "INV-103", "po_number": "PO-902", "vendor": "Gamma LLC", "amount": "800.00"},
            {"invoice_number": "INV-104", "po_number": "PO-999", "vendor": "Delta Inc", "amount": "300.00"},
            {"invoice_number": "INV-101", "po_number": "PO-900", "vendor": "Acme Corp", "amount": "1200.00"}, # Dup
        ]
        pos = [
            {"po_number": "PO-900", "vendor": "Acme Corp", "amount": "1200.00"}, # Match
            {"po_number": "PO-901", "vendor": "Beta Ltd", "amount": "400.00"},   # Mismatch
            {"po_number": "PO-902", "vendor": "Gamma LLC", "amount": "800.00"},   # Match
        ]

        res = reconcile_invoices(invoices, pos)
        self.assertEqual(res["total_invoices"], 5)
        self.assertEqual(res["matched_count"], 3) # INV-101 (twice), INV-103
        self.assertEqual(res["mismatched_amount_count"], 1) # INV-102
        self.assertEqual(res["missing_po_count"], 1) # INV-104
        self.assertEqual(res["duplicate_invoices"], ["INV-101"])

        md = format_markdown_report(res)
        self.assertIn("# Supplier Invoice Reconciliation Report", md)
        self.assertIn("INV-101", md)


if __name__ == "__main__":
    unittest.main()
