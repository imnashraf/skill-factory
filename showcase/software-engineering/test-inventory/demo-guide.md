# Test Inventory Analyzer — End-to-End Demonstration Guide

This guide walks through the complete lifecycle of generating, validating, evaluating, installing, and executing the **Test Inventory Analyzer** using Skill Factory.

## Step 1: Real-World Problem & Target Audience

- **Target Persona**: QA Lead, Software Architect, DevSecOps Engineer.
- **Problem**: Engineering teams cannot easily see what tests exist, which modules have 0 test files, or where tests are duplicated or skipped without running slow runtime instrumentation.
- **Goal**: Rapidly catalog test suites, detect duplicate test cases, map tests to source modules, and flag untested components.

## Step 2: Skill Factory Generation Command

Generate the foundational skill structure using Skill Factory's standard CLI:

```bash
skillfactory new test-inventory \
  --template python-script \
  --description "Scans codebases using AST to catalog test suites, detect duplicate test cases, and identify untested source modules." \
  --author "Skill Factory Showcase Team" \
  --license MIT
```

### Generated Skill Structure

```text
test-inventory/
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
skillfactory validate showcase/software-engineering/test-inventory --no-hashes
```

**Expected Result**:

```text
[OK] Skill 'test-inventory' is valid Agent Skills specification.
- Structure: OK (SKILL.md present, valid frontmatter, kebab-case directory name)
- Security: OK (No dangerous AST patterns detected)
```

## Step 4: Subprocess Test Execution

Execute automated unit tests within an isolated subprocess:

```bash
skillfactory test showcase/software-engineering/test-inventory
```

**Expected Result**:

```text
[OK] Subprocess test execution passed (4 tests passed, 0 failures, 0 errors).
```

## Step 5: Quality Grading & Evaluation

Grade the skill across all 5 evaluation dimensions:

```bash
skillfactory eval showcase/software-engineering/test-inventory --no-hashes
```

**Expected Result**:

```text
Skill Evaluation Report: test-inventory
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
skillfactory install showcase/software-engineering/test-inventory --target antigravity --dry-run

# Install to Claude Code (Global user scope, dry-run simulation)
skillfactory install showcase/software-engineering/test-inventory --target claude-code --dry-run
```

## Step 7: Executing the Domain Business Workflow

Execute the test inventory script on synthetic codebases.

### Run on Fully Mapped Repository (100% Module-to-Test Mapping)

```bash
python3 showcase/software-engineering/test-inventory/scripts/main.py \
  showcase/software-engineering/test-inventory/sample-inputs/valid_repo \
  --src-dir src \
  --tests-dir tests \
  --output showcase/software-engineering/test-inventory/expected-outputs/valid_inventory_report.md
```

### Run on Edge-Case Repository (Untested Modules, Duplicates, Skipped Tests)

```bash
python3 showcase/software-engineering/test-inventory/scripts/main.py \
  showcase/software-engineering/test-inventory/sample-inputs/edge_case_repo \
  --src-dir src \
  --tests-dir tests \
  --json
```

## Step 8: Reviewing Output & Business Value

1. **Coverage Blind Spots**: Instantly highlights source modules that lack any matching test suite.
2. **Suite Cleanliness**: Surfaces duplicate test functions and dormant `@skip` decorators.
3. **Execution Speed**: Audits thousands of lines of code in under 10 milliseconds via AST parsing without running code.
4. **Clarity**: Clearly distinguishes static structural inventory from dynamic line-coverage instrumentation.
