#!/usr/bin/env python3
"""Financial Variance Analyzer (Finance & ERP Pack).

Analyzes budgeted vs. actual financial figures from CSV files, computes
absolute and percentage variances, flags material exceptions, and produces
executive summary tables.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def analyze_variances(
    budget_rows: List[Dict[str, str]],
    actual_rows: List[Dict[str, str]],
    key_field: str = "account",
    threshold_pct: float = 10.0,
    threshold_abs: float = 1000.0,
) -> Dict[str, Any]:
    """Calculate variances between budgeted and actual line items."""
    budget_map: Dict[str, float] = {}
    for r in budget_rows:
        k = r.get(key_field, "").strip()
        val = float(r.get("amount", 0) or 0)
        budget_map[k] = val

    actual_map: Dict[str, float] = {}
    for r in actual_rows:
        k = r.get(key_field, "").strip()
        val = float(r.get("amount", 0) or 0)
        actual_map[k] = val

    all_keys = sorted(set(budget_map.keys()) | set(actual_map.keys()))
    line_items: List[Dict[str, Any]] = []
    total_budget = sum(budget_map.values())
    total_actual = sum(actual_map.values())

    material_count = 0

    for k in all_keys:
        b = budget_map.get(k, 0.0)
        a = actual_map.get(k, 0.0)
        diff = a - b
        pct = ((a - b) / b * 100.0) if b != 0 else (100.0 if a != 0 else 0.0)
        
        is_material = (abs(pct) >= threshold_pct) or (abs(diff) >= threshold_abs)
        if is_material:
            material_count += 1

        direction = "Over Budget" if diff > 0 else ("Under Budget" if diff < 0 else "On Target")

        line_items.append({
            "account": k,
            "budget": b,
            "actual": a,
            "variance_amount": round(diff, 2),
            "variance_percent": round(pct, 2),
            "status": direction,
            "is_material": is_material,
        })

    total_diff = total_actual - total_budget
    total_pct = (total_diff / total_budget * 100.0) if total_budget != 0 else 0.0

    return {
        "total_budget": round(total_budget, 2),
        "total_actual": round(total_actual, 2),
        "total_variance_amount": round(total_diff, 2),
        "total_variance_percent": round(total_pct, 2),
        "total_accounts": len(all_keys),
        "material_variances_count": material_count,
        "line_items": line_items,
    }


def format_report_markdown(data: Dict[str, Any], title: str = "Financial Variance Analysis Report") -> str:
    """Format analysis data as GitHub-flavored markdown."""
    out = [f"# {title}", ""]
    out.append("## Executive Summary")
    out.append(f"- **Total Budget:** ${data['total_budget']:,.2f}")
    out.append(f"- **Total Actual:** ${data['total_actual']:,.2f}")
    out.append(f"- **Net Variance:** ${data['total_variance_amount']:,.2f} ({data['total_variance_percent']:+.1f}%)")
    out.append(f"- **Material Variances Flagged:** {data['material_variances_count']} / {data['total_accounts']} accounts")
    out.append("")
    out.append("## Detailed Account Variances")
    out.append("| Account | Budget | Actual | Variance ($) | Variance (%) | Status | Material? |")
    out.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for item in data["line_items"]:
        mat_flag = "**YES**" if item["is_material"] else "No"
        out.append(
            f"| {item['account']} | ${item['budget']:,.2f} | ${item['actual']:,.2f} | "
            f"${item['variance_amount']:+,.2f} | {item['variance_percent']:+.1f}% | "
            f"{item['status']} | {mat_flag} |"
        )
    out.append("")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze financial variance between budget and actual CSV data.")
    parser.add_argument("budget_file", help="Path to budget CSV file (must have account,amount columns)")
    parser.add_argument("actual_file", help="Path to actuals CSV file (must have account,amount columns)")
    parser.add_argument("--key", default="account", help="Key field name (default: account)")
    parser.add_argument("--threshold-pct", type=float, default=10.0, help="Material variance percentage threshold")
    parser.add_argument("--threshold-abs", type=float, default=1000.0, help="Material variance dollar threshold")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    b_path = Path(args.budget_file)
    a_path = Path(args.actual_file)

    if not b_path.is_file() or not a_path.is_file():
        print(f"[ERROR] One or both input files do not exist: {b_path}, {a_path}", file=sys.stderr)
        return 1

    with open(b_path, "r", encoding="utf-8") as f:
        budget_rows = list(csv.DictReader(f))
    with open(a_path, "r", encoding="utf-8") as f:
        actual_rows = list(csv.DictReader(f))

    data = analyze_variances(
        budget_rows,
        actual_rows,
        key_field=args.key,
        threshold_pct=args.threshold_pct,
        threshold_abs=args.threshold_abs,
    )

    if args.json:
        res = json.dumps(data, indent=2)
    else:
        res = format_report_markdown(data)

    if args.output:
        Path(args.output).write_text(res, encoding="utf-8")
        print(f"[OK] Variance report written to {args.output}")
    else:
        print(res)

    return 0


if __name__ == "__main__":
    sys.exit(main())
