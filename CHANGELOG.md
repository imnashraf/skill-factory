# Changelog

All notable changes to Skill Factory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-10-19

### Fixed

- **Platform Shorthand Aliases (DEF-04)**:
  - Enabled intuitive CLI shorthand aliases (`claude`, `anthropic`, `openai`, `google`, `agy`) for `--platform` across `install`, `update`, `rollback`, `uninstall`, and `install-self`.
- **Bytecode & Cache Manifest Filtering (DEF-05)**:
  - Filtered Python bytecode (`__pycache__`, `*.pyc`) and OS cache files (`.DS_Store`, `Thumbs.db`) from `create_manifest` and `verify_manifest` to prevent false positive integrity discrepancies when tests run before installation.

### Added

- **Phase 10 Automated Validation Suites**:
  - `tests/run_multiagent_validation.py`: Automated multi-agent lifecycle testing across Claude Code, Cursor, Codex, and Antigravity.
  - `tests/run_security_validation.py`: Comprehensive adversarial security and host isolation validation.
  - 4 new unit regression tests expanding the test suite to 114 tests with 100% pass rate.

---

## [1.0.0] - 2026-10-19

### Added

- **Core Generator Engine (Phase 1)**:
  - Atomic directory generation with sibling staging (`.tmp-*`) and rollback protection.
  - Safe YAML frontmatter serializer preventing parsing errors on colons, quotes, and hashes (resolves `DEF-01`).
  - Windows reserved name (`CON`, `PRN`, `AUX`, `NUL`) and platform reserved name protection (resolves `DEF-02`).
  - Cryptographic file manifest (`.skillfactory/manifest.json`) recording SHA-256 hashes for all generated files.
  - Legacy backward-compatible wrapper script `scripts/create_skill.py`.
- **Natural Language Skill Builder & Offline Interview (Phase 2)**:
  - Root `SKILL.md` orchestrating Host-AI assistant interactions across Claude Code, Cursor, Codex, and Antigravity.
  - Interactive terminal questionnaire CLI (`skillfactory interview`).
  - Batch answers automation mode (`--answers`).
  - Intelligent keyword heuristic router recommending the optimal template family.
  - 5 reusable starter template families: `python-script`, `file-transform`, `checklist-review`, `workflow-runbook`, `instructions-only`.
  - Deterministic golden byte-for-byte reproducibility tests.
- **Multi-Agent Compatibility & Platform Adapters (Phase 3)**:
  - Data-driven platform database `skillfactory/data/platforms.json` covering Claude Code, Cursor, OpenAI Codex, and Google Antigravity.
  - Environment detector identifying active AI coding tools and configurations.
  - System diagnostics tool `skillfactory doctor` verifying discovery paths.
  - Shared-folder collision resolver preventing duplicate entries in `.agents/skills/`.
- **Easy Installation & Automatic Backups (Phase 4)**:
  - Local installation registry tracking installed skills across project and user scopes.
  - Allow-list safe copy installer with optional symlink (`--link`) support.
  - Safe updating (`skillfactory update`) with automated backup snapshots preserved in `.skillfactory/backups/`.
  - Single-command rollback mechanism (`skillfactory rollback`) restoring previous working snapshots.
  - Non-destructive uninstall (`skillfactory uninstall`) preserving user-modified assets.
  - Self-installation command (`skillfactory install-self`) equipping host AI agents with Skill Factory.
- **Skill Testing & Quality Evaluation (Phase 5)**:
  - Isolated subprocess test runner (`skillfactory test`) with strict 10.0s execution timeout and environment sandboxing.
  - Python AST safety scanner detecting `eval()`, `exec()`, `__import__()`, `os.system()`, and destructive commands without execution.
  - Objective 0–100 quality scoring engine (`skillfactory eval`) assessing Structure, Portability, Documentation, Tests, and Safety.
  - Automated report persistence to `.skillfactory/test-results.json` and `.skillfactory/evaluation.json`.
- **Skill Library & Secure Packaging (Phase 6)**:
  - Local catalog indexer and sub-millisecond offline search (`skillfactory search`).
  - Reproducible ZIP export (`skillfactory export`) with SHA-256 checksum sidecars.
  - Secure ZIP import (`skillfactory import`) with strict defense against "Zip-Slip" path traversal exploits.
  - Standalone GitHub repository scaffolding generator (`skillfactory publish`).
  - 5 curated, Grade-A reference skills shipped in `examples/`: `pdf-to-markdown`, `docker-security-audit`, `git-release-helper`, `sql-migration-linter`, `api-schema-validator`.
- **Beginner Experience & Accessibility (Phase 7)**:
  - Interactive numbered top menu (`skillfactory menu` or invocation without args in interactive terminal).
  - 3-part beginner-friendly error messages (What happened, Why, Next steps) eliminating raw Python stack traces.
  - Complete, tested OS Quickstart guides for macOS, Windows, and Linux in `docs/quickstart/`.
  - Strict compliance with `NO_COLOR` standard and complete removal of color-only semantic signals.
  - Comprehensive Beginner's Glossary covering 17 core concepts in `docs/glossary.md`.
- **Security & Reliability Hardening (Phase 8)**:
  - Credential and secret scanner detecting AWS keys, GitHub PATs, OpenAI keys, and private certificates before publish.
  - Cross-platform path resilience across spaces, non-ASCII characters, and deep directories.
  - Robust parser fuzzing suite handling truncated YAML, null bytes, and malformed JSON cleanly.
  - GitHub Actions supply-chain pinning to full 40-character commit hashes.
  - Formal `SECURITY.md` vulnerability reporting policy and SLA.
  - Multi-OS CI testing matrix across Ubuntu, macOS, and Windows on Python 3.9, 3.11, and 3.13.

### Fixed

- `DEF-01`: Safe YAML frontmatter serializer prevents crashes from colons, hashes, and quotes in descriptions.
- `DEF-02`: Generator and validator strictly reject Windows reserved device names and platform reserved directory names.
- `DEF-03`: Minimum supported Python version validated as 3.9+ across macOS, Windows, and Linux.
