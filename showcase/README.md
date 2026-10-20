# Skill Factory — Real-World Use Case Showcase

Welcome to the **Skill Factory Real-World Use Case Showcase**. This repository area demonstrates how developers, business analysts, security engineers, and operations managers can use Skill Factory to build, test, evaluate, and deploy high-utility Agent Skills that solve practical problems across enterprise domains.

---

## What is Skill Factory?

**Skill Factory** is a free, open-source framework and CLI toolchain designed to generate, validate, test, evaluate, package, and install **Agent Skills** conforming to the open [Agent Skills Specification](https://agentskills.io).

Agent Skills are specialized folders containing instruction guides (`SKILL.md`), executable deterministic scripts, test suites, and cryptographic manifests that allow AI coding agents and platforms (such as Google Antigravity, Claude Code, Cursor, and Codex) to autonomously execute specialized workflows with 100% offline predictability.

---

## Why Would Someone Use It?

1. **Eliminate Prompt Drift**: Instead of repeatedly pasting fragile 500-word prompts into chat interfaces, you package deterministic logic into reusable, version-controlled skills.
2. **Deterministic Mathematical Accuracy**: Large Language Models (LLMs) frequently hallucinate or make arithmetic errors on spreadsheets. Skill Factory skills use deterministic Python scripts (e.g. Python `Decimal`) to perform exact calculations.
3. **Cross-Platform Portability**: Write your skill once and install it seamlessly across Google Antigravity, Claude Code, Cursor, or Codex without rewriting instructions.
4. **Automated Quality Grading**: Evaluates every skill across 5 dimensions (Spec Compliance, Portability, Documentation, Test Coverage, Code Safety) with a transparent 0–100 score.
5. **Security Quarantine**: Built-in AST safety scanning prevents dangerous shell execution, prompt injections, and hardcoded credential leaks.

---

## What Problem Does Each Demonstration Solve?

This showcase provides five production-grade reference demonstrations:

| Demo | Domain | Business Problem Solved | Key Metric / Capability | Demonstration Guide |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Finance & Accounting** | Manual spreadsheet reconciliation causes rounding drift and formula errors. | Exact Decimal arithmetic, zero-budget handling, materiality filtering, source line tracing. | [Financial Variance Guide](file:///Users/mna/skill-factory/skill-factory/showcase/finance/financial-variance/demo-guide.md) |
| **02** | **HR & Payroll** | Biometric badge swipe logs have duplicate taps, missing punches, and midnight-crossing errors. | Cross-midnight overnight shift support, duplicate swipe isolation, exception register. | [Attendance Validation Guide](file:///Users/mna/skill-factory/skill-factory/showcase/hr-payroll/attendance-validation/demo-guide.md) |
| **03** | **Project Management** | Subjective RAG status reporting hides overdue deliverables and critical blockers. | Rule-based deterministic RAG governance, overdue milestone alerts, executive action register. | [Project Status Guide](file:///Users/mna/skill-factory/skill-factory/showcase/project-management/project-status/demo-guide.md) |
| **04** | **Cybersecurity & AppSec** | Insecure protocols, mutable git branch links, and unpinned packages slip into manifests. | Static configuration audit (`DEP-01` to `DEP-06`), conflict detection; zero false CVE claims. | [Dependency Review Guide](file:///Users/mna/skill-factory/skill-factory/showcase/cybersecurity/dependency-review/demo-guide.md) |
| **05** | **Software Engineering** | Teams lack visibility into which modules lack test suites and where duplicate tests exist. | Sub-second AST test discovery, module-to-test mapping, untested module warnings. | [Test Inventory Guide](file:///Users/mna/skill-factory/skill-factory/showcase/software-engineering/test-inventory/demo-guide.md) |

---

## How Do I Install Skill Factory?

Skill Factory runs on any system with Python 3.10+ and requires **zero external third-party dependencies** (Python standard library only).

```bash
# Clone the repository
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# Install in editable mode or build distribution
python3 -m pip install -e .

# Verify installation
skillfactory --version
```

---

## How Do I Create My First Skill?

Generate an Agent Skill in seconds using one of five built-in template families:

```bash
skillfactory new my-custom-skill \
  --template python-script \
  --description "Parses incoming data files and outputs structured audit registers." \
  --author "Your Name" \
  --license MIT
```

Available template families:

- `python-script`: Executable deterministic Python script with tests and documentation.
- `file-transform`: Structured file parsing, normalization, and conversion.
- `checklist-review`: Step-by-step quality, safety, or compliance checklist.
- `workflow-runbook`: Multi-step operational playbook for engineering and sysadmins.
- `instructions-only`: High-leverage prompt guide without executable code.

---

## How Do I Test and Install a Skill?

Skill Factory provides a complete lifecycle toolchain:

```bash
# 1. Validate structure and YAML frontmatter
skillfactory validate my-custom-skill

# 2. Run unit tests in an isolated 10-second subprocess sandbox
skillfactory test my-custom-skill

# 3. Grade skill quality across 5 dimensions (0-100 score)
skillfactory eval my-custom-skill

# 4. Perform AST safety and secret leak inspection
skillfactory scan my-custom-skill

# 5. Install into Google Antigravity (Project scope)
skillfactory install my-custom-skill --target antigravity

# Or install for Claude Code, Cursor, or Codex
skillfactory install my-custom-skill --target claude-code
```

---

## How Do I Run the Demonstrations?

Execute any demonstration workflow directly from the command line:

```bash
# Demo 01: Financial Variance Analyzer
python3 showcase/finance/financial-variance/scripts/main.py \
  showcase/finance/financial-variance/sample-inputs/valid_budget.csv \
  showcase/finance/financial-variance/sample-inputs/valid_actuals.csv

# Demo 02: Attendance CSV Validator
python3 showcase/hr-payroll/attendance-validation/scripts/main.py \
  showcase/hr-payroll/attendance-validation/sample-inputs/valid_attendance.csv

# Demo 03: Project Status Reporter
python3 showcase/project-management/project-status/scripts/main.py \
  showcase/project-management/project-status/sample-inputs/valid_milestones.csv \
  --raid-file showcase/project-management/project-status/sample-inputs/valid_raid.csv

# Demo 04: Dependency Manifest Reviewer
python3 showcase/cybersecurity/dependency-review/scripts/main.py \
  showcase/cybersecurity/dependency-review/sample-inputs/edge_case_requirements.txt

# Demo 05: Test Inventory Analyzer
python3 showcase/software-engineering/test-inventory/scripts/main.py \
  showcase/software-engineering/test-inventory/sample-inputs/edge_case_repo
```

To run all five demonstrations and their automated tests end-to-end, execute:

```bash
python3 -m unittest tests/test_showcase.py -v
```

---

## How Do I Build My Own Skill for Another Business Problem?

1. **Define the Problem**: Pinpoint the manual calculation, validation, or compliance task your team repeats.
2. **Choose a Template**: Select `python-script` for deterministic data processing or `file-transform` for data conversion.
3. **Scaffold with CLI**: Run `skillfactory new <skill-name> --template <template>`.
4. **Implement Reference Script**: Place deterministic Python logic in `scripts/main.py` using Python standard library modules (`csv`, `decimal`, `json`, `datetime`, `re`, `ast`).
5. **Add Automated Tests**: Write unit tests in `tests/test_main.py` covering valid, invalid, and boundary inputs.
6. **Evaluate & Refine**: Run `skillfactory eval <skill-dir>` until your skill achieves **Grade A (>= 90/100)**.
7. **Deploy**: Run `skillfactory install <skill-dir> --target antigravity` and invoke the skill in your pair programming workflows.
