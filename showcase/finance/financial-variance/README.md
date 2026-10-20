# Showcase Demo 01 — Financial Variance Analyzer

Deterministic financial variance analysis utility comparing budgeted and actual figures using Python Decimal arithmetic.

## Quick Summary

- **Domain**: Finance & Accounting (Corporate FP&A / General Ledger Audit)
- **Problem**: Finance teams manually reconcile spreadsheets with formula drift and floating-point errors.
- **Solution**: Automated, deterministic comparison across cost centers and accounts with materiality filtering and source tracing.
- **Precision**: Exact Python `Decimal` quantization; zero division-by-zero risk on unbudgeted expenses.

## Package Contents

- [problem-statement.md](file:///Users/mna/skill-factory/skill-factory/showcase/finance/financial-variance/problem-statement.md): Business problem, user personas, input data specs, and governance boundaries.
- [demo-guide.md](file:///Users/mna/skill-factory/skill-factory/showcase/finance/financial-variance/demo-guide.md): Step-by-step terminal walkthrough for generation, validation, testing, grading, installation, and execution.
- [SKILL.md](file:///Users/mna/skill-factory/skill-factory/showcase/finance/financial-variance/SKILL.md): Agent Skills compliant instruction document.
- `scripts/main.py`: Fully executable reference script with Decimal precision.
- `tests/test_main.py`: Automated unit tests covering valid, invalid, and edge cases.
- `sample-inputs/`: Synthetic test datasets (valid, invalid, edge-case).
- `expected-outputs/`: Verified markdown reports and machine-readable JSON files.

## Quick Start Command

```bash
python3 showcase/finance/financial-variance/scripts/main.py \
  showcase/finance/financial-variance/sample-inputs/valid_budget.csv \
  showcase/finance/financial-variance/sample-inputs/valid_actuals.csv \
  --threshold-pct 10.0 \
  --threshold-abs 1000.0
```
