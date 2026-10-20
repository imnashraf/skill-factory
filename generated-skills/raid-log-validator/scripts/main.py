#!/usr/bin/env python3
"""RAID Log Validator (Project Management Pack).

Audits project Risk, Assumption, Issue, and Dependency (RAID) registers
for missing ownership, overdue resolution dates, unranked impact ratings,
and invalid lifecycle states.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

VALID_TYPES = {"RISK", "ASSUMPTION", "ISSUE", "DEPENDENCY"}
VALID_STATUSES = {"OPEN", "IN_PROGRESS", "CLOSED", "BLOCKED", "MITIGATED"}
VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def audit_raid_records(
    records: List[Dict[str, str]],
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Audit RAID register records and return findings."""
    today = reference_date or date.today()
    total_records = len(records)
    issues_found: List[Dict[str, Any]] = []
    type_counts: Dict[str, int] = {t: 0 for t in VALID_TYPES}
    overdue_count = 0

    for idx, r in enumerate(records, start=1):
        item_id = r.get("id", "").strip() or f"Row-{idx}"
        item_type = r.get("type", "").strip().upper()
        description = r.get("description", "").strip()
        owner = r.get("owner", "").strip()
        status = r.get("status", "").strip().upper()
        severity = r.get("severity", "").strip().upper()
        due_date_str = r.get("due_date", "").strip()

        # Type check
        if item_type not in VALID_TYPES:
            issues_found.append({
                "id": item_id,
                "row": idx,
                "severity": "HIGH",
                "issue": f"Invalid RAID type '{item_type}'. Must be one of {sorted(VALID_TYPES)}.",
            })
        else:
            type_counts[item_type] += 1

        # Description check
        if not description or len(description) < 5:
            issues_found.append({
                "id": item_id,
                "row": idx,
                "severity": "MEDIUM",
                "issue": "Description is missing or too brief (< 5 characters).",
            })

        # Owner check
        if not owner or owner.lower() in ("unassigned", "none", "tbd"):
            issues_found.append({
                "id": item_id,
                "row": idx,
                "severity": "HIGH",
                "issue": f"Actionable owner is missing (found '{owner or 'empty'}').",
            })

        # Status check
        if status not in VALID_STATUSES:
            issues_found.append({
                "id": item_id,
                "row": idx,
                "severity": "MEDIUM",
                "issue": f"Invalid status '{status}'. Must be one of {sorted(VALID_STATUSES)}.",
            })

        # Severity check
        if severity not in VALID_SEVERITIES:
            issues_found.append({
                "id": item_id,
                "row": idx,
                "severity": "MEDIUM",
                "issue": f"Invalid severity rating '{severity}'. Must be one of {sorted(VALID_SEVERITIES)}.",
            })

        # Due date check
        if due_date_str and status not in ("CLOSED", "MITIGATED"):
            try:
                dt = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                if dt < today:
                    overdue_count += 1
                    issues_found.append({
                        "id": item_id,
                        "row": idx,
                        "severity": "HIGH",
                        "issue": f"Target resolution date ({due_date_str}) is overdue (as of {today.isoformat()}).",
                    })
            except ValueError:
                issues_found.append({
                    "id": item_id,
                    "row": idx,
                    "severity": "MEDIUM",
                    "issue": f"Due date '{due_date_str}' is not in YYYY-MM-DD format.",
                })

    return {
        "total_records": total_records,
        "type_counts": type_counts,
        "overdue_count": overdue_count,
        "issues_count": len(issues_found),
        "is_healthy": len(issues_found) == 0,
        "issues": issues_found,
    }


def format_markdown_report(data: Dict[str, Any]) -> str:
    """Format RAID audit report as GitHub-flavored markdown."""
    out = ["# RAID Register Audit Report", ""]
    out.append("## Executive Summary")
    out.append(f"- **Total Items Audited:** {data['total_records']}")
    for k, v in data["type_counts"].items():
        out.append(f"  • {k.capitalize()}s: {v}")
    out.append(f"- **Overdue Open Items:** {data['overdue_count']}")
    out.append(f"- **Governance Issues Flagged:** {data['issues_count']}")
    health_str = "**HEALTHY (No Governance Defects)**" if data["is_healthy"] else "**ACTION REQUIRED**"
    out.append(f"- **Register Status:** {health_str}")
    out.append("")

    if data["issues"]:
        out.append("## Governance Issues Detected")
        out.append("| ID | Row | Severity | Issue Description |")
        out.append("| :--- | :--- | :--- | :--- |")
        for iss in data["issues"]:
            out.append(f"| {iss['id']} | {iss['row']} | `{iss['severity']}` | {iss['issue']} |")
        out.append("")

    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit project RAID log CSV registers.")
    parser.add_argument("file", help="Path to RAID CSV file (columns: id,type,description,owner,status,severity,due_date)")
    parser.add_argument("--json", action="store_true", help="Output audit results in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"[ERROR] Input file not found: {path}", file=sys.stderr)
        return 1

    with open(path, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    data = audit_raid_records(records)

    if args.json:
        res = json.dumps(data, indent=2)
    else:
        res = format_markdown_report(data)

    if args.output:
        Path(args.output).write_text(res, encoding="utf-8")
        print(f"[OK] Audit report written to {args.output}")
    else:
        print(res)

    return 0 if data["is_healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
