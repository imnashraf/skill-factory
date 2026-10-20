#!/usr/bin/env python3
"""Timesheet Reconciliation (HR & Workforce Pack).

Compares employee logged project hours against approved weekly allocation budgets,
identifying overruns, under-utilization, and unlogged project codes.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def reconcile_timesheets(
    timesheet_records: List[Dict[str, str]],
    budget_records: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Reconcile timesheet entries against budget allocations by employee and project."""
    # Build budget lookup: (employee_id, project_code) -> allocated_hours
    budget_map: Dict[str, float] = {}
    for b in budget_records:
        k = f"{b.get('employee_id', '').strip()}:{b.get('project_code', '').strip()}"
        budget_map[k] = float(b.get('allocated_hours', 0) or 0)

    # Aggregate timesheet hours: (employee_id, project_code) -> logged_hours
    logged_map: Dict[str, float] = {}
    for t in timesheet_records:
        k = f"{t.get('employee_id', '').strip()}:{t.get('project_code', '').strip()}"
        logged_map[k] = logged_map.get(k, 0.0) + float(t.get('hours', 0) or 0)

    all_keys = sorted(set(budget_map.keys()) | set(logged_map.keys()))
    items: List[Dict[str, Any]] = []
    overruns_count = 0
    under_count = 0

    for k in all_keys:
        emp_id, proj_code = k.split(":", 1)
        budgeted = budget_map.get(k, 0.0)
        logged = logged_map.get(k, 0.0)
        variance = logged - budgeted

        status = "On Budget"
        if variance > 0:
            status = "Over Allocation"
            overruns_count += 1
        elif variance < -5.0:
            status = "Under Allocation"
            under_count += 1

        items.append({
            "employee_id": emp_id,
            "project_code": proj_code,
            "budgeted_hours": round(budgeted, 2),
            "logged_hours": round(logged, 2),
            "variance_hours": round(variance, 2),
            "status": status,
        })

    total_budgeted = sum(budget_map.values())
    total_logged = sum(logged_map.values())

    return {
        "total_budgeted_hours": round(total_budgeted, 2),
        "total_logged_hours": round(total_logged, 2),
        "total_variance_hours": round(total_logged - total_budgeted, 2),
        "total_allocations": len(all_keys),
        "overruns_count": overruns_count,
        "under_allocations_count": under_count,
        "items": items,
    }


def format_markdown_report(data: Dict[str, Any]) -> str:
    """Format timesheet reconciliation report in GitHub-flavored markdown."""
    out = ["# Timesheet vs. Budget Reconciliation Report", ""]
    out.append("## Workforce Hours Summary")
    out.append(f"- **Total Budgeted Hours:** {data['total_budgeted_hours']:.1f} hrs")
    out.append(f"- **Total Logged Hours:** {data['total_logged_hours']:.1f} hrs")
    out.append(f"- **Net Variance:** {data['total_variance_hours']:+.1f} hrs")
    out.append(f"- **Over-Allocated Projects:** {data['overruns_count']}")
    out.append(f"- **Under-Allocated Projects:** {data['under_allocations_count']}")
    out.append("")
    out.append("## Employee & Project Details")
    out.append("| Employee ID | Project Code | Budget (hrs) | Logged (hrs) | Variance | Status |")
    out.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for it in data["items"]:
        out.append(
            f"| {it['employee_id']} | {it['project_code']} | {it['budgeted_hours']:.1f} | "
            f"{it['logged_hours']:.1f} | {it['variance_hours']:+.1f} | {it['status']} |"
        )
    out.append("")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Reconcile timesheet hours against project budget allocations.")
    parser.add_argument("timesheets_file", help="Path to timesheets CSV (columns: employee_id,project_code,hours)")
    parser.add_argument("budgets_file", help="Path to budget CSV (columns: employee_id,project_code,allocated_hours)")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    t_path = Path(args.timesheets_file)
    b_path = Path(args.budgets_file)

    if not t_path.is_file() or not b_path.is_file():
        print(f"[ERROR] Input files not found: {t_path}, {b_path}", file=sys.stderr)
        return 1

    with open(t_path, "r", encoding="utf-8") as f:
        timesheets = list(csv.DictReader(f))
    with open(b_path, "r", encoding="utf-8") as f:
        budgets = list(csv.DictReader(f))

    data = reconcile_timesheets(timesheets, budgets)

    if args.json:
        res = json.dumps(data, indent=2)
    else:
        res = format_markdown_report(data)

    if args.output:
        Path(args.output).write_text(res, encoding="utf-8")
        print(f"[OK] Reconciliation report written to {args.output}")
    else:
        print(res)

    return 0


if __name__ == "__main__":
    sys.exit(main())
