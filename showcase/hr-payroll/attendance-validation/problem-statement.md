# Attendance CSV Validator — Problem Statement

## Domain

Human Resources and Payroll Operations (Workforce Time & Attendance Audit).

## Business Problem

HR and payroll administration teams receive raw biometric punch records and badge reader logs from physical turnstiles, timeclocks, and web portals. In practice:

- Raw punch files frequently contain duplicate card swipes (employees tapping twice in quick succession).
- Employees occasionally forget to clock out, leading to open-ended shifts with missing timestamps.
- Overnight shifts spanning midnight (e.g., 22:00 to 06:00 next morning) are erroneously flagged as negative-duration shifts by naive spreadsheet formulas.
- Excessive shift durations (e.g., shifts over 14 hours) or accidental 15-minute punches pass unnoticed into payroll batches.
- Manual inspection across thousands of monthly records delays payroll finalization and creates labor law compliance exposure.

## Intended Users

- **HR Operations Specialists**: Screening time-card swipe logs before submitting to payroll.
- **Payroll Administrators**: Auditing employee punch data for completeness and validity.
- **Operations & Facility Managers**: Monitoring shift compliance, overtime anomalies, and badge reader hardware reliability.

## Input Data Requirements

A standardized attendance CSV export containing:

`employee_id,shift_id,date,clock_in,clock_out`

## Key Capabilities & Deterministic Rules

- **Duplicate Punch Detection**: Flags identical consecutive clock-ins for the same employee and date.
- **Missing Punch Isolation**: Flags missing clock-ins (`MISSING_CLOCK_IN`) or missing clock-outs (`MISSING_CLOCK_OUT`).
- **Overnight Shift Support**: Correctly computes durations across midnight without throwing negative duration errors.
- **Configurable Shift Thresholds**:
  - Enforces minimum shift duration (default: >= 1.0 hour).
  - Flags excessive shift duration (default: > 14.0 hours).
- **Non-Destructive Exception Register**: Surfaces an audit-ready register of row numbers, employee IDs, and anomaly categories while leaving source data untouched.

## Governance & Compliance Boundaries

- **Strictly No Payroll Calculation**: This tool validates time records for operational completeness; it does not calculate wages, taxes, overtime premiums, or gross-to-net pay.
- **No Record Modification**: Source punch logs are never edited or overwritten.
