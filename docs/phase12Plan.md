# Phase 12 Execution Plan — Beginner-Friendly Experience

**Phase:** Phase 12  
**Goal:** Reduce technical friction, eliminate raw terminal tracebacks, provide guided setup diagnostics, and ensure a seamless first-use journey for beginners while strictly preserving Skill Factory's local-first, secure architecture.  
**Branch:** `feat/phases-11-14-roadmap`  
**Base Commit:** `5d79852` (Phase 11 validated baseline)  

---

## 1. Context & Objectives

While Skill Factory possesses robust engineering primitives (hashing, AST scanning, multi-platform resolution), users who are new to command-line interfaces or Python packaging can encounter confusing errors (e.g., PATH issues, missing directories, or unhandled exceptions).

Phase 12 focuses on developer experience and usability:

1. **Guided Setup Diagnostics:** Enhance `skillfactory doctor` with `--guided` / `--setup` mode checking Python version, directory permissions, platform presence, and actionable setup advice.
2. **Interactive Interview Refinement:** Ensure `skillfactory interview` and `skillfactory new` prompt beginners clearly with sensible defaults, instant kebab-case feedback, and explicit notice that domain code in `scripts/main.py` requires an AI assistant or human developer.
3. **Platform Selection & Conflict Defense:** Handle scenarios where zero platforms are installed (suggesting `.agents/skills`), multiple platforms exist (prompting interactive selection), or paths are read-only.
4. **Universal 3-Part Error Formatting:** Eliminate unformatted tracebacks in CLI entrypoints by formatting all known exceptions into `What happened`, `Why it happened`, and `What to do next`.
5. **Simulated Usability Test Suite:** Automate end-to-end beginner workflows in `tests/test_beginner_experience.py` to prevent regressions.

---

## 2. Work Breakdown Structure (Tasks)

| Task ID | Component | Description | Target Deliverables |
| :--- | :--- | :--- | :--- |
| **T12.01** | `doctor.py` / `cli.py` | Add guided setup diagnostics (`doctor --guided`) testing PATH, Python 3.9+, write permissions, and AI platform discovery. | Guided doctor CLI flag, diagnostic summary, update/uninstall instructions |
| **T12.02** | `interview.py` | Enhance interactive interview: auto-suggest kebab-case names, prompt for platform target, and state functional boundaries. | Refined `skillfactory interview` and `skillfactory new --interactive` |
| **T12.03** | `installer.py` | Platform selection & conflict defense: handle 0 detected platforms, multi-choice prompt, permission barriers, collision checks. | Improved platform resolution and collision messages |
| **T12.04** | `errors.py` / `cli.py` | Universal exception handler wrapping all CLI commands in standard 3-part format; suppress raw tracebacks unless `--debug` is passed. | Robust top-level error handler in `cli.py` |
| **T12.05** | `tests/` | Implement automated beginner usability scenarios in `tests/test_beginner_experience.py`. | Comprehensive test suite testing the 5-step beginner journey |
| **T12.06** | `docs/` | Document usability validation results and author `docs/phase12Report.md`. | `docs/phase12Report.md`, updated `docs/autonomousExecutionState.md` |

---

## 3. Measurable Acceptance Criteria

- **AC12.01:** Running `skillfactory doctor --guided` outputs a structured readiness checklist with concrete remediation commands for any detected issues.
- **AC12.02:** The interactive creation flow (`interview` / `new -i`) validates inputs step-by-step, provides intelligent defaults, and includes clear functional implementation guidance.
- **AC12.03:** Installation accurately reports available platform targets, warns when 0 assistants are installed, and refuses to silently overwrite user files without `--force`.
- **AC12.04:** Common user mistakes (invalid skill name, nonexistent directory, missing arguments) produce structured 3-part messages with zero raw stack traces.
- **AC12.05:** `tests/test_beginner_experience.py` passes 100% of simulated usability scenarios.

---

## 4. Risks & Mitigations

1. **Risk:** Hiding raw tracebacks might make debugging difficult for advanced developers.  
   **Mitigation:** Provide a global `--debug` flag that displays full Python tracebacks when requested.
2. **Risk:** Interactive prompts might break non-interactive CI/CD pipelines.  
   **Mitigation:** Ensure all commands retain non-interactive default behavior; interactive flows only trigger when stdin is an active TTY or explicitly requested via `--interactive`.
3. **Risk:** Cross-platform path handling differences between Windows and Unix.  
   **Mitigation:** Use `pathlib.Path` exclusively and avoid hardcoded slash separators.
