# Project Status Reporter — Problem Statement

## Domain

Project and Program Management (Enterprise PMO / Agile Delivery Governance).

## Business Problem

Program managers, delivery leads, and PMO analysts spend significant manual effort every week compiling updates across project tracking sheets, milestone schedules, and RAID logs (Risks, Assumptions, Issues, Dependencies). In typical organizations:

- Status reporting is subjective: team members mark projects "Green" despite active unmitigated risks or overdue dependencies.
- Milestones slip quietly because overdue deadlines are not systematically reconciled against calendar benchmark dates.
- Critical risks and blocked deliverables are buried in spreadsheet tabs rather than elevated in a prioritized action summary.
- Managers often invent estimated completion percentages or speculative narratives instead of relying on verified tracking entries.

## Intended Users

- **Project & Program Managers**: Consolidating cross-functional delivery progress into weekly executive summaries.
- **PMO Directors & Portfolio Leads**: Monitoring portfolio health across multiple workstreams using standardized RAG governance rules.
- **Scrum Masters & Engineering Leads**: Surfacing blockers and high-severity dependencies requiring managerial intervention.

## Input Data Requirements

1. **Milestones CSV**: `id,name,owner,due_date,status,completion_pct`
2. **RAID Log CSV (Optional but recommended)**: `id,type,title,severity,status,owner`

## Key Capabilities & Deterministic Governance Rules

- **Deterministic RAG Calculation**:
  - **RED**: Triggered if ANY milestone is `BLOCKED`, OR >= 2 milestones are overdue, OR >= 1 `CRITICAL` active risk exists.
  - **AMBER**: Triggered if exactly 1 milestone is overdue, OR >= 1 `HIGH` active risk exists, OR unmitigated active issues exist.
  - **GREEN**: All milestones proceed on schedule with zero unmitigated high/critical risks.
- **Action Summary Prioritization**: Extracts an explicit executive action list targeting blocked deliverables, overdue items, and high/critical risks with assigned owners.
- **Progress Tracking**: Aggregates milestone completion rate percentage from verifiable entries.
- **Strict Data Integrity**: Source logs remain untouched; zero speculative justifications or invented updates.

## Known Limitations

- Relies on local CSV exports; does not autonomously sync with cloud issue trackers (Jira, Linear, Asana).
- Evaluates project status against documented point-in-time benchmark rules; does not perform Monte Carlo schedule simulations.
