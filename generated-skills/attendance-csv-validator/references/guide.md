# Reference Guide: Attendance CSV Validator

## Anomaly Codes

- `DUPLICATE_SWIPE`: Identical employee and timestamp recorded more than once.
- `MISSING_CLOCK_IN`: Clock-out recorded without initial punch.
- `MISSING_CLOCK_OUT`: Incomplete shift without clock-out.
- `NEGATIVE_DURATION`: Clock-out precedes clock-in.
- `EXCESSIVE_OVERTIME_ANOMALY`: Shift length exceeds 14 continuous hours.
