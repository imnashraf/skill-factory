# Reference Guide: RAID Log Validator

## Standard Field Definitions

- `id`: Unique identifier (e.g. `R-101`, `I-204`).
- `type`: Must be `RISK`, `ASSUMPTION`, `ISSUE`, or `DEPENDENCY`.
- `description`: Summary of the item (minimum 5 chars).
- `owner`: Responsible individual or squad lead.
- `status`: Must be `OPEN`, `IN_PROGRESS`, `CLOSED`, `BLOCKED`, or `MITIGATED`.
- `severity`: Must be `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
- `due_date`: Expected resolution date in `YYYY-MM-DD` format.
