# Showcase Demo 02 — Attendance CSV Validator

Deterministic workforce operations utility auditing employee timecard punch logs for missing punches, duplicate swipes, and overnight shift anomalies.

## Quick Summary

- **Domain**: HR & Payroll (Workforce Operations / Timecard Audit)
- **Problem**: HR teams spend hours sorting through punch records to find missing clock-outs, double swipes, and overnight shift errors.
- **Solution**: Automated pre-payroll screening that detects anomalies and generates an exception register while leaving source data intact.
- **Governance**: Zero payroll calculations; zero modification of employee records.

## Package Contents

- [problem-statement.md](file:///Users/mna/skill-factory/skill-factory/showcase/hr-payroll/attendance-validation/problem-statement.md): Business problem, user personas, input data specs, and compliance boundaries.
- [demo-guide.md](file:///Users/mna/skill-factory/skill-factory/showcase/hr-payroll/attendance-validation/demo-guide.md): Step-by-step terminal walkthrough for generation, validation, testing, grading, installation, and execution.
- [SKILL.md](file:///Users/mna/skill-factory/skill-factory/showcase/hr-payroll/attendance-validation/SKILL.md): Agent Skills compliant instruction document.
- `scripts/main.py`: Fully executable reference script with overnight shift detection.
- `tests/test_main.py`: Automated unit tests covering valid, invalid, and edge cases.
- `sample-inputs/`: Synthetic test datasets (valid, invalid, edge-case).
- `expected-outputs/`: Verified markdown reports and machine-readable JSON files.

## Quick Start Command

```bash
python3 showcase/hr-payroll/attendance-validation/scripts/main.py \
  showcase/hr-payroll/attendance-validation/sample-inputs/valid_attendance.csv
```
