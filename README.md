# Skill Factory

[![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen.svg)](.github/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.11%20%7C%203.13-blue.svg)](pyproject.toml)
[![Dependencies](https://img.shields.io/badge/dependencies-0%20(standard%20library)-success.svg)](skillfactory/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Specification](https://img.shields.io/badge/spec-agentskills.io-orange.svg)](https://agentskills.io/specification)
[![Status](https://img.shields.io/badge/status-development%20complete-success.svg)](PROJECT_CLOSURE.md)

**Skill Factory** is an open-source, local-first generator, validator, evaluator, package manager, and lifecycle system for **Agent Skills** conforming to the [Agent Skills open specification](https://agentskills.io/specification).

It bridges the gap between conversational AI prompts and production-grade tools across 8 major AI coding assistants—including **Claude Code**, **Google Antigravity**, **Cursor**, **OpenAI Codex**, **Windsurf**, **Continue**, **Cline**, and **GitHub Copilot**.

```text
   ┌───────────────────────────────────────────────────────────────┐
   │                       SKILL FACTORY                           │
   │                                                               │
   │  [1] Create a new skill (interactive interview)               │
   │  [2] Search local skill library                               │
   │  [3] Validate an existing skill folder                        │
   │  [4] Run skill automated tests                                │
   │  [5] Evaluate skill quality score (0–100)                     │
   │  [6] Scan skill for secrets and safety issues                 │
   │  [7] Platform health doctor (check AI agents)                 │
   │  [8] Install a skill into an AI tool                          │
   │  [9] List installed skills                                    │
   │  [10] Beginner guided walkthrough (step-by-step wizard)       │
   │  [11] AI-assisted skill creation (natural language)           │
   │  [12] Curated domain skill packs (browse & install)           │
   │  [0] Exit                                                     │
   │                                                               │
   │  100% Python Standard Library • Zero Paid APIs • Local-First  │
   └───────────────────────────────────────────────────────────────┘
```

---

## What Skill Factory Does & Does Not Do

To ensure complete transparency and prevent adoption friction, here are the explicit design boundaries of Skill Factory:

### What Skill Factory Does

- ✅ **Scaffolds Specification-Compliant Skills:** Creates standardized folders with validated YAML frontmatter (`name`, `description`), structured markdown instructions (`SKILL.md`), human documentation (`README.md`), unit tests (`tests/`), scripts (`scripts/`), and cryptographic SHA-256 manifests (`.skillfactory/manifest.json`).
- ✅ **Evaluates & Scores Quality (0–100):** Grades skills objectively against 5 dimensions: specification compliance, portability, progressive disclosure, test execution, and code safety.
- ✅ **Scans for Security Risks & Injections:** Static AST scanner flags dangerous calls (`eval`, `exec`, `os.system`, shell injection). Secrets scanner flags leaked AWS keys, GitHub tokens, and OpenAI/Anthropic keys. Hardened with 7 categories of prompt injection detection and symlink escape defense.
- ✅ **Manages Complete Lifecycles:** Installs skills into official AI agent directories, creates automatic timestamped backup snapshots before updates, performs single-command rollbacks, and cleanly uninstalls skills while preserving user data.
- ✅ **Curated Domain Skill Packs:** Ships with 5 curated domain packs (Office Productivity, Finance & ERP, HR & Workforce, Project Management, Developer & Security) containing 14 reference skills scoring Grade A (≥90/100).
- ✅ **Optional AI-Assisted Skill Creation:** Pluggable, provider-neutral synthesis engine (`skillfactory ai-create`) supporting local Ollama or compatible models with pre-execution AST safety quarantine and bounded test self-repair.
- ✅ **Runs 100% Locally & Offline:** Requires zero API subscriptions, zero third-party packages, zero account registration, and zero telemetry.

### What Skill Factory Does Not Do

- ❌ **It is not an autonomous "no-code" app creator:** In Offline Mode (`new`, `interview`), Skill Factory generates robust structural scaffolds, validated frontmatter, and test stubs. Domain business logic must be implemented by the developer or by a connected AI assistant.
- ❌ **It does not invent AI platform features:** It adheres strictly to each platform's documented skill discovery paths and capabilities. It does not force autonomous model invocation on platforms that only support manual slash commands or directory indexing.
- ❌ **It does not make external network requests:** Skill Factory will never secretly upload your skills, metrics, code, or telemetry to a remote server.

---

## Key Features

- ⚡ **Zero Third-Party Dependencies:** Pure Python standard-library implementation. Runs immediately on any machine with Python 3.9+ without `pip install` friction or virtual environments.
- 🔒 **Safe & Isolated Execution:** Subprocess test runner enforces an isolated 10-second timeout. Zip archive import strictly validates target paths against Zip-Slip traversal attacks (`../`), and installation defends against symlink escapes.
- 🎯 **Dual Console Entry Points:** Both `skillfactory` and `skill-factory` CLI commands installed out of the box.
- 🌐 **8 Supported AI Platforms:** Native discovery and installation for Claude Code, Google Antigravity, Cursor, OpenAI Codex, Windsurf, Continue, Cline, and GitHub Copilot with collision detection and alias normalization.
- 📦 **Automated Backups & Rollback:** Every update creates an immutable timestamped backup snapshot, enabling instant rollback if a new version breaks existing behavior.
- 🤖 **Optional AI Engine:** Synthesizes skills from natural language descriptions via local Ollama or OpenAI-compatible endpoints with AST safety interception and up to 3 automated test self-repair retries.

---

## Supported AI Platforms & Verification Levels

Skill Factory maps to official agent discovery paths defined in [`skillfactory/data/platforms.json`](skillfactory/data/platforms.json):

| Platform | Project Scope Folder | Global (User) Scope Folder | Verification Level & Activation Model |
| :--- | :--- | :--- | :--- |
| **Claude Code** | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | **Verified Autonomous Activation:** Host model matches prompt intent to `SKILL.md` description; also supports manual `/<skill-name>` command. |
| **Google Antigravity** | `.agents/skills/<name>/` | `~/.gemini/config/skills/` | **Verified Autonomous Activation:** Engine injects discovered skills into system prompt `<skills>` context; model autonomously reads `SKILL.md` when intent matches. |
| **Cursor** | `.agents/skills/<name>/`, `.cursor/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` | **Verified Directory Discovery:** Discovered in workspace or global folder; invoked via manual slash command `/<skill-name>` or explicit `@` context inclusion. |
| **OpenAI Codex** | `.agents/skills/<name>/` | `~/.agents/skills/` | **Simulated CLI Integration:** Discovered in `.agents/skills/`; invoked via CLI syntax `$<skill-name>`; respects `agents/openai.yaml` metadata. |
| **Windsurf** | `.codeium/windsurf/skills/<name>/` | `~/.codeium/windsurf/skills/<name>/` | **Verified Directory Discovery:** Discovered in Codeium Cascade workspace configuration. |
| **Continue** | `.continue/prompts/<name>/` | `~/.continue/prompts/<name>/` | **Verified Prompt / Tool Folder:** Discovered in Continue prompt/custom commands directory. |
| **Cline** | `.cline/skills/<name>/` | `~/.cline/skills/<name>/` | **Verified Workspace Skill Path:** Discovered in project `.cline/` root directory. |
| **GitHub Copilot** | `.github/skills/<name>/` | `~/.config/github-copilot/skills/<name>/` | **Verified Repository Instruction Path:** Discovered in `.github/` repository directory. |

Run `skillfactory doctor` to automatically detect which AI assistants are installed on your workstation.

---

## Quickstart

### Prerequisites

Python 3.9 or higher (macOS default Command Line Tools, Linux, or Windows).

### 1. Launch the Interactive Menu (Beginner Friendly)

```bash
# Clone the repository
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# Run the interactive menu (zero flags needed)
python3 -m skillfactory
```

*(On Windows, use `py -m skillfactory` or `python -m skillfactory`)*

### 2. Run the Beginner Guided Wizard

```bash
# Step-by-step walkthrough checking system health, choosing an assistant, and generating a skill
skillfactory guide
```

### 3. Install via pip

```bash
# Install from PyPI
pip install agent-skill-factory

# Or install locally from source
pip install .

# Run from anywhere via either command
skillfactory
skill-factory
```

Detailed operating-system walkthroughs:

- 🍏 [macOS Beginner Guide](docs/quickstart/macos.md)
- 🪟 [Windows Beginner Guide](docs/quickstart/windows.md)
- 🐧 [Linux Beginner Guide](docs/quickstart/linux.md)
- 📖 [Comprehensive Beginner Quickstart](docs/beginnerQuickstart.md)
- 📚 [Beginner Glossary](docs/glossary.md)

---

## End-to-End Walkthrough Examples

### A. Classic Deterministic Creation & Installation

```bash
# Step 1: Create a new skill
skillfactory new --name log-summarizer --description "Analyze server logs and output error distribution summaries."

# Step 2: Validate specification compliance, run tests, and evaluate
skillfactory validate generated-skills/log-summarizer
skillfactory test generated-skills/log-summarizer
skillfactory eval generated-skills/log-summarizer

# Step 3: Install the skill into your AI assistant (e.g. Claude Code or Antigravity)
skillfactory install generated-skills/log-summarizer --platform claude

# Step 4: Verify installed skill status
skillfactory list
```

### B. Curated Domain Skill Packs

```bash
# List all 5 available curated skill packs
skillfactory pack list

# Install the entire Finance & ERP Pack into Cursor
skillfactory pack install finance-erp --target cursor

# Verify pack integrity and test coverage
skillfactory pack verify finance-erp
```

### C. Optional AI-Assisted Skill Creation

```bash
# Synthesize a skill from natural language with AST safety interception and bounded self-repair
skillfactory ai-create "Compare two attendance logs and identify missing employees, duplicate records, and overtime hours" --name attendance-auditor
```

---

## Curated Domain Skill Packs (14 Reference Skills)

Skill Factory organizes reference skills into a 3-tier taxonomy (**Personal**, **Professional**, **Developer**) across 5 curated packs. Every included skill is tested and scores Grade A (≥90/100):

### 1. Office Productivity Pack (`office-productivity`)

- **Excel Comparison Engine** (`excel-comparison`): Pure standard-library `.xlsx` parser diffing spreadsheets cell-by-cell.
- **Smart File Organizer & Renamer** (`file-organizer`): Categorizes files by MIME/date with dry-run collision defense.
- **CSV Analytical Report Generator** (`csv-to-report`): Computes statistical summaries and outputs Markdown, HTML, and JSON.
- **Markdown Repository Validator** (`markdown-doc-validator`): Detects broken relative file links, unaligned tables, and untagged fences.
- **Structured Notes Formatter** (`structured-notes-formatter`): Transforms raw meeting notes into structured minutes with action item extraction.

### 2. Finance & ERP Pack (`finance-erp`)

- **Financial Variance Analyzer** (`financial-variance-analyzer`): Compares budget vs. actual figures, flagging percentage and absolute thresholds.
- **Invoice Reconciliation** (`invoice-reconciliation`): Reconciles vendor invoices against purchase orders, identifying mismatched totals and duplicate line items.

### 3. HR & Workforce Pack (`hr-workforce`)

- **Attendance CSV Validator** (`attendance-csv-validator`): Audits clock-in/out records for anomalies, missing punches, and negative durations.
- **Timesheet Reconciliation** (`timesheet-reconciliation`): Cross-references contractor timesheets against approved project rosters.

### 4. Project Management Pack (`project-management`)

- **RAID Log Validator** (`raid-log-validator`): Validates Risk, Assumption, Issue, and Dependency matrices against delivery standards.
- **Project Status Reporter** (`project-status-reporter`): Aggregates sprint updates and milestones into executive Markdown summaries.

### 5. Developer & Security Pack (`developer-security`)

- **Security & Configuration Scanner** (`security-config-scanner`): AST-based scanner detecting exposed API keys and permissive CORS wildcards.
- **Dependency Manifest Reviewer** (`dependency-manifest-reviewer`): Audits `requirements.txt` and `package.json` for unpinned or insecure dependencies.
- **Test Inventory Analyzer** (`test-inventory-analyzer`): Inventories automated tests, measuring coverage distribution and skipped test ratios.

---

## Real-World Use Cases Showcase

Skill Factory includes five comprehensive, post-release real-world use case demonstrations. Each demonstration packages an end-to-end business problem, synthetic datasets, deterministic reference execution workflows, automated unit test suites, expected golden outputs, and video recording scripts:

| Domain | Business Problem | Skill | Inputs | Outputs | Demonstration Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Finance & Accounting** | Manual spreadsheet reconciliation causes rounding drift, formula breaks, and division-by-zero on unbudgeted items. | `financial-variance` | `budget.csv`, `actuals.csv` | Executive Variance Register (Markdown/JSON) | [Finance Showcase](showcase/finance/financial-variance/README.md) |
| **HR & Payroll** | Biometric badge swipe files have duplicate taps, missing clock-outs, and cross-midnight overnight shift calculation errors. | `attendance-validation` | `attendance.csv` | HR Exception Register & Summary (Markdown/JSON) | [HR Showcase](showcase/hr-payroll/attendance-validation/README.md) |
| **Project Management** | Subjective project health reporting conceals overdue deliverables, active blockers, and unmitigated risks. | `project-status` | `milestones.csv`, `raid.csv` | Executive Status Dashboard & Action Summary | [PMO Showcase](showcase/project-management/project-status/README.md) |
| **Cybersecurity & AppSec** | Insecure protocols, mutable VCS links, duplicate versions, and unpinned dependencies introduce build risks. | `dependency-review` | `requirements.txt`, `package.json` | Supply Chain Audit Report & Guidance | [Security Showcase](showcase/cybersecurity/dependency-review/README.md) |
| **Software Engineering** | Teams lack quick visibility into which modules lack test suites and where duplicate or skipped tests exist. | `test-inventory` | Codebase (`src/`, `tests/`) | Test Suite Catalog & Gap Analysis | [QA Showcase](showcase/software-engineering/test-inventory/README.md) |

For comprehensive beginner walkthroughs, architecture notes, and video recording scripts, visit the [Showcase Documentation Landing Page](showcase/README.md).

---

## CLI Command Reference

All commands are available via `skillfactory <command>` or `skill-factory <command>`:

| Command | Description | Example |
| --- | --- | --- |
| `menu` | Opens the interactive numbered menu (default when run without args). | `skillfactory` |
| `guide` | Step-by-step interactive beginner onboarding wizard. | `skillfactory guide` |
| `new` | Directly generates a skill with command-line flags. | `skillfactory new --name my-tool --desc "Process log files"` |
| `interview` | Guided 5-question terminal interview or non-interactive JSON batch. | `skillfactory interview` |
| `ai-create` | Synthesizes a skill from natural language with AST safety interception. | `skillfactory ai-create "Extract tables from CSV files"` |
| `pack` | Browse, install, verify, and uninstall curated domain packs. | `skillfactory pack list` |
| `validate` | Validates YAML frontmatter, naming, structure, and SHA-256 hashes. | `skillfactory validate generated-skills/my-tool` |
| `doctor` | Inspects workstation, Python runtime, and reports installed AI platforms. | `skillfactory doctor` |
| `test` | Runs a skill's automated test suite in an isolated subprocess (10s timeout). | `skillfactory test generated-skills/my-tool` |
| `eval` | Computes 0–100 quality score and letter grade (Grade A–F). | `skillfactory eval generated-skills/my-tool` |
| `scan` | Scans for dangerous AST calls (`eval`, `exec`, `os.system`), prompt injections, and leaked keys. | `skillfactory scan generated-skills/my-tool` |
| `install` | Installs a skill into an AI platform with backup snapshotting. | `skillfactory install generated-skills/my-tool --platform cursor` |
| `list` | Lists all installed skills across all detected platforms. | `skillfactory list` |
| `update` | Updates an installed skill, detecting local modifications and backing up. | `skillfactory update my-tool --platform cursor` |
| `rollback` | Restores an installed skill to its previous backup snapshot. | `skillfactory rollback my-tool --platform cursor` |
| `uninstall` | Safely removes an installed skill, preserving user data files. | `skillfactory uninstall my-tool --platform cursor` |
| `install-self` | Installs Skill Factory itself into a chosen AI coding assistant. | `skillfactory install-self --platform claude` |
| `search` | Sub-millisecond offline keyword/tag search on library. | `skillfactory search log` |
| `export` | Packages a skill into a portable `.zip` with SHA-256 checksum sidecar. | `skillfactory export generated-skills/my-tool` |
| `import` | Safely extracts a `.zip` skill package with Zip-Slip defense. | `skillfactory import my-tool.zip` |
| `publish` | Generates a standalone repository with README, LICENSE, and CI. | `skillfactory publish generated-skills/my-tool --out-dir dist/` |

---

## Security & Privacy Model

Skill Factory adheres to strict host isolation and safety guarantees:

- **Local-First & Zero-Telemetry:** All operations execute locally. No code, skill names, descriptions, or parameters are ever transmitted over the network.
- **AST Danger Detection:** Source code is analyzed using Python's abstract syntax tree before execution to intercept forbidden patterns (`eval`, `exec`, `os.system`, `subprocess` with `shell=True`, and recursive filesystem deletions).
- **Prompt Injection Defense:** Multi-vector screening detects directive overrides, persona hijacks, hidden markup, exfiltration endpoints, and system prompt extraction attacks.
- **Symlink Escape Defense:** File copying and packaging strictly verify that symlinks do not escape the skill folder boundary to access sensitive host files.
- **Secrets & Credential Scanner:** Detects exposed AWS keys, GitHub tokens, OpenAI/Anthropic API keys, and PEM certificates.
- **Atomic Staging:** Files are generated in sibling staging directories (`.tmp-<uuid>`) and atomically renamed only upon successful manifest generation, preventing corrupt or half-written skills.
- **Zip-Slip Defense:** Archive extraction strictly verifies resolved destination paths to prevent path traversal attacks (`../`).
- **Subprocess Isolation:** Test execution runs in an isolated child process with a strict 10-second timeout, preventing hanging processes or memory exhaustion.

Review our full [Security Policy](SECURITY.md) and [Security Architecture](docs/securityAndPrivacy.md) for vulnerability reporting and threat modeling.

---

## Troubleshooting & FAQ

### 1. `python3: command not found` (Windows)

On Windows, the default Python launcher is `py`. Use:

```cmd
py -m skillfactory
```

Or ensure Python is added to your system `PATH` in the Windows installer.

### 2. "Destination already exists and is not managed by Skill Factory"

Skill Factory protects your pre-existing files. If a directory was created manually, Skill Factory refuses to overwrite it. To overwrite an unmanaged directory, pass `--force`:

```bash
skillfactory install generated-skills/my-skill --platform claude --force
```

### 3. "Skill has local modifications. Use --force to overwrite"

During `update`, Skill Factory checks current files against the original cryptographic manifest. If you edited files manually, it alerts you to prevent accidental data loss. Passing `--force` creates a backup snapshot and updates the files.

### 4. How do I test backward compatibility?

Skill Factory preserves full backward compatibility with the legacy Phase 0 generator:

```bash
python3 scripts/create_skill.py --name test-skill --description "Testing backward compatibility"
```

---

## Governance & Contributing

Skill Factory is an open-source project welcoming community contributions. Please review:

- [Contributing Guidelines](CONTRIBUTING.md)
- [Project Closure Report](PROJECT_CLOSURE.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Architecture Decisions Log](docs/decisions.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

---

## License

MIT License. Copyright (c) 2026 Skill Factory Contributors.

All skills generated by Skill Factory are the **100% exclusive property of the user** under whichever license the user selects. Skill Factory does not require viral attribution in your generated skills.
