# Financial Variance Analyzer — Problem Statement

## Domain

Finance and Accounting (Corporate FP&A / General Ledger Audit).

## Business Problem

Finance and FP&A teams spend countless hours each month reconciling departmental budgets against actual general ledger spend across cost centers, accounts, and operating units. In typical organizations:

- Variance analysis is performed manually across disparate spreadsheet exports, leading to formula errors and unverified assumptions.
- Standard floating-point arithmetic in ad-hoc scripts causes rounding drift and pennies mismatches in executive reporting.
- Zero-budget items (unbudgeted spend) frequently trigger division-by-zero errors or crash automated batch runs.
- Auditors struggle to trace summary variances back to original CSV row records.
- Analysts often invent speculative qualitative explanations for variances rather than documenting the deterministic mathematical variance facts.

## Intended Users

- **Financial Planning & Analysis (FP&A) Analysts**: Requiring automated month-end variance registers.
- **Financial Controllers & Finance Directors**: Reviewing material threshold exceptions across departments.
- **Cost Center Managers**: Tracking operational spend against approved budget allocations.
- **Internal Audit & Compliance Teams**: Verifying exact audit trails from variance tables to source ledger records.

## Input Data Requirements

Two CSV files with consistent schema:

1. **Budget File**: `account,cost_center,department,budget_amount`
2. **Actuals File**: `account,cost_center,department,actual_amount`

## Key Capabilities & Deterministic Rules

- **Exact Decimal Arithmetic**: Implemented exclusively using Python's `Decimal` standard library module, quantized to two decimal places with `ROUND_HALF_UP`.
- **Composite Key Matching**: Line items are joined by `(account, cost_center)`, enabling multi-department isolation for shared GL accounts.
- **Zero-Budget Handling**: Deterministically flags unbudgeted spend (+100.0%) and unspent budget (-100.0%) without division-by-zero exceptions.
- **Configurable Materiality**: Flags variances exceeding percentage thresholds (e.g., >= 10.0%) OR absolute currency thresholds (e.g., >= $1,000.00).
- **Source Record Tracing**: Every line item explicitly cites source CSV row numbers (`L{budget} / L{actual}`).
- **Governance**: Factual, audit-ready reporting with zero invented justifications.

## Known Limitations

- Operates strictly offline on local CSV exports; does not autonomously connect to live banking or ERP APIs (SAP, Oracle, NetSuite).
- Relies on synthetic or sanitized input data.
- Does not predict future revenue or generate multi-year cash flow forecasts.
