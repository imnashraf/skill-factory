# Functional Requirements

Format: `FR-<AREA>-<nn>`. **Priority**: M = must for v1.0, S = should, C = could. **Phase** = where it is delivered. Parent product requirements are listed in [requirementsTraceability.md](requirementsTraceability.md).

Areas: `CORE` generation engine · `SPEC` skill specification · `VAL` validation · `NL` natural-language builder · `COMPAT` multi-agent · `INST` install/update · `TEST` skill testing · `EVAL` quality evaluation · `LIB` library/discovery · `PUB` sharing/publishing · `UX` experience · `CLI` command interface.

## CLI — command interface

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-CLI-01 | A single entry point `python3 -m skillfactory <command>` (and `py -m skillfactory` on Windows) runs from a cloned repo without `pip install`. | M | 1 |
| FR-CLI-02 | The existing `python3 scripts/create_skill.py --name --description [--output]` keeps working with identical behaviour and exit codes (compatibility wrapper). | M | 1 |
| FR-CLI-03 | Every command supports `--help`, returns exit code 0 on success, 1 on validation/test failure, 2 on usage error, 3 on environment error (e.g. Python too old). | M | 1 |
| FR-CLI-04 | Every command that changes files supports `--dry-run`, which prints the planned changes and writes nothing. | M | 1 |
| FR-CLI-05 | Machine-readable output via `--json` for `validate`, `test`, `eval`, `doctor`, `list`. | S | 1 |
| FR-CLI-06 | `skillfactory doctor` reports Python version, OS, detected AI platforms and their skill folders, write permissions, and Git availability — read-only. | M | 3 |

## SPEC — skill specification (the intermediate format)

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-SPEC-01 | A versioned **Skill Spec** JSON format (`skill-spec.json`, schema version `1`) describes a skill: name, description, purpose, inputs, outputs, steps, examples, edge cases, required tools, scripts needed (yes/no + language), target platforms, license, author. | M | 1 |
| FR-SPEC-02 | The spec is validated against a bundled schema using a stdlib-only validator with clear, field-specific error messages. | M | 1 |
| FR-SPEC-03 | The spec is the **only** input to the builder. Both the host-AI path and the offline path produce a spec (see [architecture.md](architecture.md#natural-language-generation)). | M | 1–2 |
| FR-SPEC-04 | Spec files are saved inside the generated skill under `.skillfactory/skill-spec.json` for regeneration and auditing. | M | 1 |

## CORE — generation engine

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-CORE-01 | `skillfactory new` builds a skill from CLI flags or `--spec FILE`. | M | 1 |
| FR-CORE-02 | Generated package contains: `SKILL.md`, `README.md`, `scripts/` (when needed), `tests/`, `references/`, `examples/`, `LICENSE` (if selected), `.skillfactory/manifest.json`. | M | 1 |
| FR-CORE-03 | Output is **deterministic**: the same spec + same Skill Factory version produces byte-identical files (except the manifest timestamp field). | M | 1 |
| FR-CORE-04 | YAML frontmatter values are always safely serialised (quoted/escaped) so any valid description produces valid YAML. Fixes DEF-01. | M | 1 |
| FR-CORE-05 | Generation is **atomic**: files are written to a temporary sibling folder and renamed into place only after all writes succeed; on failure nothing is left behind. | M | 1 |
| FR-CORE-06 | Never overwrite an existing folder. `--force` is not provided in Phase 1; regeneration over an existing skill is an update (Phase 4). | M | 1 |
| FR-CORE-07 | Templates are plain text files under `skillfactory/templates/`, rendered with `string.Template` (no code execution in templates). | M | 1 |
| FR-CORE-08 | Template families: `instructions-only`, `python-script`, `checklist-review`, `file-transform`, `workflow-runbook`. | M | 1 (2 families), 2 (rest) |
| FR-CORE-09 | Text files are written as UTF-8 with LF line endings on all OSes. | M | 1 |
| FR-CORE-10 | `manifest.json` records: skill name, skill version (semver, starts `0.1.0`), generator version, template id + version, spec schema version, created/updated timestamps (UTC), SHA-256 of every file. | M | 1 |

## VAL — validation

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-VAL-01 | `skillfactory validate PATH` checks the Agent Skills spec rules: `SKILL.md` exists; frontmatter is valid YAML-subset; `name` 1–64 chars, `[a-z0-9-]`, no leading/trailing/consecutive hyphens, equals folder name; `description` 1–1024 chars; `compatibility` ≤ 500 chars; `metadata` string→string. | M | 1 |
| FR-VAL-02 | Portability warnings: platform-specific fields (`allowed-tools`, `disable-model-invocation`, `context`, `paths`, …) flagged with which platforms honour them ([compatibilityMatrix.md](compatibilityMatrix.md)). | M | 3 |
| FR-VAL-03 | Best-practice warnings: `SKILL.md` > 500 lines, body > ~5000 tokens (estimated), broken relative links, references nested more than one level, absolute paths in instructions. | M | 1 (links/paths), 5 (rest) |
| FR-VAL-04 | Cross-platform name checks: reject Windows reserved names (`con`, `prn`, `aux`, `nul`, `com1`–`com9`, `lpt1`–`lpt9`) and platform-reserved names (e.g. Claude Code's `synced`). Fixes DEF-02. | M | 1 |
| FR-VAL-05 | If the optional external tool `skills-ref` is installed, `validate --with-skills-ref` also runs it and merges results; absence is not an error. | C | 5 |
| FR-VAL-06 | Validation writes `.skillfactory/validation.json` (results + timestamp + generator version) when `--record` is passed. | M | 5 |

## NL — natural-language skill builder

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-NL-01 | **Host-AI mode**: the root `SKILL.md` instructs the host assistant to (1) interview the user, (2) write a `skill-spec.json`, (3) run `skillfactory new --spec`, (4) implement scripts and tests, (5) run `validate`, `test`, `eval`, (6) report results. | M | 2 |
| FR-NL-02 | **Offline mode**: `skillfactory interview` asks a fixed, guided question sequence (problem, input, output, steps, examples, edge cases, needs scripts?) and writes a spec. Works with no AI and no network. | M | 2 |
| FR-NL-03 | Offline template selection is deterministic: keyword rules + explicit user choice; the chosen template and reason are shown. | M | 2 |
| FR-NL-04 | Offline mode derives a valid name from the problem text (lowercase, hyphenated, ≤ 64, reserved names avoided) and lets the user confirm/edit. | M | 2 |
| FR-NL-05 | Offline output is honest: instruction-only skills can be complete; skills needing code get documented stubs and tests marked `not-implemented`, and the report says so. | M | 2 |
| FR-NL-06 | Non-interactive offline mode: `skillfactory interview --answers answers.json` for automation and tests. | M | 2 |
| FR-NL-07 | The host-AI workflow never requires Skill Factory to call a model API; the host AI drives Skill Factory through its CLI only. | M | 2 |

## COMPAT — multi-agent compatibility

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-COMPAT-01 | Platform knowledge (skill folders per scope and OS, supported frontmatter fields, reserved names, invocation syntax, reload behaviour, last-verified date and source URL) lives in one data file `skillfactory/data/platforms.json`. | M | 3 |
| FR-COMPAT-02 | Detect installed platforms by presence of their config folders (read-only). | M | 3 |
| FR-COMPAT-03 | Generated skills use only spec-standard frontmatter by default. Platform-specific fields are opt-in per target and reported. | M | 3 |
| FR-COMPAT-04 | `compatibility` frontmatter and `README.md` "Compatibility" section are generated from the matrix, listing only verified targets. | M | 3 |
| FR-COMPAT-05 | Shared-folder awareness: avoid double-installing where one folder serves several tools (e.g. `.agents/skills` read by Cursor, Codex and Antigravity) and warn about duplicate-name conflicts. | M | 3–4 |

## INST — installation, update, uninstall, rollback

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-INST-01 | `skillfactory install PATH --target <platform> --scope <user|project>` copies an allow-listed set of files into the platform folder. Shows plan; asks for confirmation unless `--yes`. | M | 4 |
| FR-INST-02 | Never overwrite an unmanaged folder of the same name; stop and explain. | M | 4 |
| FR-INST-03 | Every install/update/uninstall is recorded in an install registry (`<user-data-dir>/skillfactory/registry.json`) with a backup of the previous version. | M | 4 |
| FR-INST-04 | `update` detects local modifications (hash mismatch vs manifest) and refuses unless the user confirms; the previous version is backed up. | M | 4 |
| FR-INST-05 | `uninstall` removes only files listed in the manifest; unknown files cause a stop-and-ask. | M | 4 |
| FR-INST-06 | `rollback NAME --target` restores the previous backed-up version. At least the last 3 versions are kept (configurable). | M | 4 |
| FR-INST-07 | Install method default is **copy**; `--link` (symlink) is optional where the platform supports it and the OS permits (Windows may require Developer Mode). | S | 4 |
| FR-INST-08 | Self-install: Skill Factory can install itself as a skill into each target platform using the same mechanism. | M | 4 |
| FR-INST-09 | Self-update: `skillfactory self-update` uses `git pull --ff-only` when installed from a Git clone, or explains manual steps for zip installs. No auto-update. | S | 4 |

## TEST — skill testing

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-TEST-01 | `skillfactory test PATH` runs the skill's `tests/` with `unittest` in a subprocess with timeout, cwd set to a temp copy, and minimal environment. | M | 5 |
| FR-TEST-02 | Skipped tests are reported as **not implemented**, never as passing. | M | 5 |
| FR-TEST-03 | Every generated skill includes structural tests (frontmatter valid, referenced files exist) that pass immediately, plus behaviour-test stubs. | M | 1 |
| FR-TEST-04 | Results are written to `.skillfactory/test-results.json` and summarised in plain language. | M | 5 |

## EVAL — quality evaluation

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-EVAL-01 | `skillfactory eval PATH` produces a scored report (structure, spec compliance, portability, documentation, tests, safety) as defined in [eval.md](eval.md). | M | 5 |
| FR-EVAL-02 | Static safety scan of scripts (stdlib `ast` for Python, pattern rules for shell) flags risky operations. | M | 5 |
| FR-EVAL-03 | Optional host-AI evaluation: trigger-phrase checks (does the description match should-trigger / should-not-trigger prompts) run by the host assistant using a provided rubric; results recorded but never required. | S | 5 |

## LIB — library and discovery

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-LIB-01 | `skillfactory list` shows skills installed per platform and scope, with version, managed/unmanaged, and modified status. | M | 6 |
| FR-LIB-02 | Local library: a folder of skills with a generated `index.json` (name, description, version, tags, compatibility, eval score). | M | 6 |
| FR-LIB-03 | `skillfactory search TEXT` searches the local index offline. | M | 6 |
| FR-LIB-04 | Optional remote index: a static `index.json` from a GitHub repository URL the user provides; fetched only on explicit command; checksum-verified. | S | 6 |
| FR-LIB-05 | Curated example skills (≥ 5) shipped in `examples/` covering each template family. | M | 6 |

## PUB — sharing and publishing

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-PUB-01 | `skillfactory export PATH` produces a reproducible `.zip` with checksum (SHA-256) and the manifest. | M | 6 |
| FR-PUB-02 | `skillfactory import FILE.zip` validates checksum, path safety (no `..`, no absolute paths, no symlinks), and runs `validate` + safety scan before extraction completes. | M | 6 |
| FR-PUB-03 | `skillfactory publish PATH` prepares a Git repository (README, LICENSE, `.gitignore`, CI workflow for the skill) and prints the exact `git`/`gh` commands; it never pushes without explicit confirmation. | M | 6 |
| FR-PUB-04 | Pre-publish checklist: license chosen, no secrets detected, eval score ≥ threshold, compatibility claims verified. | M | 6 |

## UX — beginner experience

| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-UX-01 | Every error message says what happened, why, and the next step, in plain language; no raw tracebacks unless `--debug`. | M | 1 (core), 7 (all) |
| FR-UX-02 | Guided interactive mode `skillfactory` (no args) offers a numbered menu: create, validate, test, install, list, help. | M | 7 |
| FR-UX-03 | Quickstart guides per OS, tested by following them on CI runners. | M | 7 |
| FR-UX-04 | Optional local web UI (`skillfactory ui`) served on `127.0.0.1` only, stdlib `http.server`, no external assets. Decision D-09. | C | 7 |
| FR-UX-05 | Glossary of terms (skill, frontmatter, scope, host AI…) linked from all user docs. | M | 7 |
