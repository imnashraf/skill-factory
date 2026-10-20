---
name: project-status
description: Consolidates project milestone trackers and RAID logs, calculating RAG delivery health and action summaries from documented governance rules.
---

# Project Status Reporter

Deterministic delivery governance utility for evaluating project health, tracking milestone completion percentages, identifying overdue deliverables, and synthesizing RAID logs into executive summaries.

## When to Use This Skill

Activate this skill when:

- Preparing weekly or monthly executive project delivery reports.
- Evaluating objective project health (Red, Amber, Green) against documented benchmark rules.
- Isolating blocked deliverables and overdue milestone commitments requiring escalation.
- Consolidating RAID logs (Risks, Assumptions, Issues, Dependencies) into actionable summaries.

## Workflow Instructions

1. Prepare milestones CSV (`id,name,owner,due_date,status,completion_pct`).
2. Optional: Prepare RAID log CSV (`id,type,title,severity,status,owner`).
3. Run project status generation:

   ```bash
   python3 scripts/main.py milestones.csv --raid-file raid.csv --output status_report.md
   ```

4. Set explicit benchmark as-of date:

   ```bash
   python3 scripts/main.py milestones.csv --as-of-date 2026-10-20 --output status_report.md
   ```

5. Export structured JSON for leadership dashboards:

   ```bash
   python3 scripts/main.py milestones.csv --raid-file raid.csv --json --output status_report.json
   ```

## Limitations & Best Practices

- Does not connect to live cloud trackers (Jira, Linear, Asana).
- Operates locally on sanitized CSV exports.
- Evaluates deadlines against the specified benchmark date.
- Does not invent project progress updates or speculate on unverified completion rates.
