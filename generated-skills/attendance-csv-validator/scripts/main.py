#!/usr/bin/env python3
"""Attendance CSV Validator (HR & Workforce Pack).

Validates employee clock-in/clock-out logs, detecting missing punch-outs,
anomalous shifts (>12h), negative duration entries, and duplicate swipes.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_time_str(val: str) -> Optional[datetime]:
    """Parse common time strings like '09:00', '09:00:00', '2026-10-20 09:00'."""
    val = val.strip()
    if not val:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            pass
    return None


def validate_attendance_records(records: List[Dict[str, str]]) -> Dict[str, Any]:
    """Validate list of attendance rows and return structured findings."""
    total_records = len(records)
    valid_count = 0
    anomalies: List[Dict[str, Any]] = []
    seen_swipes: Dict[str, str] = {}

    for idx, row in enumerate(records, start=1):
        emp_id = row.get("employee_id", "").strip() or f"Row-{idx}"
        dt_str = row.get("date", "").strip()
        cin_str = row.get("clock_in", "").strip()
        cout_str = row.get("clock_out", "").strip()

        # Check duplicate swipe
        swipe_key = f"{emp_id}_{dt_str}_{cin_str}"
        if cin_str and swipe_key in seen_swipes:
            anomalies.append({
                "row": idx,
                "employee_id": emp_id,
                "type": "DUPLICATE_SWIPE",
                "message": f"Duplicate clock-in swipe detected at {cin_str}.",
            })
            continue
        if cin_str:
            seen_swipes[swipe_key] = "seen"

        # Missing clock in
        if not cin_str:
            anomalies.append({
                "row": idx,
                "employee_id": emp_id,
                "type": "MISSING_CLOCK_IN",
                "message": "Missing clock-in timestamp.",
            })
            continue

        # Missing clock out
        if not cout_str:
            anomalies.append({
                "row": idx,
                "employee_id": emp_id,
                "type": "MISSING_CLOCK_OUT",
                "message": "Incomplete shift: clock-in recorded without matching clock-out.",
            })
            continue

        # Parse times
        t_in = parse_time_str(cin_str)
        t_out = parse_time_str(cout_str)

        if not t_in or not t_out:
            anomalies.append({
                "row": idx,
                "employee_id": emp_id,
                "type": "INVALID_TIMESTAMP_FORMAT",
                "message": f"Unrecognized time format: in='{cin_str}', out='{cout_str}'.",
            })
            continue

        duration_hours = (t_out - t_in).total_seconds() / 3600.0

        if duration_hours < 0:
            anomalies.append({
                "row": idx,
                "employee_id": emp_id,
                "type": "NEGATIVE_DURATION",
                "message": f"Clock-out ({cout_str}) occurs before clock-in ({cin_str}).",
            })
            continue

        if duration_hours > 14.0:
            anomalies.append({
                "row": idx,
                "employee_id": emp_id,
                "type": "EXCESSIVE_OVERTIME_ANOMALY",
                "message": f"Recorded duration is {duration_hours:.1f} hours (> 14h limit).",
            })
            continue

        valid_count += 1

    return {
        "total_records": total_records,
        "valid_records": valid_count,
        "anomaly_count": len(anomalies),
        "is_clean": len(anomalies) == 0,
        "anomalies": anomalies,
    }


def format_report_markdown(data: Dict[str, Any]) -> str:
    """Format attendance validation findings as GitHub-flavored markdown."""
    out = ["# Attendance CSV Validation Report", ""]
    out.append("## Summary Statistics")
    out.append(f"- **Total Records Analyzed:** {data['total_records']}")
    out.append(f"- **Valid Shifts:** {data['valid_records']}")
    out.append(f"- **Anomalies / Flagged Records:** {data['anomaly_count']}")
    status_str = "**PASSED (Clean)**" if data["is_clean"] else "**FAILED (Anomalies Found)**"
    out.append(f"- **Overall Audit Status:** {status_str}")
    out.append("")

    if data["anomalies"]:
        out.append("## Flagged Anomalies")
        out.append("| Row | Employee ID | Anomaly Type | Description |")
        out.append("| :--- | :--- | :--- | :--- |")
        for a in data["anomalies"]:
            out.append(f"| {a['row']} | {a['employee_id']} | `{a['type']}` | {a['message']} |")
        out.append("")

    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit attendance clock-in/out CSV files for errors and anomalies.")
    parser.add_argument("file", help="Path to attendance CSV (columns: employee_id,date,clock_in,clock_out)")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"[ERROR] Input file not found: {path}", file=sys.stderr)
        return 1

    with open(path, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    data = validate_attendance_records(records)

    if args.json:
        res = json.dumps(data, indent=2)
    else:
        res = format_report_markdown(data)

    if args.output:
        Path(args.output).write_text(res, encoding="utf-8")
        print(f"[OK] Audit report written to {args.output}")
    else:
        print(res)

    return 0 if data["is_clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
