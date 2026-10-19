# Implementation Plan & Risk Management

This document defines the execution sequence, dependency graph, critical path, and risk management plan for building Skill Factory from Phase 1 through Phase 9.

---

## 1. Phase Dependency Graph

```text
[ Phase 0: GitHub Foundation ] (Done)
              |
              v
[ Phase 1: Skill Factory Core ] <---------------------------- (Critical Foundation)
  - Data model (`SkillSpec`)
  - Modular package structure
  - Deterministic generator & safe YAML escaping
  - Baseline validator & manifest
              |
              +---------------------------------------+
              |                                       |
              v                                       v
[ Phase 2: Natural Language Builder ]   [ Phase 3: Multi-Agent Compatibility ]
  - Host-AI mode (SKILL.md)               - Platform database (`platforms.json`)
  - Offline guided interview              - Discovery & `skillfactory doctor`
  - Template families                     - Shared folder collision handling
              |                                       |
              +-------------------+-------------------+
                                  |
                                  v
                    [ Phase 4: Installation & Updates ]
                      - Safe install / copy engine
                      - Local registry (`registry.json`)
                      - Atomic backup & rollback
                                  |
                                  v
                    [ Phase 5: Testing & Evaluation ]
                      - Isolated test runner subprocess
                      - AST Static Safety Scanner
                      - 0–100 quality scoring engine
                                  |
                                  v
                    [ Phase 6: Library, Export & Discovery ]
                      - Local indexing & search
                      - Zip export / safe import
                      - GitHub publisher assistant
                      - Curated example skills
                                  |
                                  v
                    [ Phase 7: Beginner Experience ]
                      - Interactive numbered menu
                      - Friendly error messages
                      - Cross-platform quickstart guides
                      - Accessibility audit (`NO_COLOR`)
                                  |
                                  v
                    [ Phase 8: Security & Reliability ]
                      - Hardening & fuzzing
                      - Secret & credential scanner
                      - Edge-case verification
                      - Full OS matrix CI tests
                                  |
                                  v
                    [ Phase 9: Public Release v1.0 ]
                      - Final documentation synchronization
                      - Governance files (CONTRIBUTING, etc.)
                      - Tagged release `v1.0.0`
```

---

## 2. Critical Path Analysis

The critical path represents the sequence of dependent steps that determines the minimum project duration:

1. **Phase 1 (Core)** is the prerequisite for everything. Without the `SkillSpec` data model, safe YAML emitter, and manifest tracker, no other phase can produce valid output.
2. **Phase 2 & Phase 3** can be developed concurrently or sequentially. Phase 2 standardizes how skills are authored, while Phase 3 establishes where they live and how platforms consume them.
3. **Phase 4 (Installation)** requires both the core skill structure (Phase 1) and platform directory knowledge (Phase 3).
4. **Phase 5 (Testing & Eval)** ensures skills installed by Phase 4 can be proven correct and safe.
5. **Phase 6 through 9** build on the stable core, adding distribution, beginner ergonomics, security hardening, and public release packaging.

---

## 3. Technical Risk Matrix & Mitigations

| Risk ID | Risk Description | Severity | Likelihood | Mitigation Strategy |
| --- | --- | --- | --- | --- |
| **R-01** | **Breaking changes in target AI platforms** (e.g., Claude Code or Cursor changing skill paths or frontmatter). | High | High | Data-driven architecture (`platforms.json`). Platform paths are decoupled from code. `skillfactory doctor` verifies paths live on the user's system. Documented verification dates (PR-15, PR-24). |
| **R-02** | **YAML syntax breakage from user descriptions.** (Special characters like `:`, `#`, `'` breaking YAML frontmatter parsing). | High | Medium | **Addressed immediately in Phase 1.** Implement safe string escaping/quoting for all frontmatter serialization; comprehensive YAML roundtrip tests. |
| **R-03** | **Windows path and permission limitations** (Path separators `\`, max path length 260 chars, restricted symlinks, reserved names). | Medium | High | Use `pathlib.Path` exclusively; keep generated subfolder hierarchies shallow; default to copying rather than symlinks; validate against Windows reserved device names (`CON`, `PRN`, etc.). Run CI on Windows runners. |
| **R-04** | **Subprocess security risk during skill testing.** (A test script hanging indefinitely or damaging user files). | High | Low | Enforce strict timeouts (default 10s); execute tests inside a temporary working copy; set minimal, isolated `PYTHONPATH` in test runner subprocess. |
| **R-05** | **Accidental loss of user work during install or update.** | High | Low | Collision detection: refuse to overwrite unmanaged folders; automatic timestamped backup before any overwrite; one-command `rollback` support. |
| **R-06** | **Beginner confusion from technical error tracebacks.** | Medium | Medium | Wrap top-level CLI commands with user-friendly error handlers. Print what failed, why, and what command to run next. Preserve `--debug` for developer stack traces. |
| **R-07** | **Incomplete skills generated in offline mode.** (Users expecting fully functional code without an AI model). | Medium | High | Explicit honesty in CLI and docs: offline mode clearly indicates when a skill is an "instruction-only" skill vs. a "scaffold stub" requiring manual code implementation. Test stubs are marked `unittest.skip("Not implemented")`. |
| **R-08** | **Dependency creep.** (Well-intentioned PRs introducing third-party packages like `pyyaml` or `click`). | High | Low | Automated CI check `tests/test_no_third_party_imports.py` that verifies 0 external packages are imported at runtime. Enforced in PR reviews. |

---

## 4. Change Management & Governance

- **Single Source of Truth:** The `docs/` directory is maintained alongside code.
- **Traceability:** Every functional requirement (`FR-*`) maps directly to specific tasks (`T*.*`) and acceptance criteria (`AC*.*`).
- **No Silent Changes:** If a requirement needs adjustment during implementation, a new decision (`D-xx`) must be added to `docs/decisions.md` before code changes are made.
