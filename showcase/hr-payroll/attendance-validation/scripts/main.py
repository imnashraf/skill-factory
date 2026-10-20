#!/usr/bin/env python3
"""Attendance CSV Validator (Showcase Demo 02).

Domain: HR and Payroll.
Audits employee time-and-attendance biometric swipe logs for missing punches,
duplicate swipes, overnight shifts, and anomalous shift durations without modifying
source records or attempting unauthorized payroll calculations.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EMP_ID_PATTERN = re.compile(r"^[A-Z0-9_-]{3,20}$", re.IGNORECASE)


def parse_timestamp_or_time(time_str: str, date_str: Optional[str] = None) -> Optional[datetime]:
    """Parse timestamp string supporting both full datetimes and time-only formats."""
    val = time_str.strip()
    if not val:
        return None

    # Full datetime formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            pass

    # Time-only formats with date context
    if date_str:
        d_val = date_str.strip()
        for d_fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
            try:
                base_date = datetime.strptime(d_val, d_fmt).date()
                for t_fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"):
                    try:
                        t_obj = datetime.strptime(val, t_fmt).time()
                        return datetime.combine(base_date, t_obj)
                    except ValueError:
                        pass
            except ValueError:
                pass

    return None


def validate_attendance_records(
    records: List[Dict[str, str]],
    max_shift_hours: float = 14.0,
    min_shift_hours: float = 1.0,
    emp_col: str = "employee_id",
    date_col: str = "date",
    clock_in_col: str = "clock_in",
    clock_out_col: str = "clock_out",
    shift_col: str = "shift_id",
) -> Dict[str, Any]:
    """Audit attendance records and return structured findings and statistics."""
    total_records = len(records)
    valid_count = 0
    anomalies: List[Dict[str, Any]] = []
    seen_swipes: Dict[Tuple[str, str, str], int] = {}

    for idx, row in enumerate(records, start=2):  # line 2 is first data row
        emp_id = (row.get(emp_col) or "").strip()
        dt_str = (row.get(date_col) or "").strip()
        cin_str = (row.get(clock_in_col) or "").strip()
        cout_str = (row.get(clock_out_col) or "").strip()
        shift_id = (row.get(shift_col) or f"SH-{idx}").strip()

        # 1. Employee ID validation
        if not emp_id:
            anomalies.append({
                "line": idx,
                "employee_id": "UNKNOWN",
                "shift_id": shift_id,
                "type": "MISSING_EMPLOYEE_ID",
                "severity": "HIGH",
                "message": "Missing employee identifier.",
            })
            continue

        if not EMP_ID_PATTERN.match(emp_id):
            anomalies.append({
                "line": idx,
                "employee_id": emp_id,
                "shift_id": shift_id,
                "type": "INVALID_EMPLOYEE_ID_FORMAT",
                "severity": "MEDIUM",
                "message": f"Employee identifier '{emp_id}' does not match expected format.",
            })

        # 2. Duplicate swipe detection
        if cin_str:
            swipe_key = (emp_id, dt_str, cin_str)
            if swipe_key in seen_swipes:
                prior_line = seen_swipes[swipe_key]
                anomalies.append({
                    "line": idx,
                    "employee_id": emp_id,
                    "shift_id": shift_id,
                    "type": "DUPLICATE_SWIPE",
                    "severity": "HIGH",
                    "message": f"Duplicate clock-in punch '{cin_str}' already recorded on line {prior_line}.",
                })
                continue
            seen_swipes[swipe_key] = idx

        # 3. Missing punch detection
        if not cin_str and not cout_str:
            anomalies.append({
                "line": idx,
                "employee_id": emp_id,
                "shift_id": shift_id,
                "type": "EMPTY_PUNCH_RECORD",
                "severity": "HIGH",
                "message": "Both clock-in and clock-out timestamps are empty.",
            })
            continue

        if not cin_str:
            anomalies.append({
                "line": idx,
                "employee_id": emp_id,
                "shift_id": shift_id,
                "type": "MISSING_CLOCK_IN",
                "severity": "HIGH",
                "message": f"Missing clock-in punch for shift ending at '{cout_str}'.",
            })
            continue

        if not cout_str:
            anomalies.append({
                "line": idx,
                "employee_id": emp_id,
                "shift_id": shift_id,
                "type": "MISSING_CLOCK_OUT",
                "severity": "HIGH",
                "message": f"Incomplete shift: clock-in at '{cin_str}' without corresponding clock-out.",
            })
            continue

        # 4. Timestamp parsing
        dt_in = parse_timestamp_or_time(cin_str, dt_str)
        dt_out = parse_timestamp_or_time(cout_str, dt_str)

        if not dt_in or not dt_out:
            anomalies.append({
                "line": idx,
                "employee_id": emp_id,
                "shift_id": shift_id,
                "type": "INVALID_TIMESTAMP_FORMAT",
                "severity": "MEDIUM",
                "message": f"Unparseable timestamp: clock_in='{cin_str}', clock_out='{cout_str}'.",
            })
            continue

        # 5. Overnight shift handling
        # If dates are the same and clock_out is earlier than clock_in, it is an overnight shift spanning midnight
        is_overnight = False
        if dt_out <= dt_in:
            if dt_str and dt_in.date() == dt_out.date():
                # Cross-midnight shift on single date record (e.g. 22:00 -> 06:00)
                dt_out_adjusted = dt_out + timedelta(days=1)
                is_overnight = True
                duration_hours = (dt_out_adjusted - dt_in).total_seconds() / 3600.0
            else:
                anomalies.append({
                    "line": idx,
                    "employee_id": emp_id,
                    "shift_id": shift_id,
                    "type": "NEGATIVE_DURATION_ERROR",
                    "severity": "CRITICAL",
                    "message": f"Clock-out ({dt_out.isoformat()}) precedes clock-in ({dt_in.isoformat()}).",
                })
                continue
        else:
            duration_hours = (dt_out - dt_in).total_seconds() / 3600.0
            if dt_out.date() > dt_in.date():
                is_overnight = True

        # 6. Shift duration threshold validation
        if duration_hours < min_shift_hours:
            anomalies.append({
                "line": idx,
                "employee_id": emp_id,
                "shift_id": shift_id,
                "type": "SHORT_SHIFT_ANOMALY",
                "severity": "MEDIUM",
                "message": f"Recorded shift duration is {duration_hours:.2f} hours (< {min_shift_hours:.1f}h minimum).",
            })
            continue

        if duration_hours > max_shift_hours:
            anomalies.append({
                "line": idx,
                "employee_id": emp_id,
                "shift_id": shift_id,
                "type": "EXCESSIVE_SHIFT_HOURS",
                "severity": "HIGH",
                "message": f"Recorded shift duration is {duration_hours:.2f} hours (> {max_shift_hours:.1f}h threshold).",
            })
            continue

        valid_count += 1

    return {
        "total_records": total_records,
        "valid_records": valid_count,
        "anomalies_count": len(anomalies),
        "is_clean": len(anomalies) == 0,
        "max_shift_hours": max_shift_hours,
        "min_shift_hours": min_shift_hours,
        "anomalies": anomalies,
    }


def format_markdown_report(data: Dict[str, Any], title: str = "Attendance CSV Validation Report") -> str:
    """Format attendance findings into clean GitHub-flavored markdown."""
    status_str = "**PASSED (Clean Dataset)**" if data["is_clean"] else "**ACTION REQUIRED (Exceptions Found)**"

    out: List[str] = [
        f"# {title}",
        "",
        "## Summary for HR Review",
        "",
        f"- **Audit Status:** {status_str}",
        f"- **Total Swipe Records Audited:** {data['total_records']}",
        f"- **Valid & Clean Shifts:** {data['valid_records']}",
        f"- **Flagged Exceptions:** {data['anomalies_count']}",
        f"- **Applied Threshold Limits:** Shift duration between {data['min_shift_hours']}h and {data['max_shift_hours']}h",
        "",
    ]

    if data["anomalies"]:
        out.append("## Exception Register")
        out.append("")
        out.append("| Line | Employee ID | Shift ID | Anomaly Type | Severity | Description |")
        out.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for a in data["anomalies"]:
            out.append(
                f"| L{a['line']} | `{a['employee_id']}` | `{a['shift_id']}` | "
                f"`{a['type']}` | **{a['severity']}** | {a['message']} |"
            )
        out.append("")

    out.append("## Governance & Compliance Notice")
    out.append("")
    out.append("This utility performs validation of biometric swipe logs only. It does NOT compute payroll,")
    out.append("alter employee records, or determine wage entitlements.")
    out.append("")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit employee attendance swipe CSV files for punch anomalies.")
    parser.add_argument("file", help="Path to attendance CSV file")
    parser.add_argument("--max-hours", type=float, default=14.0, help="Maximum allowable shift duration (default: 14.0)")
    parser.add_argument("--min-hours", type=float, default=1.0, help="Minimum valid shift duration (default: 1.0)")
    parser.add_argument("--emp-col", default="employee_id", help="Employee ID column name (default: employee_id)")
    parser.add_argument("--date-col", default="date", help="Date column name (default: date)")
    parser.add_argument("--clock-in-col", default="clock_in", help="Clock-in column name (default: clock_in)")
    parser.add_argument("--clock-out-col", default="clock_out", help="Clock-out column name (default: clock_out)")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"[ERROR] Input file not found: {path}", file=sys.stderr)
        return 1

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"[ERROR] Could not read file '{path}': {exc}", file=sys.stderr)
        return 1

    reader = csv.DictReader(content.splitlines())
    records = list(reader)

    data = validate_attendance_records(
        records,
        max_shift_hours=args.max_hours,
        min_shift_hours=args.min_hours,
        emp_col=args.emp_col,
        date_col=args.date_col,
        clock_in_col=args.clock_in_col,
        clock_out_col=args.clock_out_col,
    )

    if args.json:
        output_text = json.dumps(data, indent=2)
    else:
        output_text = format_markdown_report(data)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output_text, encoding="utf-8")
        print(f"[OK] Attendance validation report written to {args.output}")
    else:
        print(output_text)

    return 0 if data["is_clean"] else 2


if __name__ == "__main__":
    sys.exit(main())
