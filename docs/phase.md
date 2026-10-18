# Development Phases (Phase 0 – Phase 9)

Skill Factory is developed across 10 disciplined phases. Each phase has explicit goals, scope boundaries, entry criteria, and measurable exit criteria. No phase begins until the preceding phase meets its exit criteria.

---

## Overview

| Phase | Title | Focus Area | Status |
|---|---|---|---|
| **Phase 0** | GitHub Foundation | Repository layout, CI baseline, cleanup | **Completed** |
| **Phase 1** | Skill Factory Core | Core architecture, CLI, generator, spec, basic validation | **Ready for Entry** |
| **Phase 2** | Natural Language Skill Builder | Host-AI workflow + Offline guided interview | Planned |
| **Phase 3** | Multi-Agent Compatibility | 4-platform adapter, inspection, `doctor`, directory mapping | Planned |
| **Phase 4** | Easy Installation and Updates | Install, update, uninstall, rollback, local registry | Planned |
| **Phase 5** | Skill Testing and Validation | Subprocess test runner, AST safety scanner, eval scoring | Planned |
| **Phase 6** | Skill Library and Discovery | Local index, search, packaging (`zip`), GitHub publisher | Planned |
| **Phase 7** | Beginner-Friendly Experience | Numbered menu CLI, quickstart walkthroughs, error clarity | Planned |
| **Phase 8** | Security and Reliability | Hardening, secret scanner, OS matrix testing, edge cases | Planned |
| **Phase 9** | Public Release v1.0 | Documentation polish, governance files, v1.0.0 release | Planned |

---

## Phase 0 — GitHub Foundation

- **Status:** **Completed** (Commit `74635ac`, October 2026).
- **Goal:** Clean repository layout, correct file positions, eliminate tracked cache files, establish working GitHub Actions CI.
- **Deliverables:**
  - Root project layout (`README.md`, `SKILL.md`, `LICENSE`, `scripts/`, `tests/`).
  - `.gitignore` for Python, caches, IDE files, and generator output.
  - `.github/workflows/tests.yml` passing unit tests on Python 3.11 and 3.13.

---

## Phase 1 — Skill Factory Core

- **Goal:** Build the robust, modular Python package `skillfactory`, implement the canonical `SkillSpec` data model, safe YAML frontmatter rendering, atomic generation engine, and core validator.
- **Scope:**
  - Create package `skillfactory/` with `cli.py`, `core.py`, `spec.py`, `validator.py`, `templates/`.
  - Fix defect `DEF-01` (safe YAML escaping for frontmatter fields).
  - Fix defect `DEF-02` (cross-platform and Windows reserved name validation).
  - Backward compatibility: ensure `python3 scripts/create_skill.py` delegates seamlessly to the new core engine without changing arguments or behavior.
  - Implement atomic file generation with rollback on write failure.
  - Generate `.skillfactory/manifest.json` with SHA-256 hashes.
- **Entry Criteria:** Phase 0 complete and passing CI. User approval of master planning documentation.
- **Exit Criteria:**
  - `python3 -m skillfactory new` and `python3 scripts/create_skill.py` pass 100% of unit tests.
  - Generated skills strictly validate against Agent Skills format specification.
  - Zero third-party runtime dependencies.
  - All tests passing across Python 3.9, 3.11, and 3.13 on Linux, macOS, and Windows.

---

## Phase 2 — Natural Language Skill Builder

- **Goal:** Support creating skills from conversational plain-language problem statements, both with an AI assistant and completely offline.
- **Scope:**
  - **Host-AI Mode:** Refactor root `SKILL.md` to instruct host assistants (Claude Code, Cursor, Codex, Antigravity) to interview the user, construct a `skill-spec.json`, run `new --spec`, implement Python code and tests, and verify results.
  - **Offline Mode:** Implement interactive terminal interview (`skillfactory interview`) asking structured questions and deterministically choosing templates based on keyword heuristics.
  - Non-interactive batch answering (`--answers file.json`) for automated pipelines.
  - Template families: `instructions-only`, `python-script`, `checklist-review`, `file-transform`, `workflow-runbook`.
- **Entry Criteria:** Phase 1 exit criteria met.
- **Exit Criteria:**
  - Both Host-AI mode and Offline interview generate identical valid spec files.
  - Offline mode produces working scaffolding with honest "not implemented" test stubs.
  - Golden-file tests confirm deterministic generation output.

---

## Phase 3 — Multi-Agent Compatibility

- **Goal:** Ensure generated skills run smoothly across Claude Code, Cursor, OpenAI Codex, and Google Antigravity.
- **Scope:**
  - Data-driven platform database `skillfactory/data/platforms.json`.
  - Implement `skillfactory doctor` to detect installed AI platforms, verify read/write permissions, and report environment health.
  - Handle shared directories (`.agents/skills/` used by Cursor, Codex, and Antigravity) to prevent duplicate skill indexing.
  - Provide platform-specific frontmatter hints (`allowed-tools`, `disable-model-invocation`) only when explicitly requested, maintaining pure spec portability by default.
- **Entry Criteria:** Phase 2 exit criteria met.
- **Exit Criteria:**
  - `skillfactory doctor` correctly identifies platform presence on test machines.
  - Generated skills load in all 4 target platforms without syntax or discovery errors.

---

## Phase 4 — Easy Installation and Updates

- **Goal:** One-command installation, update, uninstallation, and rollback of skills without manual folder digging.
- **Scope:**
  - Commands: `skillfactory install`, `update`, `uninstall`, `rollback`, `list`.
  - Collision detection: protect unmanaged folders from accidental overwrites.
  - User-level registry `<user_data>/skillfactory/registry.json`.
  - Automatic backup snapshots before updates; one-command rollback to previous versions.
  - Clean uninstallation that deletes only manifest-tracked files.
  - Self-installation command (`skillfactory install-self`).
- **Entry Criteria:** Phase 3 exit criteria met.
- **Exit Criteria:**
  - Install, update, and uninstall successfully tested on all three operating systems (macOS, Linux, Windows).
  - Rollback verified: restoring a broken update restores previous working state cleanly.

---

## Phase 5 — Skill Testing and Validation

- **Goal:** Built-in automated test runner and multi-dimensional quality evaluation scoring.
- **Scope:**
  - `skillfactory test <skill-dir>`: isolated subprocess test execution with timeout and environment restrictions.
  - `skillfactory eval <skill-dir>`: objective quality scoring engine (0–100) assessing spec compliance, documentation, test coverage, and safety.
  - AST Static Safety Scanner: inspects Python scripts for suspicious code (`eval`, `exec`, shell injections, filesystem wiping).
  - Optional integration with `skills-ref validate` if installed locally.
- **Entry Criteria:** Phase 4 exit criteria met.
- **Exit Criteria:**
  - Test runner safely handles infinite loops and timeouts without hanging.
  - Evaluation engine produces consistent, reproducible scores on benchmark skills.

---

## Phase 6 — Skill Library and Discovery

- **Goal:** Browse, search, share, package, and publish skills.
- **Scope:**
  - Local skill catalog indexing and offline search (`skillfactory search`).
  - Portable export to `.zip` with integrity checksums (`skillfactory export`).
  - Safe import from `.zip` with Zip-Slip path traversal defense (`skillfactory import`).
  - Automated GitHub preparation (`skillfactory publish` generating README, license, CI, and git instructions).
  - Ship at least 5 curated, fully functional open-source example skills in `examples/`.
- **Entry Criteria:** Phase 5 exit criteria met.
- **Exit Criteria:**
  - Exported zip packages import cleanly on different machines.
  - Malicious zip archives (containing `../`) are rejected safely by the import validator.

---

## Phase 7 — Beginner-Friendly Experience

- **Goal:** Make Skill Factory effortlessly accessible to complete beginners.
- **Scope:**
  - Interactive top-level menu when running `python3 -m skillfactory` without arguments.
  - Friendly error messages with plain-language explanations and suggested next steps (no raw Python tracebacks).
  - Step-by-step Quickstart guides for macOS, Windows, and Linux.
  - Full adherence to accessibility standards (no color-only semantics, screen-reader friendly output, `NO_COLOR` support).
  - Plain-language glossary of Agent Skill concepts.
- **Entry Criteria:** Phase 6 exit criteria met.
- **Exit Criteria:**
  - Beginner usability validation: a new user completes creation and installation in ≤ 10 minutes without outside assistance.
  - 100% of CLI error messages pass the beginner-readability checklist.

---

## Phase 8 — Security and Reliability

- **Goal:** Comprehensive security audit, fuzzing, secret scanning, and cross-platform edge-case hardening.
- **Scope:**
  - Integrated secret and credential scanner (`SEC-02`).
  - Cross-platform path and Unicode edge-case testing (spaces in paths, non-ASCII characters, long Windows paths).
  - Fuzzing of YAML and JSON input parsers.
  - Security documentation (`SECURITY.md`) and vulnerability disclosure policy.
  - Supply-chain hardening: pin GitHub Actions with full commit hashes.
- **Entry Criteria:** Phase 7 exit criteria met.
- **Exit Criteria:**
  - Zero high or critical security findings.
  - Secret scanner catches 100% of synthetic test tokens and keys.
  - All edge cases documented in `docs/edgeCases.md` have passing automated test coverage.

---

## Phase 9 — Public Release v1.0

- **Goal:** Polish, final documentation sync, public release packaging, and community governance.
- **Scope:**
  - Complete documentation review and validation against running code.
  - Add community governance files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`.
  - Git tagging `v1.0.0` and automated GitHub Release workflow.
  - Verified demo walkthrough video or animated recording.
- **Entry Criteria:** Phase 8 exit criteria met.
- **Exit Criteria:**
  - GitHub Actions fully green across all OS and Python matrix combinations.
  - Clean v1.0.0 tag and GitHub Release with verified release assets.
  - All requirements in `docs/requirementsTraceability.md` verified complete.
