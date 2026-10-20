# Changelog

All notable changes to Skill Factory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.2] - 2026-10-20

### Added

- **CLI Simulation Support (`--dry-run`)**: Added `--dry-run` simulation to `skillfactory install` and `skillfactory uninstall`, accurately predicting file operations without creating directories or writing/removing files on disk.
- **Dry-Run Regression Test Suite**: Added dedicated test coverage in `tests/test_installer.py`.

### Fixed

- **Static Type Checking & Diagnostics**: Remediated Pyrefly and type analysis warnings in `skillfactory/yaml_util.py` and `tests/test_compat.py`.

---

## [1.2.1] - 2026-10-20

### Changed

- **PyPI Distribution Package Renamed**: Updated distribution package name in `pyproject.toml` to `agent-skill-factory` to avoid PyPI namespace similarity collisions with legacy packages.
- **Python Import & CLI Preserved**: The Python runtime import package remains `skillfactory` and both existing CLI commands (`skillfactory` and `skill-factory`) remain unchanged.
- **PyPI OIDC Publishing**: Updated workflow `.github/workflows/pypi-publish.yml` environment target URL to `https://pypi.org/p/agent-skill-factory`.
- **Documentation Updates**: Updated `README.md` and quickstart guides with `pip install agent-skill-factory`.

---

## [1.2.0] - 2026-10-20

### Added

- **PyPI Distribution Readiness (Workstream A)**:
  - Packaging configuration verified in `pyproject.toml` with dual console scripts: `skillfactory` and `skill-factory`.
  - Comprehensive bundled package data rules ensuring `data/*/*.json` and subdirectories are fully included in wheels.
  - PyPI namespace collision audit documented; publication pathway configured via GitHub Actions OIDC Trusted Publishing (`.github/workflows/pypi-publish.yml`).
  - Isolated clean-environment installation testing verified outside source tree.
- **Beginner Onboarding & Guided UX (Workstream B)**:
  - Interactive step-by-step onboarding wizard (`skillfactory guide`) covering diagnostic pre-flight, assistant selection, specification, generation, and optional installation.
  - Enhanced top-level interactive menu with choices 0–12 and zero required flags.
- **Curated Domain Skill Packs (Workstream D)**:
  - 3-tier domain taxonomy schema (Personal, Professional, Developer) covering 31 domain specializations.
  - 5 curated domain packs (`office-productivity`, `finance-erp`, `hr-workforce`, `project-management`, `developer-security`) defined in `skillfactory/data/packs.json`.
  - Full pack lifecycle CLI manager (`skillfactory pack list`, `install`, `verify`, `uninstall`) with atomic rollback on partial batch failures.
  - 9 new production-grade reference skills (total 14 skills in library), all achieving Grade A (≥90/100) on the quality rubric.
- **Optional AI-Assisted Skill Creation (Workstream E)**:
  - Provider-neutral AI creation engine (`skillfactory ai-create`) supporting local Ollama, OpenAI-compatible APIs, and offline deterministic mock providers.
  - Pre-execution AST safety quarantine scanning for dangerous calls before running tests.
  - Isolated subprocess execution sandbox (10.0s timeout) with bounded self-repair loop (up to 3 retries).
- **Multi-Agent Platform Expansion (Workstream F)**:
  - Expanded compatibility to 8 AI coding assistants: Claude Code, Google Antigravity, Cursor, OpenAI Codex, Windsurf, Continue, Cline, and GitHub Copilot.
  - Added native detection rules, directory schemas, and shorthand alias normalization (`windsurf`, `codeium`, `continue`, `cline`, `copilot`, `github-copilot`).
- **Security & Quality Hardening (Workstream G)**:
  - Symlink escape defense in file installer and package importer preventing access to files outside skill directory.
  - 3 new prompt injection rules (`INJ005` system prompt extraction, `INJ006` webhook exfiltration, `INJ007` adversarial roleplay).
  - Multiagent validation suite expanded to test all 8 platforms through 6-stage lifecycle (`install`, `validate`, `execute`, `update`, `rollback`, `uninstall`).
- **Natural-Language Requirements & Behavioral Testing (Phase 16)**:
  - Natural-language requirement parser (`skillfactory/ai/requirements.py`) extracting intent, constraints, inputs/outputs, and generating an automated assumption register.
  - Automated behavioral unit test generation (`skillfactory/ai/test_gen.py`) establishing traceability matrices mapped directly to user acceptance criteria.
  - Deterministic non-AI fallback synthesis engine and bounded self-repair loop with automated code modification diffing.
- **Skill Library, Multi-Attribute Discovery & Community Quarantine (Phase 17)**:
  - 3-tier domain taxonomy and multi-attribute catalog search filtering by tags, author, platform, and minimum quality score.
  - Pack installation preview CLI with target filesystem inspection and destination collision detection.
  - Community submission quarantine gate with pre-execution AST screening and manifest integrity verification.
- **Production Hardening & 16-Vector Threat Model (Phase 18)**:
  - Comprehensive 16-vector security audit (`docs/final-development/securityFindings.md`) covering Zip-Slip, symlink escapes, AST dangerous calls, secrets, prompt injection, and host isolation.
  - Multiagent validation suite expanded to 8 platforms across all 6 lifecycle stages (`install`, `validate`, `execute`, `update`, `rollback`, `uninstall`).
  - Production benchmark harness confirming sub-10ms CLI launch and high-throughput AST scanning.
- **Markdown Quality & CI Regression Suite**:
  - Full remediation of 179 Markdown formatting violations across all 152 repository documentation files and skills.
  - Template engine updates ensuring zero blank-line or heading violations (MD022, MD031, MD032, MD040, MD058, MD060).
  - Automated CI regression test suite (`tests/test_markdown_lint.py`) integrated into GitHub Actions across Ubuntu, macOS, and Windows.
- **Community & Launch Kit (Workstreams C & H)**:
  - Community launch preparation kit with platform-tailored announcements for Hacker News, Reddit, and LinkedIn.
  - GitHub issue forms (`bug_report.yml`, `feature_request.yml`) and pull request template (`pull_request_template.md`).
  - Zero-telemetry adoption measurement policy.

---

## [1.1.0] - 2026-10-19

### Added

- **Public Launch & Developer Adoption (Phase 11)**:
  - Comprehensive, honest `README.md` with explicit product boundaries and verified platform support tiers.
  - Beginner-friendly platform-specific onboarding guide (`docs/beginnerQuickstart.md`) for macOS, Windows, and Linux.
  - 5 reproducible, real-world reference skill demonstrations with automated validation harness (`scripts/run_demos.py` and `docs/demonstrations.md`).
  - Community launch preparation kit (`docs/launchPreparation.md`) including Show HN/Reddit drafts, FAQ, and AI coding assistant comparisons.
- **Beginner-Friendly Experience (Phase 12)**:
  - Pre-flight diagnostic engine (`skillfactory doctor --guided`) checking Python runtime, permissions, shell PATH, and assistant installations with concrete remediation commands.
  - Intuitive positional skill name CLI syntax (`skillfactory new my-skill`) with automatic trigger guidance.
  - Interactive questionnaire (`skillfactory interview`) enhancements with live kebab-case sanitization loops and target assistant prompts.
  - Universal 3-part structured error formatting (`What happened`, `Why it happened`, `What to do next`) across all CLI errors with stack trace suppression.
  - Automated usability regression test suite (`tests/test_beginner_experience.py`).
- **Skill Library & Community Ecosystem (Phase 13)**:
  - Built-in offline reference catalog (`skillfactory/data/catalog.json`) containing 5 Grade-A reference skills with instant (<10ms) local search.
  - Static prompt injection and adversarial instruction scanner rules (`INJ001`–`INJ004` in `skillfactory/scanner.py`) detecting directive overrides, persona shifts, remote execution pipelines, and hidden markup.
  - Objective 100-point community quality scoring rubric (`docs/skillQualityStandards.md`) defining evaluation criteria for Grade A/B/C/F classifications.
  - Standardized community contribution workflow (`docs/communityContributions.md`) and GitHub submission issue form (`.github/ISSUE_TEMPLATE/skill_submission.yml`).
  - Untrusted archive import quarantine warning banners in `skillfactory import`.
- **Production Hardening & Ecosystem Expansion (Phase 14)**:
  - Cross-platform regression test suite (`tests/test_hardening.py`) verifying deep Unicode paths, spaces, Windows reserved device names (`CON`, `PRN`, `NUL`), Zip Slip traversal defenses, and atomic rollbacks.
  - Repeatable performance benchmark harness (`scripts/run_benchmarks.py`) profiling cold starts, scaffolding throughput, AST scanning rate, and manifest verification.
  - Comprehensive 14-vector security threat model audit (`docs/securityThreatModel.md`).
  - Rigorous 4-tier platform compatibility matrix (`docs/compatibilityMatrix.md`) distinguishing verified autonomous activation, manual invocation, directory discovery, and simulated testing.
  - Ecosystem expansion assessment (`docs/ecosystemExpansion.md`) evaluating Windsurf, Continue.dev, Cline, and Copilot.

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
