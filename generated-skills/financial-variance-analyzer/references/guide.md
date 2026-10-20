# Reference Guide: Financial Variance Analyzer

## Column Format Requirements

Input CSV files must contain at least:

1. `account`: String identifier for the departmental or ledger account.
2. `amount`: Numeric value representing budgeted or actual dollar amount.

## Materiality Calculation

A line item is flagged as material if:

- `|variance_percentage| >= threshold_pct` (default: 10.0%), OR
- `|variance_dollars| >= threshold_abs` (default: $1,000.00).
