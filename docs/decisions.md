# Architecture Decision Log (ADR)

This document records the critical technical and architectural decisions made for Skill Factory. Every decision explains the context, alternatives evaluated, rationale, and consequences.

---

## Decision Index

| ID | Title | Status | Impact Area |
|---|---|---|---|
| **D-01** | Standard-Library-Only Runtime Policy | **Approved** | Core Architecture, Dependencies |
| **D-02** | Canonical Intermediate Specification (`SkillSpec`) | **Approved** | Generation, Dual-Mode Design |
| **D-03** | Minimum Python Runtime Policy (Python 3.9+) | **Approved** | Compatibility, Runtime |
| **D-04** | Lightweight Safe YAML Emitter (No PyYAML) | **Approved** | Security, Dependencies |
| **D-05** | Atomic Sibling Staging for File Generation | **Approved** | Reliability, Recoverability |
| **D-06** | Copy-by-Default for Skill Installation | **Approved** | Installation, Windows Safety |
| **D-07** | Data-Driven Multi-Platform Database (`platforms.json`) | **Approved** | Compatibility, Maintenance |
| **D-08** | Subprocess Execution with Timeouts for Skill Testing | **Approved** | Testing, Security |
| **D-09** | Terminal-First Interactive Experience (CLI over Web UI) | **Approved** | User Experience |
| **D-10** | Zero Built-In AI API Calls (Host Assistant Orchestration) | **Approved** | Cost, Privacy, Simplicity |
| **D-11** | Full User Ownership of Generated Skills (No Viral Attribution) | **Approved** | Legal, Licensing |
| **D-12** | Strict Backward Compatibility for `scripts/create_skill.py` | **Approved** | Compatibility, Governance |

---

## Detailed Records

### D-01: Standard-Library-Only Runtime Policy
- **Status:** **Approved** (from Product Vision PR-01, PR-13).
- **Context:** Many Python tools require `pip install -r requirements.txt`, introducing package manager friction, broken virtual environments, and supply-chain vulnerabilities.
- **Alternatives Considered:**
  - Using `Click` or `Typer` for CLI: cleaner syntax, but requires external wheels.
  - Using `Jinja2` for templates: powerful logic, but introduces code execution risks and external dependencies.
  - Using `PyYAML` for frontmatter: full YAML spec, but requires C bindings or heavy dependencies.
- **Decision:** Skill Factory core CLI shall use **Python standard library only**.
- **Consequences:** Zero installation friction; runs instantly anywhere Python is present. Requires writing lightweight standard-library utilities for YAML serialization and template substitution.

---

### D-02: Canonical Intermediate Specification (`SkillSpec`)
- **Status:** **Approved**.
- **Context:** Natural-language skill creation can happen interactively inside an AI assistant (Claude Code, Cursor, etc.) or offline via a terminal questionnaire.
- **Decision:** Both modes will produce a canonical `skill-spec.json` data structure. The core generator only accepts this spec.
- **Consequences:** Decouples user interaction from file writing. Makes testing straightforward (testing spec generation vs. testing file rendering).

---

### D-03: Minimum Python Runtime Policy (Python 3.9+)
- **Status:** **Approved** (per User Directive).
- **Context:** macOS Command Line Tools currently bundles Python 3.9.6. Linux distributions (Ubuntu 22.04 LTS) include Python 3.10. Modern Python is at 3.12/3.13. Setting the minimum to Python 3.10 would break default macOS developer setups; setting it to 3.8 would require workarounds for `pathlib` and type hinting.
- **Decision:** Set minimum supported Python version to **Python 3.9**. Configure CI matrix to test 3.9, 3.11, and 3.13. Add an early startup check exiting code 3 if Python < 3.9.
- **Consequences:** Out-of-the-box compatibility for macOS users without needing Homebrew or pyenv. Zero third-party runtime dependencies. Automated testing on 3.9, 3.11, and 3.13.

---

### D-04: Lightweight Safe YAML Emitter (No PyYAML)
- **Status:** **Approved**.
- **Context:** Generated `SKILL.md` requires YAML frontmatter. Writing unquoted strings like `description: Compare: diffs` breaks YAML parsers (`DEF-01`).
- **Decision:** Implement a focused, standard-library YAML serializer in `skillfactory/yaml_util.py` that automatically quotes and escapes strings, handles folded multiline text, and enforces frontmatter delimiters.
- **Consequences:** Eliminates external PyYAML dependency while guaranteeing 100% valid YAML frontmatter.

---

### D-05: Atomic Sibling Staging for File Generation
- **Status:** **Approved**.
- **Context:** If generation crashes mid-write (due to power loss, disk full, or bad permissions), the user is left with a corrupt, half-formed folder.
- **Decision:** Files are generated into `.tmp-<uuid>/`. Once all files and manifests are written and validated, the temporary directory is atomically renamed into place via `os.replace()`.
- **Consequences:** Guarantees zero orphan or half-written skills.

---

### D-06: Copy-by-Default for Skill Installation
- **Status:** **Approved**.
- **Context:** On Windows, creating symbolic links requires administrator privileges or Windows Developer Mode enabled.
- **Decision:** Default installation method is **physical file copying** (`copy`). Symlink mode (`--link`) is optional and automatically checks OS support before attempting.
- **Consequences:** Flawless out-of-the-box installation on Windows without administrative permission errors.

---

### D-07: Data-Driven Multi-Platform Database (`platforms.json`)
- **Status:** **Approved**.
- **Context:** AI platforms (Claude Code, Cursor, Codex, Antigravity) update their discovery paths and frontmatter features frequently. Hardcoding these paths in Python classes makes updates cumbersome.
- **Decision:** Store platform discovery paths, scopes, frontmatter support, and documentation dates in a single JSON file: `skillfactory/data/platforms.json`.
- **Consequences:** Platform definitions can be updated, extended, or patched without modifying core generator logic.

---

### D-08: Subprocess Execution with Timeouts for Skill Testing
- **Status:** **Approved**.
- **Context:** Running tests from user-generated or third-party skills inside the main process could allow malicious scripts or bugs to freeze the CLI or manipulate memory.
- **Decision:** Execute skill tests in an isolated `subprocess.run()` with a strict 10-second timeout, temporary working directory, and restricted `PYTHONPATH`.
- **Consequences:** Protects the Skill Factory process from crashes, memory exhaustion, or infinite loops.

---

### D-09: Terminal-First Interactive Experience (CLI over Web UI)
- **Status:** **Approved**.
- **Context:** Beginners need simplicity. A local web UI requires managing browser tabs, ports, and potential port collisions (`127.0.0.1:8000`).
- **Decision:** Focus on a beautifully formatted, numbered terminal menu for Phase 1–8. Consider an optional local web UI only as an experimental enhancement in Phase 7.
- **Consequences:** Immediate reliability in terminal, SSH, and remote container environments.

---

### D-10: Zero Built-In AI API Calls (Host Assistant Orchestration)
- **Status:** **Approved**.
- **Context:** Calling OpenAI, Anthropic, or Gemini APIs directly requires users to provide API keys or pay for usage.
- **Decision:** Skill Factory provides a root `SKILL.md` that teaches the user's **existing host assistant** how to orchestrate the generation workflow. Skill Factory itself makes zero AI API calls.
- **Consequences:** 100% free; zero credential management; preserves user privacy.

---

### D-11: Full User Ownership of Generated Skills
- **Status:** **Approved**.
- **Context:** Open-source generators must not inject restrictive licensing or viral copyright into user-created output.
- **Decision:** Skills generated by Skill Factory belong entirely to the user. The user selects the license for their skill. Skill Factory does not force promotional badges or attribution.
- **Consequences:** Friendly to corporate and proprietary usage.

---

### D-12: Strict Backward Compatibility for `scripts/create_skill.py`
- **Status:** **Approved**.
- **Context:** Existing users and documentation rely on `python3 scripts/create_skill.py --name ... --description ...`.
- **Decision:** Keep `scripts/create_skill.py` as an entry point that delegates to `skillfactory.core` with identical arguments, flags, and exit codes.
- **Consequences:** Existing scripts, CI jobs, and user habits continue to work without disruption.
