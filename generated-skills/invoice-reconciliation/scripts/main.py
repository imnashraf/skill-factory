#!/usr/bin/env python3
"""Invoice Reconciliation (Finance & ERP Pack).

Reconciles supplier invoices against purchase order registers or payment records,
detecting price variances, unlinked POs, and duplicate invoices.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def reconcile_invoices(
    invoices: List[Dict[str, str]],
    purchase_orders: List[Dict[str, str]],
    amount_tolerance: float = 0.01,
) -> Dict[str, Any]:
    """Reconcile invoices against purchase orders."""
    po_index: Dict[str, Dict[str, str]] = {}
    for po in purchase_orders:
        po_num = po.get("po_number", "").strip()
        if po_num:
            po_index[po_num] = po

    matched: List[Dict[str, Any]] = []
    amount_mismatch: List[Dict[str, Any]] = []
    missing_po: List[Dict[str, Any]] = []
    seen_invoices: Dict[str, int] = {}
    duplicates: List[str] = []

    for inv in invoices:
        inv_num = inv.get("invoice_number", "").strip()
        po_num = inv.get("po_number", "").strip()
        inv_amt = float(inv.get("amount", 0) or 0)
        vendor = inv.get("vendor", "").strip()

        # Duplicate check
        seen_invoices[inv_num] = seen_invoices.get(inv_num, 0) + 1
        if seen_invoices[inv_num] == 2:
            duplicates.append(inv_num)

        if not po_num or po_num not in po_index:
            missing_po.append({
                "invoice_number": inv_num,
                "vendor": vendor,
                "amount": inv_amt,
                "po_number": po_num or "None",
            })
            continue

        po = po_index[po_num]
        po_amt = float(po.get("amount", 0) or 0)
        diff = inv_amt - po_amt

        if abs(diff) <= amount_tolerance:
            matched.append({
                "invoice_number": inv_num,
                "po_number": po_num,
                "vendor": vendor,
                "amount": inv_amt,
            })
        else:
            amount_mismatch.append({
                "invoice_number": inv_num,
                "po_number": po_num,
                "vendor": vendor,
                "invoice_amount": inv_amt,
                "po_amount": po_amt,
                "difference": round(diff, 2),
            })

    total_invoices_count = len(invoices)
    total_invoiced_amt = sum(float(i.get("amount", 0) or 0) for i in invoices)

    return {
        "total_invoices": total_invoices_count,
        "total_invoiced_amount": round(total_invoiced_amt, 2),
        "matched_count": len(matched),
        "mismatched_amount_count": len(amount_mismatch),
        "missing_po_count": len(missing_po),
        "duplicate_invoices": duplicates,
        "matched": matched,
        "amount_mismatch": amount_mismatch,
        "missing_po": missing_po,
    }


def format_markdown_report(data: Dict[str, Any]) -> str:
    """Format reconciliation results as GitHub-flavored markdown."""
    out = ["# Supplier Invoice Reconciliation Report", ""]
    out.append("## Reconciliation Summary")
    out.append(f"- **Total Invoices Processed:** {data['total_invoices']}")
    out.append(f"- **Total Invoiced Amount:** ${data['total_invoiced_amount']:,.2f}")
    out.append(f"- **Fully Matched:** {data['matched_count']}")
    out.append(f"- **Amount Discrepancies:** {data['mismatched_amount_count']}")
    out.append(f"- **Missing / Invalid POs:** {data['missing_po_count']}")
    out.append(f"- **Duplicate Invoices Detected:** {len(data['duplicate_invoices'])}")
    out.append("")

    if data["duplicate_invoices"]:
        out.append("## Duplicate Invoices Flagged")
        for dup in data["duplicate_invoices"]:
            out.append(f"- **Flag:** Invoice #{dup} appeared multiple times.")
        out.append("")

    if data["amount_mismatch"]:
        out.append("## Price & Amount Discrepancies")
        out.append("| Invoice # | PO # | Vendor | Invoice Amt | PO Amt | Variance |")
        out.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for item in data["amount_mismatch"]:
            out.append(
                f"| {item['invoice_number']} | {item['po_number']} | {item['vendor']} | "
                f"${item['invoice_amount']:,.2f} | ${item['po_amount']:,.2f} | ${item['difference']:+,.2f} |"
            )
        out.append("")

    if data["missing_po"]:
        out.append("## Invoices with Missing or Unrecognized Purchase Orders")
        out.append("| Invoice # | Vendor | Amount | Referenced PO |")
        out.append("| :--- | :--- | :--- | :--- |")
        for item in data["missing_po"]:
            out.append(f"| {item['invoice_number']} | {item['vendor']} | ${item['amount']:,.2f} | {item['po_number']} |")
        out.append("")

    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Reconcile supplier invoices against purchase order data.")
    parser.add_argument("invoices_file", help="Path to invoices CSV (columns: invoice_number,po_number,vendor,amount)")
    parser.add_argument("po_file", help="Path to purchase orders CSV (columns: po_number,vendor,amount)")
    parser.add_argument("--tolerance", type=float, default=0.01, help="Amount tolerance for match")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    inv_path = Path(args.invoices_file)
    po_path = Path(args.po_file)

    if not inv_path.is_file() or not po_path.is_file():
        print(f"[ERROR] Input files not found: {inv_path}, {po_path}", file=sys.stderr)
        return 1

    with open(inv_path, "r", encoding="utf-8") as f:
        invoices = list(csv.DictReader(f))
    with open(po_path, "r", encoding="utf-8") as f:
        pos = list(csv.DictReader(f))

    data = reconcile_invoices(invoices, pos, amount_tolerance=args.tolerance)

    if args.json:
        out = json.dumps(data, indent=2)
    else:
        out = format_markdown_report(data)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"[OK] Report written to {args.output}")
    else:
        print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
