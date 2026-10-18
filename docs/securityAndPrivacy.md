# Security, Privacy & Legal Boundaries

Skill Factory generates and runs code on the user's computer. When dealing with code generation and third-party skills, **security and privacy are non-negotiable**.

This document outlines the threat model, technical safeguards, privacy commitments, and legal licensing considerations.

---

## 1. Threat Model & Risk Analysis

| Threat ID | Threat Description | Attack Vector / Scenario | Impact | Mitigation Strategy |
|---|---|---|---|---|
| **TH-01** | Malicious executable scripts | User imports or runs a third-party skill containing destructive commands (`rm -rf ~`, ransomware, data exfiltration). | Severe: Data loss or compromised machine | Static safety scan (`SEC-01`), explicit review prompt before running scripts (`SEC-03`), isolated test subprocess (`SEC-04`). |
| **TH-02** | Path traversal attacks | A malicious `.zip` archive or skill name contains `../` sequences (`../../.bashrc`). | High: Arbitrary file overwrite outside the skill folder | Strict path sanitization (`SEC-05`), rejection of path traversal components. |
| **TH-03** | Secrets leakage | Skill scripts or markdown prompt instructions inadvertently commit API keys, tokens, or personal passwords. | High: Credential theft | Pre-commit and pre-publish credential scanners (`SEC-02`), `.gitignore` defaults for `.env` files. |
| **TH-04** | Accidental file overwrite | Generator or installer overwrites existing user code or an existing unmanaged skill. | Medium: Lost work | Collision detection, atomic write via temp directory, mandatory backup before update (`SEC-06`). |
| **TH-05** | Silent telemetry / tracking | Tool silently reports usage data, skill names, or IP addresses to a central server. | Medium: Privacy violation | Zero network calls in core codebase; zero telemetry libraries (`SEC-07`). |

---

## 2. Security Boundaries & Requirements (`SEC-xx`)

### SEC-01: Static AST Safety Scanner for Python Scripts
Before executing any script during testing or evaluation, Skill Factory parses the Python code using Python's standard `ast` (Abstract Syntax Tree) module.
It inspects nodes for high-risk operations and issues graded warnings:
- **Critical Warnings (Block unless `--allow-unsafe`):**
  - Use of `eval()`, `exec()`, or `__import__()`.
  - Shell execution with `shell=True` in `subprocess`.
  - Recursive deletion of root or home directory paths (`shutil.rmtree('/')`).
- **Informational Warnings:**
  - Network requests (`urllib`, `http.client`, `socket`).
  - Access to sensitive files (`~/.ssh`, `~/.aws`, `.env`).
  - Reading environment variables (`os.environ`).

### SEC-02: Credential & Secret Scanner
Skill Factory includes a built-in regular expression scanner that checks all files in a skill before `install`, `export`, or `publish`:
- Scans for AWS keys (`AKIA...`), GitHub personal access tokens (`ghp_...`), OpenAI API keys (`sk-...`), private keys (`-----BEGIN PRIVATE KEY-----`), and generic `api_key = "..."` assignments.
- If matches are found, the command halts and directs the user to remove the hardcoded secret.

### SEC-03: Explicit Confirmation for Destructive Actions
- Any operation that writes to, overwrites, or deletes files from disk requires explicit interactive confirmation (`Proceed? [y/N]`).
- For automated testing or non-interactive environments, this can be bypassed only with explicit `--yes`.
- Every modifying command supports `--dry-run` to preview actions without touching the disk.

### SEC-04: Subprocess Execution Limits
When running automated tests on generated skills:
- Tests run in an isolated subprocess with a strict execution timeout (default: 10 seconds).
- The subprocess inherits a restricted environment: `PYTHONPATH` is strictly set to the temporary skill directory, preventing accidental loading of local workspace packages.
- CWD (current working directory) is pinned to a temporary copy of the skill to protect the user's active workspace.

### SEC-05: Path Validation & Zip Slip Prevention
- When importing skills from `.zip` packages (`skillfactory import`), every entry in the archive is validated.
- Any archive containing paths with `../`, leading slashes (`/` or `C:\`), null bytes, or symbolic links pointing outside the extraction root is immediately rejected with an error.

### SEC-06: Atomic Operations & Sibling Staging
- All file generation and package extraction writes to a hidden sibling directory first (`.tmp-<uuid>`).
- Only after all files are completely written, formatted, and validated is the folder renamed into place using `os.replace()` or `shutil.move()`.
- On any error, the temporary folder is deleted, leaving no corrupted half-states.

### SEC-07: Offline Guarantee
- No core command (`new`, `validate`, `test`, `eval`, `install`, `uninstall`, `list`) makes any network request.
- Network access is only invoked when the user explicitly triggers an external remote command (e.g., checking an optional online index or running `git pull` in `self-update`).

---

## 3. Privacy Commitments

1. **Local-First Execution:** All processing happens directly on your machine. No code, skill names, descriptions, or parameters are ever sent to an external server by Skill Factory.
2. **Transparent Host-AI Disclosure:** When using Skill Factory inside a host AI assistant (Claude Code, Cursor, Codex, Antigravity), **that assistant** transmits prompts and conversation history to its respective AI model provider according to that provider's privacy terms. Skill Factory's documentation clearly discloses this distinction to users (PR-18).
3. **No Crash Reporting or Analytics:** There are no trackers, telemetry cookies, or analytics pings.

---

## 4. Legal & Licensing Obligations (`LEG-xx`)

### LEG-01: Skill Factory License
Skill Factory itself is distributed under the permissive **MIT License**. Users are free to use, modify, distribute, and embed Skill Factory in personal, educational, or commercial workflows.

### LEG-02: Rights to Generated Skills
- **Skills generated by Skill Factory belong 100% to the user.**
- Skill Factory does **not** assert any copyright or license over the output generated by users.
- Users choose the license for their generated skills during creation (e.g., MIT, Apache 2.0, Unlicense, or Proprietary).

### LEG-03: No Viral Attribution
Skill Factory does not force promotional watermarks or mandatory advertising tags into generated skills. A clean comment noting the generator version is included in `.skillfactory/manifest.json` for technical provenance, but user-facing markdown is clean.

### LEG-04: Third-Party Dependencies
Skill Factory's core CLI uses **zero third-party dependencies**. There are no transitive open-source license obligations or conflicting copyleft licenses in the core runtime.
