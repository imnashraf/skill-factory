---
name: financial-variance
description: Compares budgeted vs actual financial figures from CSV files, calculates exact Decimal variances, flags material exceptions, and produces executive variance registers.
---

# Financial Variance Analyzer

Deterministic financial analysis utility for comparing actual general ledger spending and revenue against approved budget plans using Python Decimal precision.

## When to Use This Skill

Activate this skill when:

- Analyzing monthly, quarterly, or annual budget variances across departments and cost centers.
- Auditing general ledger transactions against approved allocations.
- Identifying cost overruns and material variances exceeding configured percentage or dollar thresholds.
- Reconciling zero-budget scenarios, unspent budgets, and unbudgeted departmental expenses.

## Workflow Instructions

1. Prepare budget CSV (`account,cost_center,department,budget_amount`) and actuals CSV (`account,cost_center,department,actual_amount`).
2. Run standard variance analysis:

   ```bash
   python3 scripts/main.py budget.csv actuals.csv --output variance_report.md
   ```

3. Set custom materiality thresholds:

   ```bash
   python3 scripts/main.py budget.csv actuals.csv --threshold-pct 5.0 --threshold-abs 2000.00
   ```

4. Export structured JSON for upstream ERP or dashboard ingestion:

   ```bash
   python3 scripts/main.py budget.csv actuals.csv --json --output variance_report.json
   ```

## Limitations & Best Practices

- Does not connect directly to banking or live ERP APIs (SAP, Oracle, NetSuite).
- Operates locally on sanitized CSV exports.
- Requires standard numerical values in currency columns.
- Uses exact decimal arithmetic and never invents speculative qualitative justifications.
