# Video Recording Script: Demo 02 — Attendance CSV Validator

**Duration**: 75 seconds (1m 15s)  
**Format**: Terminal Screen Recording + Voiceover  
**Target Audience**: HR Directors, Payroll Administrators, Workforce Managers  

---

## Scene 1: Business Problem Hook (0:00 – 0:12)

**Visual**: Camera focuses on a raw biometric clock-in file with double-swipes and missing timestamps.  
**Voiceover**:  
> "Payroll teams lose entire mornings hunting down missing punch-outs, duplicate badge taps, and overnight shifts that break payroll batches. Let's see how Skill Factory audits thousands of swipes in milliseconds."

---

## Scene 2: Synthetic Dataset Introduction (0:12 – 0:22)

**Visual**: Terminal displays head of `sample-inputs/edge_case_attendance.csv`.  

```bash
cat showcase/hr-payroll/attendance-validation/sample-inputs/edge_case_attendance.csv
```

**Voiceover**:  
> "Here is a typical raw facility swipe file containing standard shifts, overnight shifts bridging midnight, double taps, and forgotten clock-outs."

---

## Scene 3: Skill Factory Lifecycle (0:22 – 0:38)

**Visual**: Operator runs validation, tests, and evaluation.  

```bash
skillfactory validate showcase/hr-payroll/attendance-validation --no-hashes
skillfactory eval showcase/hr-payroll/attendance-validation --no-hashes
```

**Voiceover**:  
> "Using the Skill Factory CLI, we validate our attendance skill and run automated tests in an isolated sandbox. It scores 98 out of 100 with zero AST security violations."

---

## Scene 4: Workflow Execution & Actual Results (0:38 – 0:58)

**Visual**: Operator executes the attendance audit script.  

```bash
python3 showcase/hr-payroll/attendance-validation/scripts/main.py \
  showcase/hr-payroll/attendance-validation/sample-inputs/edge_case_attendance.csv
```

**Voiceover**:  
> "Instantly, the validator audits eight swipe events. It correctly validates the cross-midnight shift without throwing negative duration errors, while isolating duplicate badge taps on line 3, missing clock-outs on line 4, and a 16.5-hour excessive overtime shift on line 7."

---

## Scene 5: Closing Statement & Next Steps (0:58 – 1:15)

**Visual**: Terminal displays exception register and dry-run installation.  

```bash
skillfactory install showcase/hr-payroll/attendance-validation --target antigravity --dry-run
```

**Voiceover**:  
> "Source attendance records remain 100% immutable and unedited, with zero payroll calculations performed. Deploy to Antigravity, Cursor, or Claude Code in seconds with Skill Factory."
