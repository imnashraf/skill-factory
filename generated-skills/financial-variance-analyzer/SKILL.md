---
name: financial-variance-analyzer
description: Compares budgeted vs. actual financial figures from CSV files, calculates dollar and percentage variance, flags material exceptions, and produces executive reports.
---

# Financial Variance Analyzer

Deterministic financial analysis utility for comparing actual spending and revenue against budget plans without cloud dependencies.

## When to Use This Skill

Activate this skill when:

- Analyzing monthly or quarterly budget variances.
- Auditing departmental spend reports against approved allocations.
- Identifying cost overruns and material variances exceeding configured thresholds.

## Workflow Instructions

1. Prepare budget CSV (`account,amount`) and actuals CSV (`account,amount`).
2. Run variance analysis:

   ```bash
   python3 scripts/main.py budget.csv actuals.csv --output variance_report.md
   ```

3. Set custom materiality thresholds:

   ```bash
   python3 scripts/main.py budget.csv actuals.csv --threshold-pct 5.0 --threshold-abs 2000.0
   ```

## Limitations & Best Practices

- Does not connect to banking or ERP APIs autonomously.
- Uses local CSV files only.
- Relies on synthetic or sanitized financial data.
