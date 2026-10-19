---
name: raid-log-validator
description: Audits project RAID (Risks, Assumptions, Issues, Dependencies) log registers for missing owners, overdue resolution dates, unranked impact ratings, and invalid states.
---

# RAID Log Validator

Audit project Risk, Assumption, Issue, and Dependency registers for governance defects and overdue milestones.

## When to Use This Skill

Activate this skill when:
- Conducting weekly or monthly project management steering committee audits.
- Reviewing RAID log health across agile sprints or waterfall phases.
- Flagging unowned issues or overdue target resolution dates.

## Workflow Instructions

1. Prepare the RAID CSV (`id,type,description,owner,status,severity,due_date`).
2. Run validation:
   ```bash
   python3 scripts/main.py raid_log.csv --output audit_report.md
   ```
3. Export JSON:
   ```bash
   python3 scripts/main.py raid_log.csv --json
   ```

## Limitations & Best Practices

- Purely offline deterministic validation.
- Does not modify project tracking platforms (Jira, Linear, Asana) autonomously.
- Uses synthetic project codes and de-identified personnel names.
