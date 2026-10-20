#!/usr/bin/env python3
"""Project Status Reporter (Project Management Pack).

Generates executive weekly status reports from project milestone and sprint task CSV files,
calculating completion percentage, tracking velocity, and highlighting blocked or overdue deliverables.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_status_summary(
    milestones: List[Dict[str, str]],
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Compute status analytics across milestones."""
    today = reference_date or date.today()
    total = len(milestones)
    completed = 0
    in_progress = 0
    blocked = 0
    not_started = 0
    overdue_count = 0

    detailed_items: List[Dict[str, Any]] = []

    for m in milestones:
        m_id = m.get("id", "").strip()
        name = m.get("name", "").strip()
        status = m.get("status", "").strip().upper()
        owner = m.get("owner", "").strip()
        due_str = m.get("due_date", "").strip()

        is_overdue = False
        if due_str and status not in ("COMPLETED", "DONE", "CLOSED"):
            try:
                dt = datetime.strptime(due_str, "%Y-%m-%d").date()
                if dt < today:
                    is_overdue = True
                    overdue_count += 1
            except ValueError:
                pass

        if status in ("COMPLETED", "DONE", "CLOSED"):
            completed += 1
        elif status in ("IN_PROGRESS", "ACTIVE"):
            in_progress += 1
        elif status in ("BLOCKED", "STALLED"):
            blocked += 1
        else:
            not_started += 1

        detailed_items.append({
            "id": m_id,
            "name": name,
            "owner": owner,
            "status": status,
            "due_date": due_str,
            "is_overdue": is_overdue,
        })

    completion_pct = (completed / total * 100.0) if total > 0 else 0.0

    overall_health = "Green"
    if blocked > 0 or overdue_count > 1:
        overall_health = "Red"
    elif in_progress > 0 and overdue_count == 1:
        overall_health = "Amber"

    return {
        "report_date": today.isoformat(),
        "total_milestones": total,
        "completed": completed,
        "in_progress": in_progress,
        "blocked": blocked,
        "not_started": not_started,
        "overdue_count": overdue_count,
        "completion_percentage": round(completion_pct, 1),
        "overall_health": overall_health,
        "milestones": detailed_items,
    }


def format_markdown_report(data: Dict[str, Any], project_title: str = "Project Delivery") -> str:
    """Format status metrics into clean GitHub-flavored markdown."""
    out = [f"# {project_title} — Weekly Status Report", ""]
    out.append(f"**As of:** {data['report_date']} | **Overall Health:** `{data['overall_health']}`")
    out.append("")
    out.append("## Progress Dashboard")
    out.append(f"- **Completion Rate:** {data['completion_percentage']}% ({data['completed']} / {data['total_milestones']} milestones done)")
    out.append(f"- **In Progress:** {data['in_progress']}")
    out.append(f"- **Blocked Deliverables:** {data['blocked']}")
    out.append(f"- **Overdue Milestones:** {data['overdue_count']}")
    out.append("")
    out.append("## Milestones Tracker")
    out.append("| ID | Milestone Name | Owner | Due Date | Status | Overdue? |")
    out.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for item in data["milestones"]:
        overdue_str = "**YES**" if item["is_overdue"] else "No"
        out.append(
            f"| {item['id']} | {item['name']} | {item['owner']} | "
            f"{item['due_date']} | `{item['status']}` | {overdue_str} |"
        )
    out.append("")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate weekly status report from project milestones CSV.")
    parser.add_argument("file", help="Path to milestones CSV file (columns: id,name,owner,status,due_date)")
    parser.add_argument("--title", default="Project Delivery", help="Project report title")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"[ERROR] Input file not found: {path}", file=sys.stderr)
        return 1

    with open(path, "r", encoding="utf-8") as f:
        milestones = list(csv.DictReader(f))

    data = generate_status_summary(milestones)

    if args.json:
        res = json.dumps(data, indent=2)
    else:
        res = format_markdown_report(data, project_title=args.title)

    if args.output:
        Path(args.output).write_text(res, encoding="utf-8")
        print(f"[OK] Status report written to {args.output}")
    else:
        print(res)

    return 0


if __name__ == "__main__":
    sys.exit(main())
