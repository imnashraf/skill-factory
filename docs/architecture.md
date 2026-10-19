# Architecture & System Design

Skill Factory is designed to be **simple, reliable, completely free, and standard-library-first**. It has zero mandatory runtime dependencies, meaning any user with a standard Python installation can run it immediately without running `pip install` or managing complex virtual environments.

---

## 1. High-Level System Architecture

Skill Factory operates as a command-line tool, a Python package (`skillfactory`), and an Agent Skill itself (`SKILL.md` at root).

```text
+-------------------------------------------------------------------------------+
|                               User Interaction Layer                         |
|  - Beginner Guided Mode (`python3 -m skillfactory`)                          |
|  - Direct CLI Commands (`new`, `validate`, `test`, `install`, `eval`, etc.)  |
|  - Host AI Assistant Interface (`SKILL.md` prompt driving CLI commands)      |
|  - Legacy Wrapper (`python3 scripts/create_skill.py`)                         |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                             CLI & Dispatch Engine                             |
|  - Command Router & Argument Parser (`argparse`)                             |
|  - Human-friendly Output & Error Presenter (friendly explanations, NO_COLOR)  |
|  - Exit Code Handler (0=success, 1=fail, 2=usage, 3=env error)               |
+-------------------------------------------------------------------------------+
                                      |
    +-------------------+-------------+--------------+------------------+
    |                   |                            |                  |
    v                   v                            v                  v
+------------+  +----------------+           +---------------+  +---------------+
| Core &     |  | Validation &   |           | Compatibility |  | Installation  |
| Generator  |  | Linter Engine  |           | & Discovery   |  | & Rollback    |
+------------+  +----------------+           +---------------+  +---------------+
    |                   |                            |                  |
    |                   |                            |                  |
    v                   v                            v                  v
+------------+  +----------------+           +---------------+  +---------------+
| Test &     |  | Evaluation &   |           | Library &     |  | Offline / NL  |
| Runner     |  | Safety Engine  |           | Packaging     |  | Interviewer   |
+------------+  +----------------+           +---------------+  +---------------+
```

---

## 2. Core Subsystems and Modules

The project is structured under a clean internal module namespace `skillfactory/`:

### `skillfactory.cli` — Command-Line Interface

- **Responsibility:** Handles arguments, command routing, and formatted terminal output.
- **Key Characteristics:**
  - Uses `argparse` from standard library.
  - Formats output for humans with clear symbols (`[OK]`, `[WARN]`, `[ERROR]`) without relying on colors alone.
  - Supports `--json` for machine readability and automated integration.
  - Supports `--dry-run` to preview actions before touching files.

### `skillfactory.core` — Skill Generation Engine

- **Responsibility:** Generates reproducible, portable skill directories from a structured `SkillSpec`.
- **Key Characteristics:**
  - **Deterministic Output:** Given the same spec and template, produces byte-identical files every time (with stable formatting and sorted keys).
  - **Safe YAML Serialization:** Ensures all YAML frontmatter strings (names, descriptions, hints) are properly escaped/quoted to prevent YAML syntax errors (fixes `DEF-01`).
  - **Atomic File Writing:** Writes all files into a temporary staging folder first (`.tmp-<random>`); renames into place only after all files are verified. If anything fails, staging is deleted and the target path remains clean.
  - **Manifest Generation:** Produces `.skillfactory/manifest.json` containing SHA-256 hashes of all generated files, generator version, and timestamp.

### `skillfactory.spec` — The Skill Specification Model

- **Responsibility:** Defines the canonical intermediate format `SkillSpec` (`skill-spec.json`).
- **Why this matters:** By decoupling the *description of the skill* from *how files are written*, both the **Host AI model** and the **Offline deterministic interview** produce the exact same data structure.
- **Fields in `SkillSpec`:**
  - `name`: Lowercase hyphenated identifier (1–64 characters).
  - `description`: What the skill does and when an agent should trigger it (1–1024 characters).
  - `template_family`: One of `instructions-only`, `python-script`, `checklist-review`, `file-transform`, `workflow-runbook`.
  - `inputs` & `outputs`: Data formats or parameters expected.
  - `steps`: Ordered list of workflow steps.
  - `examples`: Sample inputs, user prompts, and expected outputs.
  - `edge_cases`: Documented pitfalls and failure handling.
  - `license`: MIT, Apache-2.0, Unlicense, or Custom.
  - `target_platforms`: List of target AI tools (Claude Code, Cursor, Codex, Antigravity).

### `skillfactory.validator` — Agent Skills Spec & Quality Linter

- **Responsibility:** Enforces compliance with the open [Agent Skills Specification](https://agentskills.io/specification).
- **Checks Performed:**
  1. `SKILL.md` exists and starts with YAML frontmatter `---`.
  2. `name` matches regex `^[a-z0-9]+(?:-[a-z0-9]+)*$`, ≤ 64 chars, no consecutive hyphens, matches parent directory name.
  3. `name` is not a Windows reserved name (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) or tool-reserved name (`synced`).
  4. `description` is non-empty, single block or valid multi-line string ≤ 1024 characters, third-person active phrasing.
  5. Body length checks (advises when `SKILL.md` exceeds 500 lines or estimated 5,000 tokens).
  6. File references in markdown resolve to real files one level deep (e.g., `scripts/run.py` or `references/guide.md`).
  7. No hardcoded absolute local paths (`/Users/...`, `C:\...`).

### `skillfactory.compat` — Multi-Platform Adapter

- **Responsibility:** Encapsulates directory conventions, frontmatter differences, and platform quirks.
- **Data-Driven Architecture:** All platform knowledge lives in `skillfactory/data/platforms.json`. Adding support or updating a platform path requires updating data, not editing core logic.
- **Inspection (`doctor`):** Inspects the host machine to detect which platforms are installed, verifies write access to their skills folders, and flags potential duplicate name collisions across shared folders (like `.agents/skills/`).

### `skillfactory.installer` — Safe Installation, Update, and Rollback

- **Responsibility:** Safely moves skill files into target AI agent discovery folders.
- **Key Safety Mechanisms:**
  - **Copy-by-Default:** Safe copy of allow-listed files only (no hidden IDE caches, no test fixtures from Skill Factory itself).
  - **Collision Prevention:** Refuses to overwrite unmanaged directories.
  - **Registry & Backup:** Maintains a global/user registry at `<user_config>/skillfactory/registry.json`. Backs up previous versions before any update.
  - **Atomic Rollback:** Reverts instantly to a previous backup snapshot if an update causes issues.

### `skillfactory.tester` — Automated Skill Test Runner

- **Responsibility:** Runs automated tests packaged inside the skill's `tests/` folder.
- **Isolation:** Runs tests in a separate subprocess with an execution timeout (e.g., 10 seconds), minimal environment variables, and working directory pinned to a temporary copy.
- **Honest Status Reporting:** Clearly distinguishes between `PASSED`, `FAILED`, and `NOT IMPLEMENTED / SKIPPED`.

### `skillfactory.eval` — Quality & Safety Evaluation Engine

- **Responsibility:** Calculates an objective quality score (0–100) across structure, spec compliance, portability, documentation, test completeness, and static script safety.
- **Static Safety Scanner:** Parses Python scripts into an AST (Abstract Syntax Tree) to check for suspicious operations (e.g., destructive system calls, hardcoded tokens) and generates warnings.

---

## 3. How Natural-Language Skill Generation Works

A key requirement is that Skill Factory works **with or without** an external AI model. Here is exactly how both modes operate:

### Mode A: Host-AI Generation (When inside Claude Code, Cursor, Codex, or Antigravity)

In this mode, Skill Factory does **not** make any API calls. Instead, the host assistant executes the instructions in Skill Factory's root `SKILL.md`:

1. **Interactive Interview:** The host AI interviews the user about their problem, required inputs, edge cases, and target platforms.
2. **Spec Generation:** The host AI structures the user's answers into a valid `skill-spec.json`.
3. **Scaffolding:** The host AI runs `python3 -m skillfactory new --spec skill-spec.json` to generate the correct deterministic skeleton, tests, and manifest.
4. **Implementation:** The host AI fills in the actual Python logic inside `scripts/`, fleshes out `references/`, and writes thorough test cases in `tests/`.
5. **Verification Loop:** The host AI runs `python3 -m skillfactory test <skill-dir>` and `python3 -m skillfactory eval <skill-dir>`. If any test fails, the host AI inspects the error and fixes it.
6. **Reporting:** The host AI presents the verified skill, test results, and eval score to the user.

### Mode B: Offline Deterministic Generation (No AI Model Available)

When running in a bare terminal, offline, or without an AI assistant:

1. **Guided Questionnaire (`skillfactory interview`):** The CLI presents a step-by-step sequence of plain-language questions in the terminal:
   - What problem does this skill solve?
   - What inputs does it accept?
   - Does it require custom scripts, or just instructions?
   - What are the major steps?
2. **Template Selection:** A deterministic rule engine maps the answers to the best template family (e.g., text parsing -> `file-transform`; verification checklist -> `checklist-review`).
3. **Scaffolding & Stubs:** The CLI generates the complete spec and renders the skill package.
4. **Honest Stubs:** For skills requiring executable scripts, the generator creates fully documented Python stubs with `TODO` markers and unit tests marked `unittest.skip("Not implemented")`.
5. **Clear Instructions:** The terminal output tells the beginner exactly how to test their skill and how to either write the script manually or import it into an AI tool later.

---

## 4. Data Flow Diagram

```text
[ User Input / Plain Language ]
       |
       +---> (Mode A: Host AI Prompt) ----> [ Host Model Generates JSON ] ---+
       |                                                                     |
       +---> (Mode B: CLI Interview)  ----> [ Deterministic CLI Parser ] ----+
                                                                             |
                                                                             v
                                                                   [ skill-spec.json ]
                                                                             |
                                                                             v
                                                                 [ skillfactory.core ]
                                                                             |
                                                     +-----------------------+-----------------------+
                                                     |                       |                       |
                                                     v                       v                       v
                                                [ SKILL.md ]        [ scripts/ & tests/ ]   [ manifest.json ]
                                                     |                       |                       |
                                                     +-----------------------+-----------------------+
                                                                             |
                                                                             v
                                                                 [ Staged Output Folder ]
                                                                             |
                                                                             v
                                                                   [ skillfactory.val ]
                                                                             |
                                                                             v
                                                            [ Final Validated Skill Package ]
```

---

## 5. Technology Stack & Design Constraints

| Component | Choice | Rationale |
| --- | --- | --- |
| **Language** | Python 3.9+ | Universal availability across macOS, Linux, and Windows. |
| **Dependencies** | Python Standard Library only | Zero install burden, no supply-chain breakage, 100% offline reliability. |
| **File Formats** | UTF-8 Markdown, JSON, YAML-subset | Standard, portable, human-readable, easily parsed. |
| **CLI Framework** | Standard `argparse` | Lightweight, robust, standard POSIX exit codes, no dependencies. |
| **Template Engine** | `string.Template` | Safe interpolation without code execution risk (unlike Jinja2/eval). |
| **Testing** | Standard `unittest` | Built into Python; runs everywhere out of the box. |
| **CI / CD** | GitHub Actions | Free for open-source repositories; automated testing across OSes and Python versions. |
