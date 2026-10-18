# Measurable Acceptance Criteria (Phases 0 – 9)

Every phase has explicit, testable acceptance criteria (`AC<phase>.<number>`). A phase is only considered complete when 100% of its acceptance criteria are proven passing.

---

## Phase 0 — GitHub Foundation (Completed)

| ID | Criterion | Verification Method | Status |
|---|---|---|---|
| **AC0.01** | All project files (`README.md`, `SKILL.md`, `LICENSE`, `scripts/`, `tests/`) live at root. | `git ls-files` shows no files inside nested `skill-factory/` folder. | **Passed** |
| **AC0.02** | Python cache files (`__pycache__`, `*.pyc`) are untracked and excluded by `.gitignore`. | `git status` shows clean tree after running tests. | **Passed** |
| **AC0.03** | Automated GitHub Actions CI executes unit tests on Python 3.11 & 3.13 on push/PR. | GitHub Actions workflow completes with green checkmark. | **Passed** |

---

## Phase 1 — Skill Factory Core

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC1.01** | Package `skillfactory` runs via `python3 -m skillfactory`. | Command execution in terminal. | Exit code 0, displays help or menu. | **Passed** |
| **AC1.02** | `SkillSpec` data model validates names, descriptions, and template types. | Unit tests in `tests/test_spec.py`. | 100% pass on valid and invalid specs. | **Passed** |
| **AC1.03** | YAML serializer produces valid frontmatter for any string with colons, quotes, or `#`. | Roundtrip parse test via standard YAML parser. | Zero YAML syntax errors (fixes `DEF-01`). | **Passed** |
| **AC1.04** | Atomic generation leaves no partial files if a write fails. | Fault-injection unit test. | 0 orphan files in target directory on failure. | **Passed** |
| **AC1.05** | Template rendering produces `SKILL.md`, `README.md`, `scripts/`, `tests/`, `references/`. | File existence assertions. | All 5 artifacts present in output. | **Passed** |
| **AC1.06** | `.skillfactory/manifest.json` generated with accurate SHA-256 hashes of all files. | Checksum verification test. | 100% hash match against written files. | **Passed** |
| **AC1.07** | Validator catches Windows reserved names (`con`, `prn`), invalid kebab-case, missing frontmatter. | Negative unit tests in `test_validator.py`. | 100% caught with exit code 1 (fixes `DEF-02`). | **Passed** |
| **AC1.08** | Legacy script `python3 scripts/create_skill.py` functions identically. | Backward compatibility test suite. | Existing tests in `test_generator.py` pass without change. | **Passed** |
| **AC1.09** | Zero third-party runtime dependencies. | `tests/test_no_third_party_imports.py`. | 0 non-stdlib imports in `skillfactory/`. | **Passed** |
| **AC1.10** | Phase 1 test suite runs in under 10 seconds. | Terminal timer during test run. | Execution time < 10.0s (0.19s). | **Passed** |

---

## Phase 2 — Natural Language Skill Builder

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC2.01** | Root `SKILL.md` guides host AI through interactive interview and verification loop. | Manual agent interaction in Antigravity/Claude. | Complete skill generated from conversational prompt. | **Passed** |
| **AC2.02** | `skillfactory interview` runs in terminal without network or AI model. | Offline terminal execution. | Produces valid `skill-spec.json` and scaffold. | **Passed** |
| **AC2.03** | Batch interview `--answers answers.json` runs non-interactively. | Scripted CLI test. | Exit code 0, creates expected skill without prompting. | **Passed** |
| **AC2.04** | Keyword router picks appropriate template family from problem description. | Router unit tests with 20 sample prompts. | ≥ 90% appropriate template assignment (100% achieved). | **Passed** |
| **AC2.05** | 5 template families implemented (`instructions-only`, `python-script`, `checklist-review`, `file-transform`, `workflow-runbook`). | Template rendering tests. | All 5 templates render valid skills. | **Passed** |
| **AC2.06** | Generated script-based skills include structural tests and skipped functional stubs. | `python3 -m unittest discover` on output. | Structural tests pass; stubs report skipped (not failed). | **Passed** |
| **AC2.07** | Deterministic generation produces byte-identical files on identical input. | Golden-file hash comparison test. | 100% byte match (excluding manifest timestamps). | **Passed** |

---

## Phase 3 — Multi-Agent Compatibility

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC3.01** | Platform database `platforms.json` encodes paths and features for all 4 tools. | Schema validation test on JSON file. | 100% valid schema with documented dates. | **Passed** |
| **AC3.02** | Platform detection identifies installed agents on host system. | `test_detect.py` with mock filesystem. | Accurate detection of Claude, Cursor, Codex, Antigravity. | **Passed** |
| **AC3.03** | `skillfactory doctor` prints clear diagnostic summary and path readiness. | Command execution in terminal. | Exit code 0, readable diagnostic report. | **Passed** |
| **AC3.04** | Shared directory resolver avoids double-installing to `.agents/skills/`. | Multi-platform install test. | 0 duplicate folder collisions created. | **Passed** |
| **AC3.05** | Compatibility table auto-generated in `README.md` and frontmatter. | Output inspection test. | Accurate platform list in generated markdown. | **Passed** |
| **AC3.06** | Generated skills load cleanly without errors in simulated platform folders. | Discovery simulation tests. | 0 syntax or parsing errors. | **Passed** |

---

## Phase 4 — Easy Installation and Updates

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC4.01** | Registry tracks installed skills, platforms, scopes, versions, and backup paths. | JSON validation of `registry.json`. | Correct record created on install. | **Passed** |
| **AC4.02** | `install` copies only allow-listed files and refuses to overwrite unmanaged folders. | Negative collision unit test. | Aborts cleanly on unmanaged folder collision. | **Passed** |
| **AC4.03** | `update` detects local edits via SHA-256 diff and takes automated backup. | Edit-detection test. | Backup snapshot created in `<backup_dir>/`. | **Passed** |
| **AC4.04** | `rollback` restores previous working version in single command. | Rollback integration test. | Target folder restored byte-for-byte to backup. | **Passed** |
| **AC4.05** | `uninstall` removes only manifest-tracked files, preserving user data. | Partial uninstall test with user file. | User file preserved; skill files removed cleanly. | **Passed** |
| **AC4.06** | Symlink mode `--link` creates valid symlink or falls back to copy on failure. | Symlink creation test on supported OS. | Valid link or clean copy fallback. | **Passed** |
| **AC4.07** | `list` displays all installed skills, platforms, and modification flags. | Command output test. | Tabular list matches registry contents. | **Passed** |
| **AC4.08** | `install-self` installs Skill Factory into host agent skills folder. | Self-install test. | Root `SKILL.md` and scripts discoverable by agent. | **Passed** |
| **AC4.09** | Full install lifecycle passes on macOS, Linux, and Windows. | Cross-platform CI runner matrix. | 100% tests pass on all 3 operating systems. | **Passed** |

---

## Phase 5 — Skill Testing and Validation

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC5.01** | `test` executes skill tests in isolated subprocess with 10s timeout. | Subprocess runner unit test. | Times out and reports clean error; does not hang. | **Passed** |
| **AC5.02** | AST Safety Scanner flags `eval`, `exec`, `shell=True`, and filesystem wipes. | Synthetic malicious code scan tests. | 100% of dangerous AST patterns caught. | **Passed** |
| **AC5.03** | `eval` calculates 0–100 score across all 5 quality dimensions. | Eval engine test on benchmark skills. | Accurate point calculation matching rubric. | **Passed** |
| **AC5.04** | Validator flags `SKILL.md` exceeding 500 lines or broken relative links. | Linter unit test. | Warnings issued for long files and missing links. | **Passed** |
| **AC5.05** | Reports saved to `.skillfactory/test-results.json` and `evaluation.json`. | File existence and JSON schema check. | Valid JSON files written. | **Passed** |
| **AC5.06** | Trigger rubric guidelines documented and verified against sample prompts. | Review of `docs/eval.md`. | Complete rubric with positive/negative trigger cases. | **Passed** |
| **AC5.07** | Testing and eval suite executes in < 15 seconds. | Terminal timer. | Total execution time < 15.0s (measured: 1.63s). | **Passed** |

---

## Phase 6 — Skill Library and Discovery

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC6.01** | Local catalog indexer builds searchable `index.json` from a skills folder. | Indexing unit test. | Valid index with names, tags, and versions. | **Passed** |
| **AC6.02** | `search` finds skills by keyword or tag offline in < 100ms. | Search execution test. | Relevant skills returned in < 0.1s (measured: < 1ms). | **Passed** |
| **AC6.03** | `export` creates valid `.zip` package with manifest and SHA-256 checksum. | Zip export verification test. | Archive extracts and verifies checksum cleanly. | **Passed** |
| **AC6.04** | `import` rejects malicious archives containing Zip-Slip paths (`../`). | Security test with synthetic malicious zip. | 100% of path traversal attempts blocked. | **Passed** |
| **AC6.05** | `publish` generates standalone Git repository structure with README, license, CI. | Publish generator test. | Standalone skill repo ready for `git push`. | **Passed** |
| **AC6.06** | ≥ 5 curated reference skills included in `examples/` covering all template families. | Manual inspection and `eval` test. | All 5 examples score ≥ 90 (Grade A). | **Passed** |
| **AC6.07** | Library test suite passes 100%. | Unit tests in `test_library.py`. | 100% passing tests (6/6 passed). | **Passed** |

---

## Phase 7 — Beginner-Friendly Experience

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC7.01** | Running `python3 -m skillfactory` without args opens clean numbered menu. | Interactive CLI test. | Clear menu with numbered choices displayed. | **Passed** |
| **AC7.02** | Error messages explain what happened, why, and what to do next (no raw stack traces). | Error message review checklist. | 100% of user-facing errors meet clarity rubric. | **Passed** |
| **AC7.03** | Quickstart guides available for macOS, Windows, and Linux. | Manual verification of documentation. | 3 complete, tested OS guides in `docs/quickstart/`. | **Passed** |
| **AC7.04** | CLI supports `NO_COLOR` and contains no color-only semantic signals. | Environment variable test `NO_COLOR=1`. | Output contains zero ANSI color escape sequences. | **Passed** |
| **AC7.05** | Beginner glossary covers all core concepts in simple language. | Review of `docs/glossary.md`. | ≥ 15 core concepts explained simply. | **Passed** |
| **AC7.06** | First-time beginner usability trial succeeds in ≤ 10 minutes. | Usability test protocol. | ≥ 80% test participants succeed without intervention. | **Passed** |

---

## Phase 8 — Security and Reliability

| ID | Criterion | Verification Method | Target Metric | Status |
|---|---|---|---|---|
| **AC8.01** | Secret scanner catches AWS keys, GitHub tokens, OpenAI keys, and private keys. | Test on synthetic credential fixture file. | 100% of credential patterns caught; blocks publish. | **Passed** |
| **AC8.02** | Full test suite passes inside paths with spaces and non-ASCII unicode characters. | Test runner executed in `/tmp/test path 🚀/`. | 100% tests pass. | **Passed** |
| **AC8.03** | Parsers handle fuzzed and malformed input without unhandled crashes. | Fuzz test runner in `test_fuzz.py`. | 0 uncaught exceptions (all return clean error code). | **Passed** |
| **AC8.04** | All GitHub Actions in workflows pinned to full 40-character commit hashes. | Review of `.github/workflows/*.yml`. | 100% actions pinned by SHA. | **Passed** |
| **AC8.05** | `SECURITY.md` published with clear vulnerability reporting policy. | File inspection at repo root. | Present and complete. | **Passed** |
| **AC8.06** | GitHub Actions matrix tests pass on `ubuntu-latest`, `macos-latest`, `windows-latest`. | GitHub Actions CI run. | All 3 OS matrix jobs green. | **Passed** |

---

## Phase 9 — Public Release v1.0

| ID | Criterion | Verification Method | Target Metric |
|---|---|---|---|
| **AC9.01** | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md` published. | File inspection at repo root. | Present, complete, community-standard. |
| **AC9.02** | 100% of documents in `docs/` synchronized with implementation. | Documentation audit. | 0 obsolete commands or contradictory instructions. |
| **AC9.03** | Platform compatibility matrix re-verified against official docs with fresh dates. | Verification checklist. | All 4 platforms re-verified within 30 days of release. |
| **AC9.04** | Automated GitHub Actions release workflow packages verified release assets. | Trigger release tag in sandbox. | Clean release created with release notes. |
| **AC9.05** | README features clear hero visual / animated demo. | Visual review of `README.md`. | High-quality visual demonstration present. |
| **AC9.06** | Git tag `v1.0.0` pushed and confirmed. | `git tag -v v1.0.0`. | Tag verified and released. |
