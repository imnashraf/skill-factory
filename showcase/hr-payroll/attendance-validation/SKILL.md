---
name: attendance-validation
description: Audits employee attendance CSV punch logs for missing punches, duplicate swipes, and overnight shift anomalies without payroll modification.
---

# Attendance CSV Validator

Deterministic workforce operations utility for validating employee clock-in and clock-out biometric logs, detecting anomalies, and producing HR audit registers.

## When to Use This Skill

Activate this skill when:

- Reviewing employee timecard punch logs prior to payroll processing.
- Identifying missing clock-in or clock-out entries requiring managerial resolution.
- Detecting duplicate badge swipes and hardware bounce anomalies.
- Auditing overnight shifts spanning midnight and overtime duration anomalies (>14h).

## Workflow Instructions

1. Prepare attendance CSV (`employee_id,shift_id,date,clock_in,clock_out`).
2. Run standard attendance audit:

   ```bash
   python3 scripts/main.py attendance.csv --output attendance_report.md
   ```

3. Set custom shift duration limits:

   ```bash
   python3 scripts/main.py attendance.csv --min-hours 2.0 --max-hours 12.0
   ```

4. Export machine-readable JSON for HRIS integration:

   ```bash
   python3 scripts/main.py attendance.csv --json --output attendance_report.json
   ```

## Limitations & Best Practices

- Validates time logs for physical and chronological completeness only.
- Does not compute wage payments, overtime premiums, or tax withholdings.
- Does not alter source attendance logs.
- Operates locally on sanitized CSV exports without connecting to external payroll APIs.
