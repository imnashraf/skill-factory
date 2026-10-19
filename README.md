# Skill Factory

[![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen.svg)](.github/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.11%20%7C%203.13-blue.svg)](pyproject.toml)
[![Dependencies](https://img.shields.io/badge/dependencies-0%20(standard%20library)-success.svg)](skillfactory/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Specification](https://img.shields.io/badge/spec-agentskills.io-orange.svg)](https://agentskills.io/specification)

**Skill Factory** is an open-source, offline-first generator, validator, evaluator, and manager for **Agent Skills** conforming to the [Agent Skills specification](https://agentskills.io/specification).

It bridges the gap between conversational AI prompts and production-grade tools for AI coding assistants—including **Claude Code**, **Cursor**, **OpenAI Codex**, and **Google Antigravity**.

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

## Key Features

- ⚡ **Zero Third-Party Dependencies:** Pure Python standard-library implementation. Runs immediately on any machine with Python 3.9+ without `pip install` friction or virtual environments.
- 🔒 **Safe & Isolated:** AST safety scanner flags dangerous code (`eval`, `exec`, shell injection, filesystem wipes). Subprocess test runner enforces a 10-second timeout. Pre-publish checks block leaked API keys, tokens, and credentials.
- 🎯 **Dual-Mode Creation:**
  - **Host-AI Mode:** Uses the capabilities of your connected AI coding assistant (Claude, Cursor, Codex, Antigravity) via the root [`SKILL.md`](SKILL.md) to generate complete, tested code. No Skill Factory API subscription required.
  - **Offline Mode:** 5-minute interactive terminal questionnaire or batch JSON answers generating deterministic, verifiable templates with honest capability placeholders.
- 🌐 **Multi-Platform Compatibility:** Native data-driven discovery and installation for Claude Code, Cursor, Codex, and Google Antigravity with collision detection and shared-folder resolution (`.agents/skills/`).
- 📦 **Complete Lifecycle Management:** atomic staging, SHA-256 manifests, platform installer with automatic backup snapshots, rollback, uninstaller, ZIP export/import with Zip-Slip defense, and standalone GitHub repository publishing.
- 📊 **Automated Quality Scoring:** 0–100 rubric evaluating specification conformance, description trigger clarity, test coverage, implementation density, and documentation hygiene.

---

## Quickstart

### Prerequisites

Python 3.9 or higher (macOS default Command Line Tools, Linux, or Windows).

```bash
# Clone the repository
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# Run the interactive menu
python3 -m skillfactory
```

*(On Windows, use `py -m skillfactory` or `python -m skillfactory`)*

### Platform Quickstart Guides

Detailed, beginner-tested walkthroughs are available for your operating system:

- 🍏 [macOS Quickstart](docs/quickstart/macos.md)
- 🪟 [Windows Quickstart](docs/quickstart/windows.md)
- 🐧 [Linux Quickstart](docs/quickstart/linux.md)
- 📖 [Beginner Glossary](docs/glossary.md)

---

## Dual-Mode Operation

Skill Factory operates in two complementary modes depending on whether an AI coding assistant is available:

```text
                      ┌────────────────────────┐
                      │   Your Goal or Idea    │
                      └───────────┬────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
      [ Host-AI Mode ]                     [ Offline Mode ]
   Inside Claude Code, Cursor,           Terminal interview or
   Codex, or Antigravity                 `skillfactory new` CLI
                 │                                 │
                 ▼                                 ▼
   Host assistant reads SKILL.md         Interactive 5-step prompt
   and writes complete logic             or template selection
                 │                                 │
                 └────────────────┬────────────────┘
                                  ▼
                     [ Canonical SkillSpec ]
                                  │
                                  ▼
                   [ Skill Factory Core Generator ]
                     • Atomic sibling directory
                     • Validated YAML frontmatter
                     • SHA-256 integrity manifest
                     • Self-contained test suite
                                  │
                                  ▼
             `generated-skills/<name>/` Ready to Use!
```

### 1. Host-AI Mode (Connected Assistant)

When working in an AI coding assistant:

1. Copy or install Skill Factory into your assistant's skill folder.
2. Ask your assistant: *"Use the skill-factory skill to create a skill that parses CSV files and generates visual summary charts."*
3. The host assistant reads [`SKILL.md`](SKILL.md), plans the domain logic, uses Skill Factory to scaffold the canonical spec, and implements the functional Python scripts and tests.
4. **Zero API keys needed:** Skill Factory itself makes zero external AI calls; it leverages your existing assistant session.

### 2. Offline Mode (Terminal / Scripting)

When working in a standard terminal without AI access:

1. Run `python3 -m skillfactory interview` to answer 5 guided questions.
2. Select from 5 built-in template families:
   - `standard`: General command and utility workflows.
   - `api-wrapper`: REST API clients with auth handling and request templates.
   - `data-pipeline`: Batch extract-transform-load (ETL) and file processors.
   - `code-analysis`: Linters, AST inspectors, and repo audits.
   - `workflow-automation`: Multi-step DevOps, git, and ticket automation.
3. Skill Factory generates working tests, clear structural instructions, and honest `TODO` capability markers.

---

## Supported AI Platforms

Skill Factory maps to official agent discovery paths defined in [`skillfactory/data/platforms.json`](skillfactory/data/platforms.json):

| Platform | Project Scope Folder | Global (User) Scope Folder | Shared Compatibility |
| --- | --- | --- | --- |
| **Claude Code** | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | Native `allowed-tools`, `argument-hint` |
| **Cursor** | `.agents/skills/<name>/`, `.cursor/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` | Auto-detects Claude & Codex paths |
| **OpenAI Codex** | `.agents/skills/<name>/` | `~/.agents/skills/` | Supports `agents/openai.yaml` metadata |
| **Google Antigravity** | `.agents/skills/<name>/` | `~/.gemini/config/skills/` | Built-in workspace hierarchy resolution |

Run `python3 -m skillfactory doctor` to automatically detect which AI assistants are installed on your workstation.

---

## Generated Skill Anatomy

Every skill generated by Skill Factory complies with the [Agent Skills standard](https://agentskills.io/specification):

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

All commands are available via `python3 -m skillfactory <command>` or legacy `python3 scripts/create_skill.py`.

| Command | Description | Example |
| --- | --- | --- |
| `menu` | Opens the beginner-friendly interactive numbered menu. | `python3 -m skillfactory` |
| `new` | Directly generates a skill with command-line flags. | `python3 -m skillfactory new --name my-tool --desc "Process log files"` |
| `interview` | Launches the terminal questionnaire or accepts `--answers file.json`. | `python3 -m skillfactory interview` |
| `validate` | Validates YAML frontmatter, naming, structure, and integrity. | `python3 -m skillfactory validate generated-skills/my-tool` |
| `doctor` | Inspects local workstation and reports installed AI platforms. | `python3 -m skillfactory doctor` |
| `test` | Runs a skill's automated test suite in an isolated subprocess. | `python3 -m skillfactory test generated-skills/my-tool` |
| `eval` | Computes 0–100 quality score across 5 evaluation dimensions. | `python3 -m skillfactory eval generated-skills/my-tool` |
| `install` | Installs a skill into an AI platform with backup snapshotting. | `python3 -m skillfactory install generated-skills/my-tool --platform cursor` |
| `list` | Lists all installed skills across all detected platforms. | `python3 -m skillfactory list` |
| `update` | Updates an installed skill and checks manifest diffs. | `python3 -m skillfactory update my-tool --platform cursor` |
| `rollback` | Restores an installed skill to its previous backup snapshot. | `python3 -m skillfactory rollback my-tool --platform cursor` |
| `uninstall` | Safely removes an installed skill from a platform. | `python3 -m skillfactory uninstall my-tool --platform cursor` |
| `install-self` | Installs Skill Factory itself into a chosen AI coding assistant. | `python3 -m skillfactory install-self --platform claude-code` |
| `search` | Performs sub-millisecond offline keyword/tag search on library. | `python3 -m skillfactory search log` |
| `export` | Packages a skill into a portable `.zip` with SHA-256 sidecar. | `python3 -m skillfactory export generated-skills/my-tool` |
| `import` | Safely extracts a `.zip` skill package with Zip-Slip defense. | `python3 -m skillfactory import my-tool.zip` |
| `publish` | Generates a standalone repository with README, LICENSE, and CI. | `python3 -m skillfactory publish generated-skills/my-tool --out-dir dist/` |

---

## Curated Reference Examples

Skill Factory ships with 5 reference skills in the [`examples/`](examples/) directory, each scoring Grade A (≥ 90/100) on the quality rubric:

1. [`examples/git-release-helper/`](examples/git-release-helper/) — *Workflow Automation family*
2. [`examples/pdf-to-markdown/`](examples/pdf-to-markdown/) — *Data Pipeline family*
3. [`examples/docker-security-audit/`](examples/docker-security-audit/) — *Code Analysis family*
4. [`examples/api-schema-validator/`](examples/api-schema-validator/) — *API Wrapper family*
5. [`examples/sql-migration-linter/`](examples/sql-migration-linter/) — *Standard Utility family*

---

## Security & Reliability

Skill Factory takes security seriously:

- **Zero Network Ingestion:** The generator performs zero unexpected network calls.
- **AST Danger Scanner:** Scans Python source code using the abstract syntax tree for forbidden invocations (`eval`, `exec`, `os.system`, `subprocess` with `shell=True`, and recursive filesystem wipes).
- **Secret & Token Detection:** Scans text and code for AWS access keys, GitHub personal access tokens, OpenAI/Anthropic keys, and PEM private keys.
- **Atomic Staging:** Files are generated in sibling staging directories (`.tmp-<uuid>`) and atomically renamed upon successful manifest generation, preventing corrupt or half-written skills.
- **Zip-Slip Protection:** Archive import strictly validates target extraction paths against directory traversal attacks (`../`).
- **Subprocess Isolation:** Test execution runs in an isolated subprocess with a strict 10-second timeout, preventing freezing or memory leaks.

See [`SECURITY.md`](SECURITY.md) for vulnerability reporting procedures and threat model details.

---

## Development & Testing

Run the full automated test suite locally:

```bash
# Run all unit, integration, and security tests
python3 -m unittest discover -s tests -v
```

All 109+ tests run in ~2 seconds using standard library `unittest`.

To test backward compatibility with the legacy Phase 0 script:

```bash
python3 scripts/create_skill.py --name test-skill --description "Testing backward compatibility"
```

---

## Governance & Contributing

Skill Factory is an open-source project welcoming contributions. Please review:

- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Architecture Decisions Log](docs/decisions.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

---

## License

MIT License. Copyright (c) 2026 Skill Factory Contributors.

All skills generated by Skill Factory are the **100% exclusive property of the user** under whichever license the user selects. Skill Factory does not require attribution in your generated skills.
