# Requirements Traceability Matrix (RTM)

This matrix maps every high-level **Product Requirement** (`PR-xx`) to its underlying **Functional & Non-Functional Requirements** (`FR-*`, `NFR-*`, `SEC-*`), the corresponding **Development Tasks** (`T*.*`), the **Test Strategy** (`TS-*`), and the **Acceptance Criteria** (`AC*.*`).

---

## Traceability Table

| PR ID | Product Requirement Summary | Child Requirements | Implementing Tasks | Verification / Tests | Acceptance Criteria | Target Phase |
| --- | --- | --- | --- | --- | --- | --- |
| **PR-01** | Free, MIT-licensed, no paid APIs | NFR-01, LEG-01, LEG-02 | T1.01, T1.04, T8.06 | TS-05, TS-06 | AC1.09, AC8.06 | All |
| **PR-02** | Local-first & offline by default | NFR-06, SEC-07, FR-NL-02 | T1.04, T2.02, T4.02 | TS-06 (`test_offline.py`) | AC2.02, AC4.02 | 1–5 |
| **PR-03** | Comprehensive skill output (SKILL.md, scripts, tests, README, references) | FR-CORE-02, FR-CORE-08 | T1.04, T1.05, T2.05 | TS-01, TS-03 | AC1.05, AC2.05 | 1, 2 |
| **PR-04** | Dual-mode: Host-AI assist & Offline deterministic templates | FR-NL-01, FR-NL-02, FR-NL-05 | T2.01, T2.02, T2.06 | TS-03 (`test_golden.py`) | AC2.01, AC2.02, AC2.06 | 2 |
| **PR-05** | Strict Agent Skills specification compliance | FR-VAL-01, FR-SPEC-01 | T1.02, T1.07, T5.04 | TS-01 (`test_validator.py`) | AC1.02, AC1.07, AC5.04 | 1, 5 |
| **PR-06** | Multi-platform support (Claude, Cursor, Codex, Antigravity) | FR-COMPAT-01..05 | T3.01, T3.02, T3.04 | TS-01 (`test_compat.py`) | AC3.01, AC3.04, AC3.06 | 3 |
| **PR-07** | Cross-platform OS support (macOS, Linux, Windows) | NFR-04, NFR-05, NFR-17 | T1.04, T8.02, T8.06 | TS-07 (`test_paths.py`), CI | AC1.10, AC4.09, AC8.06 | All |
| **PR-08** | Beginner-friendly experience & clear error guidance | FR-UX-01..05, NFR-13 | T7.01, T7.02, T7.05 | TS-01, Usability Trial | AC7.01, AC7.02, AC7.06 | 2, 7 |
| **PR-09** | Safe by default, user confirmation, dry-run, no credentials | NFR-10, SEC-03, FR-CLI-04 | T1.08, T4.02, T8.01 | TS-04, TS-01 | AC1.08, AC4.02, AC8.01 | All, 8 |
| **PR-10** | Automated skill testing and quality evaluation scoring | FR-TEST-01..04, FR-EVAL-01..03 | T5.01, T5.02, T5.03 | TS-08 (`test_eval.py`) | AC5.01, AC5.02, AC5.03 | 5 |
| **PR-11** | Easy installation, updates, uninstallation, rollback | FR-INST-01..09 | T4.01–T4.06 | TS-04 (`test_installer.py`) | AC4.01–AC4.06 | 4 |
| **PR-12** | Skill library, offline search, export/import, GitHub publish | FR-LIB-01..05, FR-PUB-01..04 | T6.01–T6.06 | TS-04 (`test_library.py`) | AC6.01–AC6.06 | 6 |
| **PR-13** | Standard-library-only runtime; zero external dependencies | NFR-02 | T1.01, T1.04, T1.09 | TS-05 (`test_no_third_party.py`) | AC1.09 | All |
| **PR-14** | Public release v1.0, quality CI, complete documentation | NFR-16, NFR-19 | T9.01–T9.06 | CI Matrix, Docs Audit | AC9.01–AC9.06 | 9 |
| **PR-15** | Honest compatibility claims with documented verification dates | FR-COMPAT-01, NFR-15 | T3.01, T9.03 | Platform docs audit | AC3.01, AC9.03 | 3, 9 |
| **PR-16** | Provenance, versioning, manifest SHA-256 hashes | FR-CORE-10, FR-SPEC-04 | T1.06, T4.03 | TS-01 (`test_manifest.py`) | AC1.06, AC4.03 | 1, 4 |
| **PR-17** | Documented Python runtime policy (Python 3.9+) & startup check | NFR-03 | T1.01, T1.10 | CI Matrix (3.9, 3.11, 3.13) | AC1.10 | 1 |
| **PR-18** | Privacy disclosure regarding host AI model providers | SEC-07, FR-NL-01 | T2.01, T7.05 | Docs Review | AC2.01, AC7.05 | 2, 7 |
| **PR-19** | Accessibility standards (NO_COLOR, plain-text, 80-col) | NFR-12, FR-UX-04 | T7.04 | TS-01 (`test_ui_util.py`) | AC7.04 | 1, 7 |
| **PR-20** | Backward compatibility for legacy CLI (`scripts/create_skill.py`) | NFR-15, FR-CLI-02 | T1.09 | Existing `tests/test_generator.py` | AC1.08 | All |
| **PR-21** | Atomic operations & failure recoverability (no orphan files) | NFR-09, FR-CORE-05, SEC-06 | T1.04, T4.04 | TS-04 (`test_atomic.py`) | AC1.04, AC4.04 | 1, 4 |
| **PR-22** | Licensing clarity for generated skills (100% user-owned) | LEG-02, LEG-03 | T1.05, T6.05 | Docs Review & Templates | AC1.05, AC6.05 | 1, 6 |
| **PR-23** | Open-source community governance files | NFR-16 | T8.05, T9.01 | File presence check | AC8.05, AC9.01 | 8, 9 |
| **PR-24** | Data-driven platform configuration (`platforms.json`) | FR-COMPAT-01 | T3.01 | Schema verification test | AC3.01 | 3 |
