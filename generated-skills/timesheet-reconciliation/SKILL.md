---
name: timesheet-reconciliation
description: Compares employee logged project timesheet hours against approved project budget allocations, detecting overruns, under-utilization, and billing discrepancies.
---

# Timesheet Reconciliation

Automate workforce timesheet auditing and project budget allocation checks without external ERP dependencies.

## When to Use This Skill

Activate this skill when:
- Reviewing weekly or monthly contractor and employee timesheet submissions.
- Auditing project billable hours against client statements of work (SOW).
- Spotting resource overallocation across multiple initiatives.

## Workflow Instructions

1. Prepare timesheet CSV (`employee_id,project_code,hours`) and budget CSV (`employee_id,project_code,allocated_hours`).
2. Run reconciliation:
   ```bash
   python3 scripts/main.py timesheets.csv budgets.csv --output report.md
   ```

## Limitations & Best Practices

- Operates purely offline using standard tabular CSV files.
- Uses synthetic employee IDs and project codes for privacy.
