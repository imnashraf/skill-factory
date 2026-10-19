# Skill Factory

[![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen.svg)](.github/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.11%20%7C%203.13-blue.svg)](pyproject.toml)
[![Dependencies](https://img.shields.io/badge/dependencies-0%20(standard%20library)-success.svg)](skillfactory/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Specification](https://img.shields.io/badge/spec-agentskills.io-orange.svg)](https://agentskills.io/specification)

**Skill Factory** is an open-source, local-first generator, validator, evaluator, and lifecycle manager for **Agent Skills** conforming to the [Agent Skills open specification](https://agentskills.io/specification).

It bridges the gap between conversational AI prompts and production-grade tools for AI coding assistants—including **Claude Code**, **Google Antigravity**, **Cursor**, and **OpenAI Codex**.

```text
   ┌───────────────────────────────────────────────────────────────┐
   │                       SKILL FACTORY                           │
   │                                                               │
   │  [1] Create new skill (interactive interview)                 │
   │  [2] Create new skill (direct command)                        │
   │  [3] Validate a skill                                         │
   │  [4] Run skill tests                                          │
   │  [5] Evaluate skill quality score (0-100)                     │
   │  [6] Detect installed AI platforms (doctor)                   │
   │  [7] Install a skill to an AI platform                        │
   │  [8] Search skill library                                     │
   │  [9] Exit                                                     │
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
- ✅ **Scans for Security Risks:** Static AST scanner flags dangerous calls (`eval`, `exec`, `os.system`, shell injection). Secrets scanner flags leaked AWS keys, GitHub tokens, and OpenAI/Anthropic keys.
- ✅ **Manages Complete Lifecycles:** Installs skills into official AI agent directories, creates automatic timestamped backup snapshots before updates, performs single-command rollbacks, and cleanly uninstalls skills while preserving user data.
- ✅ **Runs 100% Locally & Offline:** Requires zero API subscriptions, zero third-party packages, zero account registration, and zero cloud connectivity.

### What Skill Factory Does Not Do

- ❌ **It is not an autonomous "no-code" app creator:** In Offline Mode (`new`, `interview`), Skill Factory generates robust structural scaffolds, validated frontmatter, and test stubs. Domain business logic must be implemented by the developer or by a connected AI assistant.
- ❌ **It does not invent AI platform features:** It adheres strictly to each platform's documented skill discovery paths and capabilities. It does not force autonomous model invocation on platforms that only support manual slash commands or directory indexing.
- ❌ **It does not make external network requests:** Skill Factory will never secretly upload your skills, metrics, code, or telemetry to a remote server.

---

## Key Features

- ⚡ **Zero Third-Party Dependencies:** Pure Python standard-library implementation. Runs immediately on any machine with Python 3.9+ without `pip install` friction or virtual environments.
- 🔒 **Safe & Isolated Execution:** Subprocess test runner enforces an isolated 10-second timeout. Zip archive import strictly validates target paths against Zip-Slip traversal attacks (`../`).
- 🎯 **Dual-Mode Operation:**
  - **Host-AI Mode:** Leverages your connected AI coding assistant (Claude, Cursor, Codex, Antigravity) via the root [`SKILL.md`](SKILL.md) to generate complete domain logic and tests. No Skill Factory API key needed.
  - **Offline Mode:** 5-minute guided terminal interview or batch JSON parameters generating deterministic, verifiable templates with honest capability placeholders.
- 🌐 **Multi-Platform Compatibility:** Native discovery and installation for Claude Code, Cursor, Codex, and Google Antigravity with collision detection and platform alias normalization (`claude`, `openai`, `google`, `agy`).
- 📦 **Automated Backups & Rollback:** Every update creates an immutable timestamped backup snapshot, enabling instant rollback if a new version breaks existing behavior.

---

## Supported AI Platforms & Verification Levels

Skill Factory maps to official agent discovery paths defined in [`skillfactory/data/platforms.json`](skillfactory/data/platforms.json):

| Platform | Project Scope Folder | Global (User) Scope Folder | Verification Level & Activation Model |
| --- | --- | --- | --- |
| **Claude Code** | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | **Verified Autonomous Activation:** Host model matches prompt intent to `SKILL.md` description; also supports manual `/<skill-name>` command. |
| **Google Antigravity** | `.agents/skills/<name>/` | `~/.gemini/config/skills/` | **Verified Autonomous Activation:** Engine injects discovered skills into system prompt `<skills>` context; model autonomously reads `SKILL.md` when intent matches. |
| **Cursor** | `.agents/skills/<name>/`, `.cursor/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` | **Verified Directory Discovery:** Discovered in workspace or global folder; invoked via manual slash command `/<skill-name>` or explicit `@` context inclusion. |
| **OpenAI Codex** | `.agents/skills/<name>/` | `~/.agents/skills/` | **Simulated CLI Integration:** Discovered in `.agents/skills/`; invoked via CLI syntax `$<skill-name>`; respects `agents/openai.yaml` metadata. |

Run `python3 -m skillfactory doctor` to automatically detect which AI assistants are installed on your workstation.

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

### 2. Or Install via pip (Global Command)

```bash
# Install the candidate package or local clone
pip install .

# Run from anywhere
skillfactory
```

Detailed operating-system walkthroughs:

- 🍏 [macOS Beginner Guide](docs/quickstart/macos.md)
- 🪟 [Windows Beginner Guide](docs/quickstart/windows.md)
- 🐧 [Linux Beginner Guide](docs/quickstart/linux.md)
- 📖 [Comprehensive Beginner Quickstart](docs/beginnerQuickstart.md)
- 📚 [Beginner Glossary](docs/glossary.md)

---

## End-to-End Walkthrough Example

Here is a complete lifecycle demonstration from scratch in 4 simple commands:

```bash
# Step 1: Create a new skill
python3 -m skillfactory new \
  --name log-summarizer \
  --description "Analyze server access logs and output error distribution summaries."

# Step 2: Validate specification compliance and run tests
python3 -m skillfactory validate generated-skills/log-summarizer
python3 -m skillfactory test generated-skills/log-summarizer
python3 -m skillfactory eval generated-skills/log-summarizer

# Step 3: Install the skill into your AI assistant (e.g. Claude Code or Antigravity)
python3 -m skillfactory install generated-skills/log-summarizer --platform claude

# Step 4: Verify installed skill status
python3 -m skillfactory list
```

If you ever need to restore a previous version or remove the skill:

```bash
# Rollback to pre-update backup snapshot
python3 -m skillfactory rollback log-summarizer --platform claude

# Safely uninstall (removes only tracked files, preserving your data)
python3 -m skillfactory uninstall log-summarizer --platform claude
```

---

## Generated Skill Anatomy

Every skill generated by Skill Factory strictly complies with the [Agent Skills standard](https://agentskills.io/specification):

```text
generated-skills/my-skill/
├── SKILL.md                 # YAML frontmatter + structured AI instructions
├── README.md                # Human documentation and quickstart
├── scripts/
│   └── main.py              # Self-contained, executable script
├── tests/
│   └── test_main.py         # Automated unit test suite
├── references/              # Detailed guides, schemas, reference data
│   └── guide.md
└── .skillfactory/
    └── manifest.json        # Cryptographic SHA-256 file manifest
```

---

## CLI Command Reference

All commands are available via `python3 -m skillfactory <command>` or direct `skillfactory <command>` when installed.

| Command | Description | Example |
| --- | --- | --- |
| `menu` | Opens the interactive numbered menu (default when run without args). | `skillfactory` |
| `new` | Directly generates a skill with command-line flags. | `skillfactory new --name my-tool --desc "Process log files"` |
| `interview` | Guided 5-question terminal interview or non-interactive JSON batch. | `skillfactory interview` |
| `validate` | Validates YAML frontmatter, naming, structure, and SHA-256 hashes. | `skillfactory validate generated-skills/my-tool` |
| `doctor` | Inspects workstation, Python runtime, and reports installed AI platforms. | `skillfactory doctor` |
| `test` | Runs a skill's automated test suite in an isolated subprocess (10s timeout). | `skillfactory test generated-skills/my-tool` |
| `eval` | Computes 0–100 quality score and letter grade (Grade A–F). | `skillfactory eval generated-skills/my-tool` |
| `scan` | Scans for dangerous AST calls (`eval`, `exec`, `os.system`) and leaked keys. | `skillfactory scan generated-skills/my-tool` |
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

## Curated Reference Examples & Demos

Skill Factory ships with 5 production-grade reference skills in [`examples/`](examples/) and [`generated-skills/`](generated-skills/), each scoring Grade A (≥ 90/100) on the quality rubric:

1. **Excel Comparison Engine** ([`generated-skills/excel-comparison/`](generated-skills/excel-comparison/)): Pure standard-library `.xlsx` parser diffing spreadsheets cell-by-cell.
2. **Security & Configuration Scanner** ([`generated-skills/security-config-scanner/`](generated-skills/security-config-scanner/)): AST-based scanner detecting exposed API keys and permissive CORS wildcards.
3. **Smart File Organizer & Renamer** ([`generated-skills/file-organizer/`](generated-skills/file-organizer/)): Categorizes files by MIME/date with dry-run collision defense.
4. **CSV Analytical Report Generator** ([`generated-skills/csv-to-report/`](generated-skills/csv-to-report/)): Computes statistical summaries and outputs Markdown, responsive HTML, and JSON.
5. **Markdown Repository Validator** ([`generated-skills/markdown-doc-validator/`](generated-skills/markdown-doc-validator/)): Detects broken relative file links, unaligned tables, and untagged code fences.

Run the reproducible demonstration suite:

```bash
# Execute all 5 demonstrations with real sample inputs
python3 scripts/run_demos.py
```

See [docs/demonstrations.md](docs/demonstrations.md) for full input/output documentation.

---

## Security & Privacy Model

Skill Factory adheres to strict host isolation and safety guarantees:

- **Local-First & Offline:** All operations execute locally. No code, skill names, descriptions, or parameters are ever transmitted over the network.
- **AST Danger Detection:** Source code is analyzed using Python's abstract syntax tree before execution to intercept forbidden patterns (`eval`, `exec`, `os.system`, `subprocess` with `shell=True`, and recursive filesystem deletions).
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
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Architecture Decisions Log](docs/decisions.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

---

## License

MIT License. Copyright (c) 2026 Skill Factory Contributors.

All skills generated by Skill Factory are the **100% exclusive property of the user** under whichever license the user selects. Skill Factory does not require viral attribution in your generated skills.
