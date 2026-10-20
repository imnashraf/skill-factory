# Attendance CSV Validation Report

## Summary for HR Review

- **Audit Status:** **ACTION REQUIRED (Exceptions Found)**
- **Total Swipe Records Audited:** 8
- **Valid & Clean Shifts:** 3
- **Flagged Exceptions:** 5
- **Applied Threshold Limits:** Shift duration between 1.0h and 14.0h

## Exception Register

| Line | Employee ID | Shift ID | Anomaly Type | Severity | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | `EMP-2001` | `SH-01` | `DUPLICATE_SWIPE` | **HIGH** | Duplicate clock-in punch '09:00:00' already recorded on line 2. |
| L4 | `EMP-2002` | `SH-02` | `MISSING_CLOCK_OUT` | **HIGH** | Incomplete shift: clock-in at '08:30:00' without corresponding clock-out. |
| L5 | `EMP-2003` | `SH-03` | `MISSING_CLOCK_IN` | **HIGH** | Missing clock-in punch for shift ending at '17:00:00'. |
| L7 | `EMP-2005` | `SH-05` | `EXCESSIVE_SHIFT_HOURS` | **HIGH** | Recorded shift duration is 16.50 hours (> 14.0h threshold). |
| L8 | `EMP-2006` | `SH-06` | `SHORT_SHIFT_ANOMALY` | **MEDIUM** | Recorded shift duration is 0.42 hours (< 1.0h minimum). |

## Governance & Compliance Notice

This utility performs validation of biometric swipe logs only. It does NOT compute payroll,
alter employee records, or determine wage entitlements.
