# Dependency Manifest Reviewer — End-to-End Demonstration Guide

This guide walks through the complete lifecycle of generating, validating, evaluating, installing, and executing the **Dependency Manifest Reviewer** using Skill Factory.

## Step 1: Real-World Problem & Target Audience

- **Target Persona**: AppSec Engineer, DevSecOps Lead, Senior Software Engineer.
- **Problem**: Insecure protocols, mutable git references, unpinned packages, and conflicting version constraints slip into manifests, exposing build pipelines to supply-chain risks.
- **Goal**: Deterministically audit dependency manifests offline, flag insecure configurations, and provide clear remediation guidance without making unverified CVE claims.

## Step 2: Skill Factory Generation Command

Generate the foundational skill structure using Skill Factory's standard CLI:

```bash
skillfactory new dependency-review \
  --template python-script \
  --description "Audits package dependency manifests for unpinned versions, conflicting requirements, and insecure HTTP/git references." \
  --author "Skill Factory Showcase Team" \
  --license MIT
```

### Generated Skill Structure

```text
dependency-review/
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
skillfactory validate showcase/cybersecurity/dependency-review --no-hashes
```

**Expected Result**:

```text
[OK] Skill 'dependency-review' is valid Agent Skills specification.
- Structure: OK (SKILL.md present, valid frontmatter, kebab-case directory name)
- Security: OK (No dangerous AST patterns detected)
```

## Step 4: Subprocess Test Execution

Execute automated unit tests within an isolated subprocess:

```bash
skillfactory test showcase/cybersecurity/dependency-review
```

**Expected Result**:

```text
[OK] Subprocess test execution passed (4 tests passed, 0 failures, 0 errors).
```

## Step 5: Quality Grading & Evaluation

Grade the skill across all 5 evaluation dimensions:

```bash
skillfactory eval showcase/cybersecurity/dependency-review --no-hashes
```

**Expected Result**:

```text
Skill Evaluation Report: dependency-review
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
skillfactory install showcase/cybersecurity/dependency-review --target antigravity --dry-run

# Install to Claude Code (Global user scope, dry-run simulation)
skillfactory install showcase/cybersecurity/dependency-review --target claude-code --dry-run
```

## Step 7: Executing the Domain Business Workflow

Execute the dependency review script on synthetic manifests.

### Run on Securely Pinned Manifest

```bash
python3 showcase/cybersecurity/dependency-review/scripts/main.py \
  showcase/cybersecurity/dependency-review/sample-inputs/valid_requirements.txt \
  --output showcase/cybersecurity/dependency-review/expected-outputs/valid_review_report.md
```

### Run on Edge-Case Manifest (HTTP links, mutable VCS, conflicts, unpinned)

```bash
python3 showcase/cybersecurity/dependency-review/scripts/main.py \
  showcase/cybersecurity/dependency-review/sample-inputs/edge_case_requirements.txt \
  --json
```

## Step 8: Reviewing Output & Business Value

1. **Supply Chain Defense**: Flags insecure HTTP endpoints and mutable git links before builds run.
2. **Conflict Resolution**: Pinpoints exact lines where conflicting package constraints clash.
3. **Credibility**: Distinguishes configuration defects from live CVEs; zero hallucinated vulnerability warnings.
4. **Time Saved**: Accelerates dependency security review from 30 minutes of manual inspection to sub-second automated verification.
