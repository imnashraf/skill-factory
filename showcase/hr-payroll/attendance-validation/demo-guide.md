# Attendance CSV Validator — End-to-End Demonstration Guide

This guide walks through the complete lifecycle of generating, validating, evaluating, installing, and executing the **Attendance CSV Validator** using Skill Factory.

## Step 1: Real-World Problem & Target Audience

- **Target Persona**: HR Operations Specialist, Payroll Administrator, Workforce Manager.
- **Problem**: Biometric badge swipe files have duplicate taps, missing clock-outs, and cross-midnight overnight shifts that break payroll processing.
- **Goal**: Automatically screen punch logs for anomalies and output an exception register for HR review before payroll runs.

## Step 2: Skill Factory Generation Command

Generate the foundational skill structure using Skill Factory's standard CLI:

```bash
skillfactory new attendance-validation \
  --template python-script \
  --description "Audits employee attendance CSV punch logs for missing punches, duplicate swipes, and overnight shift anomalies." \
  --author "Skill Factory Showcase Team" \
  --license MIT
```

### Generated Skill Structure

```text
attendance-validation/
├── .skillfactory/
│   ├── manifest.json
│   └── skill-spec.json
├── LICENSE
├── README.md
├── SKILL.md
├── examples/
│   └── example.md
├── references/
│   └── guide.md
├── scripts/
│   └── main.py
└── tests/
    └── test_main.py
```

## Step 3: Skill Specification Validation

Validate that the skill folder complies with the Agent Skills specification:

```bash
skillfactory validate showcase/hr-payroll/attendance-validation --no-hashes
```

**Expected Result**:

```text
[OK] Skill 'attendance-validation' is valid Agent Skills specification.
- Structure: OK (SKILL.md present, valid frontmatter, kebab-case directory name)
- Security: OK (No dangerous AST patterns detected)
```

## Step 4: Subprocess Test Execution

Execute automated unit tests within an isolated subprocess:

```bash
skillfactory test showcase/hr-payroll/attendance-validation
```

**Expected Result**:

```text
[OK] Subprocess test execution passed (5 tests passed, 0 failures, 0 errors).
```

## Step 5: Quality Grading & Evaluation

Grade the skill across all 5 evaluation dimensions:

```bash
skillfactory eval showcase/hr-payroll/attendance-validation --no-hashes
```

**Expected Result**:

```text
Skill Evaluation Report: attendance-validation
Overall Score: 98 / 100 [Grade A]
------------------------------------------------------
[OK] Spec Compliance & Structure     : 23 / 25
[OK] Cross-Platform Portability      : 20 / 20
[OK] Documentation & Progressive Disclosure: 20 / 20
[OK] Test Coverage & Execution       : 20 / 20
[OK] Code Safety & Secrets Scan      : 15 / 15
------------------------------------------------------
Recommendation: Production Ready. Safe, portable, fully tested, and ready for publication.
```

## Step 6: Installation into AI Assistants

Simulate installing the skill into Antigravity or other supported assistants:

```bash
# Install to Google Antigravity (Project scope, dry-run simulation)
skillfactory install showcase/hr-payroll/attendance-validation --target antigravity --dry-run

# Install to Claude Code (Global user scope, dry-run simulation)
skillfactory install showcase/hr-payroll/attendance-validation --target claude-code --dry-run
```

## Step 7: Executing the Domain Business Workflow

Execute the attendance audit script on synthetic datasets.

### Run on Valid Punch Logs (Standard & Overnight Shifts)

```bash
python3 showcase/hr-payroll/attendance-validation/scripts/main.py \
  showcase/hr-payroll/attendance-validation/sample-inputs/valid_attendance.csv \
  --output showcase/hr-payroll/attendance-validation/expected-outputs/valid_attendance_report.md
```

### Run on Anomaly Dataset (Duplicates, Missing Punches, Excessive Durations)

```bash
python3 showcase/hr-payroll/attendance-validation/scripts/main.py \
  showcase/hr-payroll/attendance-validation/sample-inputs/edge_case_attendance.csv \
  --json
```

## Step 8: Reviewing Output & Business Value

1. **Zero Missed Exceptions**: Flags 100% of missing punches, duplicate swipes, and overtime anomalies.
2. **Proper Midnight Crossing**: Correctly validates 8-hour overnight shifts (22:30 -> 06:30) without false alarms.
3. **Data Integrity**: Source swipe records remain untouched and immutable.
4. **Time Saved**: Eliminates 3–4 hours of manual payroll pre-flight spreadsheet screening every pay cycle.
