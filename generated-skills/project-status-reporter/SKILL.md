---
name: project-status-reporter
description: Generates executive weekly project status reports from milestone and task CSV files, computing completion percentage, tracking progress, and flagging blocked deliverables.
---

# Project Status Reporter

Automate project governance and sprint status reporting from milestone spreadsheets without manual report preparation.

## When to Use This Skill

Activate this skill when:

- Compiling weekly or bi-weekly stakeholder progress reports.
- Calculating project completion percentages and milestone delivery health (Red/Amber/Green).
- Spotting blocked deliverables or overdue milestones before escalation.

## Workflow Instructions

1. Prepare milestones CSV (`id,name,owner,status,due_date`).
2. Run report generation:

   ```bash
   python3 scripts/main.py milestones.csv --title "Ecosystem Expansion" --output status.md
   ```

3. Export JSON metrics:

   ```bash
   python3 scripts/main.py milestones.csv --json
   ```

## Limitations & Best Practices

- Standard offline tabular parsing using pure Python.
- Does not modify external PM systems without human verification.
