# Financial Variance Analyzer — End-to-End Demonstration Guide

This guide walks through the complete lifecycle of creating, testing, grading, installing, and executing the **Financial Variance Analyzer** using Skill Factory.

## Step 1: Real-World Problem & Target Audience

- **Target Persona**: FP&A Analyst, Financial Controller, Operations Lead.
- **Problem**: Monthly variance reconciliation between budgets and actuals takes hours in spreadsheets and causes floating-point calculation errors.
- **Goal**: Deterministically audit spend against budget with exact decimal precision, flag material exceptions, and produce an executive management summary.

## Step 2: Skill Factory Generation Command

Generate the foundational skill structure using Skill Factory's standard CLI:

```bash
skillfactory new financial-variance \
  --template python-script \
  --description "Compares budget vs actual financial figures using exact Decimal arithmetic, flags material variances, and produces executive reports." \
  --author "Skill Factory Showcase Team" \
  --license MIT
```

### Generated Skill Structure

The command creates an Agent Skills specification compliant folder:

```text
financial-variance/
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

Validate that the skill folder complies with the Agent Skills specification and naming rules:

```bash
skillfactory validate showcase/finance/financial-variance --no-hashes
```

**Expected Result**:

```text
[OK] Skill 'financial-variance' is valid Agent Skills specification.
- Structure: OK (SKILL.md present, valid frontmatter, kebab-case directory name)
- Security: OK (No dangerous AST patterns detected)
```

## Step 4: Subprocess Test Execution

Execute automated unit tests within an isolated subprocess (with 10-second timeout enforcement):

```bash
skillfactory test showcase/finance/financial-variance
```

**Expected Result**:

```text
[OK] Subprocess test execution passed (6 tests passed, 0 failures, 0 errors).
```

## Step 5: Quality Grading & Evaluation

Grade the skill across all 5 evaluation dimensions:

```bash
skillfactory eval showcase/finance/financial-variance --no-hashes
```

**Expected Result**:

```text
Skill Evaluation Report: financial-variance
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
skillfactory install showcase/finance/financial-variance --target antigravity --dry-run

# Install to Claude Code (Global user scope, dry-run simulation)
skillfactory install showcase/finance/financial-variance --target claude-code --dry-run
```

## Step 7: Executing the Domain Business Workflow

Now execute the actual deterministic financial reconciliation script on synthetic datasets.

### Run on Valid Monthly Data

```bash
python3 showcase/finance/financial-variance/scripts/main.py \
  showcase/finance/financial-variance/sample-inputs/valid_budget.csv \
  showcase/finance/financial-variance/sample-inputs/valid_actuals.csv \
  --threshold-pct 10.0 \
  --threshold-abs 1000.0 \
  --output showcase/finance/financial-variance/expected-outputs/valid_variance_report.md
```

### Run on Edge-Case Data (Zero Budgets, Boundaries)

```bash
python3 showcase/finance/financial-variance/scripts/main.py \
  showcase/finance/financial-variance/sample-inputs/edge_case_budget.csv \
  showcase/finance/financial-variance/sample-inputs/edge_case_actuals.csv \
  --json
```

## Step 8: Reviewing Output & Business Value

1. **Deterministic Accuracy**: Zero floating-point drift; exact to the penny.
2. **Materiality Filter**: Instantly isolates the 6 critical exceptions out of 11 items.
3. **Auditability**: Direct line-level trace back to original source spreadsheets.
4. **Time Saved**: Reduces a 90-minute spreadsheet exercise to an instantaneous 10ms audit.
