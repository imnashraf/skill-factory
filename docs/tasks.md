# Master Task Catalog

Every phase is broken down into discrete, actionable tasks. Tasks follow the format `T<phase>.<number>` and reference dependencies, deliverables, and acceptance criteria.

---

## Phase 1 — Skill Factory Core

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref | Status |
|---|---|---|---|---|---|---|
| **T1.01** | Package Structure | Create `skillfactory/` package directory layout (`__init__.py`, `__main__.py`, `cli.py`, `core.py`, `spec.py`, `validator.py`, `templates/`). | None | `skillfactory/` layout | AC1.01 | **Completed** |
| **T1.02** | SkillSpec Model | Implement canonical `SkillSpec` data class and JSON schema validator (`skillfactory/spec.py`). | T1.01 | `skillfactory/spec.py` | AC1.02 | **Completed** |
| **T1.03** | Safe YAML Formatter | Implement lightweight, safe YAML frontmatter serializer handling multiline strings, colons, quotes, and escaping (fixes `DEF-01`). | T1.01 | `skillfactory/yaml_util.py` | AC1.03 | **Completed** |
| **T1.04** | Core Generator Engine | Implement atomic skill generator (`skillfactory/core.py`) with sibling staging (`.tmp-*`), rollback on error, and UTF-8 LF writing. | T1.02, T1.03 | `skillfactory/core.py` | AC1.04 | **Completed** |
| **T1.05** | Template System | Implement `string.Template` loader and initial template families: `instructions-only` and `python-script`. | T1.01 | `skillfactory/templates/` | AC1.05 | **Completed** |
| **T1.06** | Manifest & Hashes | Implement `.skillfactory/manifest.json` generation with file SHA-256 hashes, semver versioning, and generator metadata. | T1.04 | `skillfactory/manifest.py` | AC1.06 | **Completed** |
| **T1.07** | Specification Validator | Implement `skillfactory/validator.py` enforcing Agent Skills format rules, reserved names (`con`, `synced`), and relative path checks. | T1.01 | `skillfactory/validator.py` | AC1.07 | **Completed** |
| **T1.08** | CLI Dispatcher | Implement `skillfactory/cli.py` with commands `new`, `validate`, `--dry-run`, `--json`, and clear error reporting. | T1.04, T1.07 | `skillfactory/cli.py` | AC1.08 | **Completed** |
| **T1.09** | Legacy Script Wrapper | Update `scripts/create_skill.py` to delegate to `skillfactory.core` while keeping identical CLI arguments and exit codes. | T1.08 | `scripts/create_skill.py` | AC1.09 | **Completed** |
| **T1.10** | Phase 1 Tests & CI | Write comprehensive unit tests for core, generator, YAML escaping, and validation; expand CI matrix to Python 3.9, 3.11, 3.13. | T1.01–T1.09 | `tests/`, `.github/workflows/tests.yml` | AC1.10 | **Completed** |

---

## Phase 2 — Natural Language Skill Builder

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref | Status |
|---|---|---|---|---|---|---|
| **T2.01** | Host-AI Skill Prompt | Update root `SKILL.md` to instruct host assistants on the end-to-end interview, spec creation, scaffolding, and verification loop. | T1.08 | `SKILL.md` | AC2.01 | **Completed** |
| **T2.02** | Offline Interview Engine | Implement terminal questionnaire (`skillfactory/interview.py`) for plain-language guided creation without an AI model. | T1.02 | `skillfactory/interview.py` | AC2.02 | **Completed** |
| **T2.03** | Batch Answers Mode | Support `--answers answers.json` for non-interactive and scripted execution of the interview process. | T2.02 | `skillfactory/interview.py` | AC2.03 | **Completed** |
| **T2.04** | Template Selection Rules | Implement deterministic keyword heuristic mapper to suggest the best template family based on user answers. | T2.02 | `skillfactory/templates/router.py` | AC2.04 | **Completed** |
| **T2.05** | Additional Templates | Implement remaining template families: `checklist-review`, `file-transform`, `workflow-runbook`. | T1.05 | `skillfactory/templates/*` | AC2.05 | **Completed** |
| **T2.06** | Honest Stubs & Tests | Ensure generated skills include working structural tests and clearly documented, skipped functional stubs. | T2.05 | Template assets | AC2.06 | **Completed** |
| **T2.07** | Deterministic Golden Tests | Add automated tests comparing generated skills against golden sample directories byte-for-byte. | T2.05 | `tests/test_golden.py` | AC2.07 | **Completed** |

---

## Phase 3 — Multi-Agent Compatibility

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref |
|---|---|---|---|---|---|
| **T3.01** | Platform Database | Create `skillfactory/data/platforms.json` encoding folder conventions, supported fields, and verification dates. | None | `skillfactory/data/platforms.json` | AC3.01 |
| **T3.02** | Platform Detection | Implement environment scanner to detect installed AI platforms and check filesystem permissions. | T3.01 | `skillfactory/compat/detect.py` | AC3.02 |
| **T3.03** | Doctor Command | Implement `skillfactory doctor` displaying system health, detected agents, and platform discovery paths. | T3.02 | `skillfactory/cli.py` | AC3.03 |
| **T3.04** | Shared-Folder Resolver | Implement duplicate-name and collision detection across shared locations like `.agents/skills/`. | T3.01 | `skillfactory/compat/resolve.py` | AC3.04 |
| **T3.05** | Compatibility Section | Auto-generate the "Compatibility" markdown table in generated `README.md` and `compatibility` frontmatter. | T3.01 | `skillfactory/core.py` | AC3.05 |
| **T3.06** | Compatibility Matrix Verification | Create tests validating generated skills load cleanly in simulated Claude, Cursor, Codex, and Antigravity directory layouts. | T3.01 | `tests/test_compat.py` | AC3.06 |

---

## Phase 4 — Easy Installation and Updates

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref |
|---|---|---|---|---|---|
| **T4.01** | Local Registry Manager | Implement `skillfactory/registry.py` managing `<user_data>/skillfactory/registry.json`. | None | `skillfactory/registry.py` | AC4.01 |
| **T4.02** | Install Command | Implement `skillfactory install` with allow-list copying, collision protection, and confirmation prompts. | T3.01, T4.01 | `skillfactory/installer.py` | AC4.02 |
| **T4.03** | Update & Hash Diff | Implement `skillfactory update` checking file SHA-256 hashes for local edits and backing up previous versions. | T4.02 | `skillfactory/installer.py` | AC4.03 |
| **T4.04** | Rollback Command | Implement `skillfactory rollback` to cleanly restore the previous backup snapshot from the registry. | T4.03 | `skillfactory/installer.py` | AC4.04 |
| **T4.05** | Uninstall Command | Implement `skillfactory uninstall` deleting only files recorded in the manifest and cleaning registry entries. | T4.02 | `skillfactory/installer.py` | AC4.05 |
| **T4.06** | Symlink Support | Add optional `--link` mode for platforms and OSes that support symlinks, with fallback to copy. | T4.02 | `skillfactory/installer.py` | AC4.06 |
| **T4.07** | List Command | Implement `skillfactory list` showing installed skills across all platforms, versions, and modification flags. | T4.01 | `skillfactory/cli.py` | AC4.07 |
| **T4.08** | Self-Install Command | Implement `skillfactory install-self` allowing Skill Factory to install itself into any target platform. | T4.02 | `skillfactory/cli.py` | AC4.08 |
| **T4.09** | Installation Test Suite | Comprehensive tests for install, collision detection, update, rollback, and uninstall across temporary directories. | T4.01–T4.08 | `tests/test_installer.py` | AC4.09 |

---

## Phase 5 — Skill Testing and Validation

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref |
|---|---|---|---|---|---|
| **T5.01** | Subprocess Test Runner | Implement `skillfactory test` executing skill tests in an isolated subprocess with timeout and restricted environment. | T1.04 | `skillfactory/tester.py` | AC5.01 |
| **T5.02** | AST Safety Scanner | Implement `skillfactory/scanner.py` using Python `ast` to detect dangerous function calls, network requests, and disk operations. | None | `skillfactory/scanner.py` | AC5.02 |
| **T5.03** | Quality Scoring Engine | Implement `skillfactory eval` calculating 0–100 quality scores across structure, spec compliance, tests, docs, and safety. | T5.01, T5.02 | `skillfactory/eval.py` | AC5.03 |
| **T5.04** | Extended Validation Rules | Add warnings for body token length (>5000 tokens), markdown link resolution, and single-level reference nesting. | T1.07 | `skillfactory/validator.py` | AC5.04 |
| **T5.05** | Test Result Persistence | Save structured test and evaluation reports to `.skillfactory/test-results.json` and `evaluation.json`. | T5.01, T5.03 | `skillfactory/tester.py` | AC5.05 |
| **T5.06** | Host-AI Trigger Rubric | Provide guidelines and prompt tests for evaluating whether a host AI accurately triggers on relevant user requests. | T2.01 | `docs/eval.md` | AC5.06 |
| **T5.07** | Testing & Eval Tests | Write unit tests for runner timeouts, AST scanner detections, and eval score calculations. | T5.01–T5.05 | `tests/test_eval.py` | AC5.07 |

---

## Phase 6 — Skill Library and Discovery

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref |
|---|---|---|---|---|---|
| **T6.01** | Local Catalog Indexer | Implement indexer scanning a local folder of skills to build an offline searchable `index.json`. | T1.06 | `skillfactory/library.py` | AC6.01 |
| **T6.02** | Search Command | Implement `skillfactory search` searching skills by keyword, tag, or description offline. | T6.01 | `skillfactory/cli.py` | AC6.02 |
| **T6.03** | Zip Export Engine | Implement `skillfactory export` packaging skills into portable `.zip` archives with SHA-256 checksums. | T1.06 | `skillfactory/packaging.py` | AC6.03 |
| **T6.04** | Safe Zip Importer | Implement `skillfactory import` with Zip-Slip path traversal defense, checksum validation, and safety scanning. | T6.03, T5.02 | `skillfactory/packaging.py` | AC6.04 |
| **T6.05** | GitHub Publish Prep | Implement `skillfactory publish` generating a standalone repository scaffold with README, LICENSE, and CI for sharing. | T1.04 | `skillfactory/publish.py` | AC6.05 |
| **T6.06** | Curated Examples | Build and ship ≥ 5 high-quality, fully functional reference skills in `examples/` covering each template family. | T2.05 | `examples/*` | AC6.06 |
| **T6.07** | Library Test Suite | Comprehensive tests for indexing, zip export, Zip-Slip rejection, and publishing scaffold generation. | T6.01–T6.06 | `tests/test_library.py` | AC6.07 |

---

## Phase 7 — Beginner-Friendly Experience

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref |
|---|---|---|---|---|---|
| **T7.01** | Interactive Top Menu | Implement clean numbered terminal menu when running `python3 -m skillfactory` without arguments. | T1.08 | `skillfactory/cli.py` | AC7.01 |
| **T7.02** | Error Message Redesign | Audit and rewrite all CLI error messages to explain what happened, why, and suggested remediation steps. | T1.08 | `skillfactory/errors.py` | AC7.02 |
| **T7.03** | OS Quickstart Guides | Author detailed, step-by-step Quickstart guides for macOS, Windows, and Linux in `docs/quickstart/`. | None | `docs/quickstart/*.md` | AC7.03 |
| **T7.04** | Accessibility Audit | Enforce `NO_COLOR` environment variable support, eliminate color-only indicators, ensure 80-column terminal readability. | T1.08 | `skillfactory/ui_util.py` | AC7.04 |
| **T7.05** | Beginner Glossary | Create comprehensive glossary explaining Agent Skills, frontmatter, progressive disclosure, and platform concepts. | None | `docs/glossary.md` | AC7.05 |
| **T7.06** | Beginner Usability Test | Conduct structured usability trial with sample tasks to verify first-time user success within 10 minutes. | T7.01–T7.05 | Test logs | AC7.06 |

---

## Phase 8 — Security and Reliability

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref |
|---|---|---|---|---|---|
| **T8.01** | Secret & Token Scanner | Implement pattern scanner checking for hardcoded AWS keys, GitHub tokens, OpenAI keys, and private certificates. | None | `skillfactory/scanner.py` | AC8.01 |
| **T8.02** | Cross-Platform Path Hardening | Add automated test suite for spaces in paths, non-ASCII characters, and Windows long paths. | T1.04 | `tests/test_paths.py` | AC8.02 |
| **T8.03** | Input Fuzzing | Implement unit fuzz tests feeding malformed strings, deeply nested JSON, and invalid UTF-8 into parsers. | T1.02, T1.03 | `tests/test_fuzz.py` | AC8.03 |
| **T8.04** | Supply Chain Pinning | Pin all GitHub Actions in `.github/workflows/` to full 40-character commit hashes with minimal `permissions`. | Phase 0 CI | `.github/workflows/` | AC8.04 |
| **T8.05** | Security Policy | Create `SECURITY.md` defining vulnerability reporting procedure and security response turnaround. | None | `SECURITY.md` | AC8.05 |
| **T8.06** | CI Multi-OS Matrix | Configure GitHub Actions matrix to run all tests on `ubuntu-latest`, `macos-latest`, and `windows-latest`. | T8.04 | `.github/workflows/tests.yml` | AC8.06 |

---

## Phase 9 — Public Release v1.0

| Task ID | Task Title | Description | Prereqs | Deliverables | AC Ref |
|---|---|---|---|---|---|
| **T9.01** | Governance Files | Author `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `CHANGELOG.md`. | None | Root docs | AC9.01 |
| **T9.02** | Documentation Sync | Review every document in `docs/` against current code; ensure 100% accurate command examples and requirement IDs. | All phases | `docs/*` | AC9.02 |
| **T9.03** | Platform Matrix Audit | Re-verify compatibility matrix paths and frontmatter support against the latest documentation of all 4 AI tools. | T3.01 | `docs/compatibilityMatrix.md` | AC9.03 |
| **T9.04** | Release Packaging | Configure GitHub Actions release workflow triggering on `v*` tags to verify tests and generate release notes. | T8.06 | `.github/workflows/release.yml` | AC9.04 |
| **T9.05** | Demo Assets | Create clear, high-resolution demo assets (animated GIFs / terminal recordings) for the root `README.md`. | T7.01 | `assets/demo.gif` | AC9.05 |
| **T9.06** | Final Release Tag | Tag `v1.0.0`, push to GitHub, and publish public release notes. | T9.01–T9.05 | Git Tag `v1.0.0` | AC9.06 |
