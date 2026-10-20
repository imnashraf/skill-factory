# Showcase Demo 03 — Project Status Reporter

Deterministic delivery governance utility consolidating project milestones and RAID logs into executive status reports and action summaries.

## Quick Summary

- **Domain**: Project & Program Management (Enterprise PMO / Delivery Governance)
- **Problem**: Project health reporting is subjective and prone to concealing overdue items and critical blockers.
- **Solution**: Automated, rule-based RAG calculation from milestone dates and RAID severities with an explicit executive action register.
- **Governance**: Factual, evidence-based status; zero speculative narrative or unverified progress extrapolation.

## Package Contents

- [problem-statement.md](file:///Users/mna/skill-factory/skill-factory/showcase/project-management/project-status/problem-statement.md): Business problem, user personas, input data specs, and governance boundaries.
- [demo-guide.md](file:///Users/mna/skill-factory/skill-factory/showcase/project-management/project-status/demo-guide.md): Step-by-step terminal walkthrough for generation, validation, testing, grading, installation, and execution.
- [SKILL.md](file:///Users/mna/skill-factory/skill-factory/showcase/project-management/project-status/SKILL.md): Agent Skills compliant instruction document.
- `scripts/main.py`: Fully executable reference script with RAG evaluation.
- `tests/test_main.py`: Automated unit tests covering valid, invalid, and edge cases.
- `sample-inputs/`: Synthetic test datasets (valid, invalid, edge-case).
- `expected-outputs/`: Verified markdown reports and machine-readable JSON files.

## Quick Start Command

```bash
python3 showcase/project-management/project-status/scripts/main.py \
  showcase/project-management/project-status/sample-inputs/valid_milestones.csv \
  --raid-file showcase/project-management/project-status/sample-inputs/valid_raid.csv \
  --as-of-date 2026-10-20
```
