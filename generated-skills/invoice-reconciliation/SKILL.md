---
name: invoice-reconciliation
description: Reconciles supplier invoices against purchase order registers, identifying price discrepancies, missing purchase order numbers, and duplicate billings.
---

# Invoice Reconciliation

Deterministic finance utility for automated line-item reconciliation between accounts payable invoices and approved purchase orders.

## When to Use This Skill

Activate this skill when:

- Performing three-way or two-way invoice reconciliation.
- Auditing vendor invoices against approved purchase order values.
- Detecting duplicate supplier invoice numbers prior to batch payment runs.

## Workflow Instructions

1. Prepare invoices CSV (`invoice_number,po_number,vendor,amount`) and PO CSV (`po_number,vendor,amount`).
2. Run reconciliation:

   ```bash
   python3 scripts/main.py invoices.csv purchase_orders.csv --output reconciliation_report.md
   ```

3. Run with custom dollar tolerance:

   ```bash
   python3 scripts/main.py invoices.csv purchase_orders.csv --tolerance 0.05
   ```

## Limitations & Best Practices

- Operates purely offline using standard tabular CSV exports.
- Does not autonomously trigger payment disbursements or modify ledger databases.
- Compliant with financial segregation of duties.
