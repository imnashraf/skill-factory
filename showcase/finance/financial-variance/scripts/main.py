#!/usr/bin/env python3
"""Financial Variance Analyzer (Showcase Demo 01).

Domain: Finance and Accounting.
Calculates absolute and percentage variances between budgeted and actual figures
across departments, cost centers, and accounts using Python Decimal arithmetic.
Identifies material variances, handles zero-budget allocations deterministically,
and traces findings to source record lines without inventing speculative explanations.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TWO_PLACES = Decimal("0.01")
ONE_PLACE = Decimal("0.1")


def to_decimal(val: Any) -> Decimal:
    """Safely convert any numeric representation to Decimal."""
    if val is None:
        return Decimal("0.00")
    if isinstance(val, Decimal):
        return val
    cleaned = str(val).strip().replace("$", "").replace(",", "")
    if not cleaned:
        return Decimal("0.00")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Invalid monetary amount: '{val}'")


def format_currency(d: Decimal) -> str:
    """Format Decimal as standard currency string."""
    q = d.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    return f"${q:,.2f}"


def format_signed_currency(d: Decimal) -> str:
    """Format Decimal with explicit +/- currency sign."""
    q = d.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    if q > 0:
        return f"+${q:,.2f}"
    elif q < 0:
        return f"-${abs(q):,.2f}"
    return f"${q:,.2f}"


def parse_financial_csv(
    file_path: Path,
    expected_type: str,
    account_col: str = "account",
    cost_center_col: str = "cost_center",
    amount_col: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Parse financial CSV file, validate structure, and extract rows with source tracing."""
    if not file_path.is_file():
        return [], [f"File not found: {file_path}"]

    records: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return [], [f"Failed to read file '{file_path}': {exc}"]

    reader = csv.DictReader(content.splitlines())
    if not reader.fieldnames:
        return [], [f"CSV file '{file_path.name}' is empty or has no header row"]

    fieldnames = [fn.strip() for fn in reader.fieldnames if fn]
    
    # Determine amount column dynamically if not specified
    amt_col = amount_col
    if not amt_col:
        for candidate in ("amount", f"{expected_type}_amount", f"{expected_type}", "value", "spend"):
            if candidate in fieldnames:
                amt_col = candidate
                break

    if not amt_col:
        return [], [
            f"Missing amount column in '{file_path.name}'. Expected one of: "
            f"'amount', '{expected_type}_amount', or specify via CLI."
        ]

    if account_col not in fieldnames:
        return [], [f"Missing required account column '{account_col}' in '{file_path.name}'"]

    has_cost_center = cost_center_col in fieldnames

    for line_num, row in enumerate(reader, start=2):
        acc = (row.get(account_col) or "").strip()
        cc = (row.get(cost_center_col) or "GENERAL").strip() if has_cost_center else "GENERAL"
        dept = (row.get("department") or row.get("dept") or "Corporate").strip()
        raw_amount = row.get(amt_col, "").strip()

        if not acc:
            errors.append(f"Line {line_num}: missing account identifier in '{file_path.name}'")
            continue

        try:
            amount_dec = to_decimal(raw_amount)
        except ValueError as val_err:
            errors.append(f"Line {line_num}: {val_err} in '{file_path.name}'")
            continue

        records.append({
            "source_file": file_path.name,
            "source_line": line_num,
            "account": acc,
            "cost_center": cc,
            "department": dept,
            "amount": amount_dec,
        })

    return records, errors


def analyze_financial_variances(
    budget_records: List[Dict[str, Any]],
    actual_records: List[Dict[str, Any]],
    threshold_pct: Decimal = Decimal("10.0"),
    threshold_abs: Decimal = Decimal("1000.00"),
) -> Dict[str, Any]:
    """Reconcile budget and actual records by (account, cost_center) using Decimal arithmetic."""
    budget_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for r in budget_records:
        key = (r["account"], r["cost_center"])
        budget_map[key] = r

    actual_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for r in actual_records:
        key = (r["account"], r["cost_center"])
        actual_map[key] = r

    all_keys = sorted(set(budget_map.keys()) | set(actual_map.keys()))

    line_items: List[Dict[str, Any]] = []
    total_budget = Decimal("0.00")
    total_actual = Decimal("0.00")
    material_count = 0

    for acc, cc in all_keys:
        b_rec = budget_map.get((acc, cc))
        a_rec = actual_map.get((acc, cc))

        b_val = b_rec["amount"] if b_rec else Decimal("0.00")
        a_val = a_rec["amount"] if a_rec else Decimal("0.00")
        rec = a_rec if a_rec is not None else b_rec
        dept = rec["department"] if rec is not None else "Corporate"

        total_budget += b_val
        total_actual += a_val

        diff = a_val - b_val

        # Handle zero-budget and percentage calculation deterministically
        if b_val == Decimal("0.00"):
            if a_val == Decimal("0.00"):
                pct = Decimal("0.0")
                direction = "On Budget"
            else:
                pct = Decimal("100.0")
                direction = "Unbudgeted Spend"
        elif a_val == Decimal("0.00"):
            pct = Decimal("-100.0")
            direction = "Unspent Budget"
        else:
            raw_pct = ((diff / b_val) * Decimal("100.0")).quantize(ONE_PLACE, rounding=ROUND_HALF_UP)
            pct = raw_pct
            if diff > Decimal("0.00"):
                direction = "Over Budget"
            elif diff < Decimal("0.00"):
                direction = "Under Budget"
            else:
                direction = "On Budget"

        is_material = (abs(diff) >= threshold_abs) or (abs(pct) >= threshold_pct)
        if is_material:
            material_count += 1

        b_line = b_rec["source_line"] if b_rec else None
        a_line = a_rec["source_line"] if a_rec else None

        line_items.append({
            "account": acc,
            "cost_center": cc,
            "department": dept,
            "budget": b_val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
            "actual": a_val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
            "variance_amount": diff.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
            "variance_percent": pct.quantize(ONE_PLACE, rounding=ROUND_HALF_UP),
            "status": direction,
            "is_material": is_material,
            "budget_source_line": b_line,
            "actual_source_line": a_line,
        })

    total_diff = total_actual - total_budget
    if total_budget == Decimal("0.00"):
        total_pct = Decimal("100.0") if total_actual != Decimal("0.00") else Decimal("0.0")
    else:
        total_pct = ((total_diff / total_budget) * Decimal("100.0")).quantize(ONE_PLACE, rounding=ROUND_HALF_UP)

    return {
        "total_budget": total_budget.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_actual": total_actual.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_variance_amount": total_diff.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_variance_percent": total_pct,
        "total_line_items": len(all_keys),
        "material_variances_count": material_count,
        "threshold_pct": threshold_pct.quantize(ONE_PLACE),
        "threshold_abs": threshold_abs.quantize(TWO_PLACES),
        "line_items": line_items,
    }


def format_markdown_report(data: Dict[str, Any], title: str = "Financial Variance Analysis Report") -> str:
    """Render executive financial variance report in GitHub-flavored Markdown."""
    lines: List[str] = [
        f"# {title}",
        "",
        "## Executive Summary",
        "",
        f"- **Total Budget Allocation:** {format_currency(data['total_budget'])}",
        f"- **Total Actual Spend:** {format_currency(data['total_actual'])}",
        f"- **Net Variance:** {format_signed_currency(data['total_variance_amount'])} ({data['total_variance_percent']:+.1f}%)",
        f"- **Material Variances Flagged:** {data['material_variances_count']} / {data['total_line_items']} line items",
        f"- **Applied Materiality Thresholds:** >= {data['threshold_pct']}% OR >= {format_currency(data['threshold_abs'])}",
        "",
        "## Variance Register",
        "",
        "| Account | Cost Center | Department | Budget | Actual | Variance ($) | Variance (%) | Status | Material? | Source Lines (B / A) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for item in data["line_items"]:
        b_str = format_currency(item["budget"])
        a_str = format_currency(item["actual"])
        diff_str = format_signed_currency(item["variance_amount"])
        pct_str = f"{item['variance_percent']:+.1f}%"
        mat_str = "**YES**" if item["is_material"] else "No"
        b_line_str = str(item["budget_source_line"]) if item["budget_source_line"] else "-"
        a_line_str = str(item["actual_source_line"]) if item["actual_source_line"] else "-"
        sources = f"L{b_line_str} / L{a_line_str}"

        lines.append(
            f"| `{item['account']}` | `{item['cost_center']}` | {item['department']} | "
            f"{b_str} | {a_str} | {diff_str} | {pct_str} | {item['status']} | {mat_str} | {sources} |"
        )

    lines.append("")
    lines.append("## Governance & Audit Notice")
    lines.append("")
    lines.append("All calculations performed using exact decimal arithmetic. Zero-budget and unbudgeted entries")
    lines.append("are deterministically categorized without speculative justifications.")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze financial variances between budget and actual CSV datasets.")
    parser.add_argument("budget_file", help="Path to budget CSV file")
    parser.add_argument("actual_file", help="Path to actuals CSV file")
    parser.add_argument("--account-col", default="account", help="Account column name (default: account)")
    parser.add_argument("--cost-center-col", default="cost_center", help="Cost center column name (default: cost_center)")
    parser.add_argument("--amount-col", default=None, help="Explicit amount column name")
    parser.add_argument("--threshold-pct", type=float, default=10.0, help="Materiality percentage threshold (default: 10.0)")
    parser.add_argument("--threshold-abs", type=float, default=1000.0, help="Materiality absolute dollar threshold (default: 1000.0)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--output", help="Write report to specified output file")
    args = parser.parse_args(argv)

    budget_path = Path(args.budget_file)
    actual_path = Path(args.actual_file)

    b_records, b_errors = parse_financial_csv(
        budget_path,
        expected_type="budget",
        account_col=args.account_col,
        cost_center_col=args.cost_center_col,
        amount_col=args.amount_col,
    )
    a_records, a_errors = parse_financial_csv(
        actual_path,
        expected_type="actual",
        account_col=args.account_col,
        cost_center_col=args.cost_center_col,
        amount_col=args.amount_col,
    )

    all_errors = b_errors + a_errors
    if all_errors:
        print(f"[ERROR] Input validation failed with {len(all_errors)} issue(s):", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    pct_dec = Decimal(str(args.threshold_pct))
    abs_dec = Decimal(str(args.threshold_abs))

    data = analyze_financial_variances(
        b_records,
        a_records,
        threshold_pct=pct_dec,
        threshold_abs=abs_dec,
    )

    if args.json:
        # Convert Decimal values for JSON serialization
        def serialize_dec(obj: Any) -> Any:
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        output_text = json.dumps(data, indent=2, default=serialize_dec)
    else:
        output_text = format_markdown_report(data)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output_text, encoding="utf-8")
        print(f"[OK] Financial variance report written to {args.output}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
