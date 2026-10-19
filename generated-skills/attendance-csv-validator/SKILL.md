---
name: attendance-csv-validator
description: Validates employee clock-in and clock-out attendance CSV files, detecting missing punch-outs, excessive overtime shifts, duplicate swipes, and time calculation anomalies.
---

# Attendance CSV Validator

Audit workforce time-and-attendance CSV logs for payroll compliance and operational anomalies.

## When to Use This Skill

Activate this skill when:

- Auditing employee badge swipe or time clock CSV exports.
- Identifying missing clock-out timestamps before payroll processing.
- Detecting duplicate badge swipes and anomalous shift durations.

## Workflow Instructions

1. Prepare the attendance CSV (`employee_id,date,clock_in,clock_out`).
2. Run the audit validator:

   ```bash
   python3 scripts/main.py attendance.csv --output audit_report.md
   ```

3. Output machine-readable JSON:

   ```bash
   python3 scripts/main.py attendance.csv --json
   ```

## Limitations & Best Practices

- Operates strictly offline on exported CSV tabular logs.
- Does not modify HRIS or biometric clock databases.
- Relies on synthetic or de-identified workforce records.
