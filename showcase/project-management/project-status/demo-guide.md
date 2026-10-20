# Project Status Reporter — End-to-End Demonstration Guide

This guide walks through the complete lifecycle of generating, validating, evaluating, installing, and executing the **Project Status Reporter** using Skill Factory.

## Step 1: Real-World Problem & Target Audience

- **Target Persona**: Project & Program Manager, PMO Director, Agile Delivery Lead.
- **Problem**: Status reporting is often subjective, masking overdue deadlines, blocked items, and critical risks until too late.
- **Goal**: Deterministically evaluate delivery health against documented RAG governance rules, surface overdue milestones, and produce a prioritized action summary for leadership.

## Step 2: Skill Factory Generation Command

Generate the foundational skill structure using Skill Factory's standard CLI:

```bash
skillfactory new project-status \
  --template python-script \
  --description "Consolidates project milestone trackers and RAID logs, calculating RAG delivery health and action summaries." \
  --author "Skill Factory Showcase Team" \
  --license MIT
```

### Generated Skill Structure

```text
project-status/
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
skillfactory validate showcase/project-management/project-status --no-hashes
```

**Expected Result**:

```text
[OK] Skill 'project-status' is valid Agent Skills specification.
- Structure: OK (SKILL.md present, valid frontmatter, kebab-case directory name)
- Security: OK (No dangerous AST patterns detected)
```

## Step 4: Subprocess Test Execution

Execute automated unit tests within an isolated subprocess:

```bash
skillfactory test showcase/project-management/project-status
```

**Expected Result**:

```text
[OK] Subprocess test execution passed (4 tests passed, 0 failures, 0 errors).
```

## Step 5: Quality Grading & Evaluation

Grade the skill across all 5 evaluation dimensions:

```bash
skillfactory eval showcase/project-management/project-status --no-hashes
```

**Expected Result**:

```text
Skill Evaluation Report: project-status
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
skillfactory install showcase/project-management/project-status --target antigravity --dry-run

# Install to Claude Code (Global user scope, dry-run simulation)
skillfactory install showcase/project-management/project-status --target claude-code --dry-run
```

## Step 7: Executing the Domain Business Workflow

Execute the status reporting script on synthetic project updates.

### Run on Valid Project (On-Schedule, Green Health)

```bash
python3 showcase/project-management/project-status/scripts/main.py \
  showcase/project-management/project-status/sample-inputs/valid_milestones.csv \
  --raid-file showcase/project-management/project-status/sample-inputs/valid_raid.csv \
  --as-of-date 2026-10-20 \
  --output showcase/project-management/project-status/expected-outputs/valid_project_report.md
```

### Run on Edge-Case Project (Blocked Deliverable, Overdue Items, Red Health)

```bash
python3 showcase/project-management/project-status/scripts/main.py \
  showcase/project-management/project-status/sample-inputs/edge_case_milestones.csv \
  --raid-file showcase/project-management/project-status/sample-inputs/edge_case_raid.csv \
  --as-of-date 2026-10-20 \
  --json
```

## Step 8: Reviewing Output & Business Value

1. **Objective RAG Governance**: Project health is calculated mathematically from deadlines and severities, removing human reporting bias.
2. **Action Summary Prioritization**: Explicitly surfaces blocked milestones and critical risks with assigned owners.
3. **Auditability**: All progress percentages reflect verifiable source entries without speculative narratives.
4. **Time Saved**: Eliminates 2 hours of manual report formatting and alignment meetings each week.
