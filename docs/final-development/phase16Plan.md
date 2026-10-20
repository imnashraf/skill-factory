# Phase 16 Implementation Plan: Real-World Usability & Reliable AI Skill Creation

This document establishes the technical blueprint, architectural components, implementation tasks, and validation strategy for Phase 16.

---

## 1. Objectives & Scope

Phase 16 transforms Skill Factory from a functional developer tool into an intuitive, beginner-friendly platform capable of interpreting complex natural-language skill requests, generating robust specifications with explicit assumption registers, synthesizing behavioral tests, and validating functional correctness through bounded execution loops.

### Workstream Overview

1. **Workstream 16A — End-to-End Beginner Experience (`FR16-01`)**:
   - Cross-platform path guidance (macOS, Linux, Windows conventions).
   - Zero raw stack traces for user-facing commands with friendly remediation advice.
   - Comprehensive guided lifecycle walkthrough (creation, testing, installation, activation, update, rollback, uninstallation).
2. **Workstream 16B — Natural-Language Requirements Engine (`FR16-02`, `FR16-03`)**:
   - Extraction of business objectives, input/output contracts, validation rules, error scenarios, and security requirements.
   - Explicit **Assumption Register** for ambiguities and missing business rules instead of inventing facts.
   - Structured JSON/dataclass representation (`StructuredRequirementSpec`).
3. **Workstream 16C — AI-Assisted Implementation & Bounded Repair (`FR16-04`, `FR16-05`, `FR16-06`)**:
   - Pluggable AI engine separation: requirements analysis -> code generation -> test synthesis -> AST scan -> execution -> repair -> grading.
   - Automated behavioral test generation from acceptance criteria (`skillfactory/ai/test_gen.py`).
   - Deterministic non-AI scaffolding fallback when AI providers are unavailable.
   - Bounded self-repair loop (max 3 retries) with stderr feedback.
4. **Workstream 16D — Functional Correctness & Independent Checks (`FR16-07`)**:
   - Requirement-to-test traceability matrix.
   - Independent validation: AI output cannot grade itself; independent AST scanning and test runners must verify execution.
   - Boundary, negative, and fixture-driven test cases.
5. **Workstream 16E — User Experience Validation (`FR16-08`)**:
   - Automated simulated beginner journey testing (`tests/test_beginner_experience.py`).
   - Metric measurement: step count, latency, error recovery, guidance clarity.
   - Honest labeling: Simulated tests clearly distinguished from live human trials.

---

## 2. Technical Architecture & Component Design

### 2.1 Natural Language Requirements Engine (`skillfactory/ai/requirements.py`)

```text
Natural Language Input
        │
        ▼
[ Requirement Parser ] ──► Tokenize, extract verbs, domain entities, formats
        │
        ├─► Business Objective (e.g., "Reconcile two invoice CSV files")
        ├─► Inputs & Formats (e.g., "source_a.csv", "source_b.csv", CSV format)
        ├─► Expected Outputs (e.g., "discrepancies.md", discrepancy report)
        ├─► Validation Rules (e.g., "Dates must be ISO-8601; Amounts numeric")
        ├─► Error Conditions (e.g., "Missing columns -> exit code 2")
        ├─► Security Controls (e.g., "Path traversal check, size limit 10MB")
        ├─► Acceptance Criteria (e.g., "AC-1: Flag mismatched row amounts")
        └─► Assumption Register (Explicitly records ambiguous rules, e.g.:
              - "Assuming CSV headers are case-insensitive."
              - "Assuming currency defaults to USD if unspecified.")
```

### 2.2 Behavioral Test Generator (`skillfactory/ai/test_gen.py`)

Synthesizes a standalone, executable `unittest.TestCase` suite from the structured requirement specification:

- Positive functional tests for primary user workflow.
- Negative tests for missing arguments, malformed data, and boundary cases.
- Path traversal and security boundary tests.
- 100% standard library compliance (`unittest`, `tempfile`, `pathlib`).

### 2.3 Functional Evaluator (`skillfactory/ai/evaluator.py`)

Provides independent verification of AI-generated skills:

- Runs static AST analysis against 8 security vectors.
- Executes synthesized tests with a 10s timeout in a sandboxed subprocess.
- Compares actual execution outputs with expected requirement criteria.
- Returns an independent verification report with zero self-grading bias.

### 2.4 Beginner Guidance Wizard (`skillfactory/guide.py`)

Enhances onboarding with:

- OS-specific assistant directory resolution:
  - macOS: `~/Library/Application Support/...` or `~/.agents/skills`
  - Linux: `~/.config/...` or `~/.agents/skills`
  - Windows: `%USERPROFILE%\.agents\skills` or `%APPDATA%\...`
- Explanatory guidance for each lifecycle command:
  - `skillfactory new` -> Create
  - `skillfactory test` -> Verify
  - `skillfactory eval` -> Grade
  - `skillfactory install` -> Deploy
  - `skillfactory update` -> Version upgrade
  - `skillfactory rollback` -> Restore backup
  - `skillfactory uninstall` -> Clean removal

---

## 3. Implementation Steps

1. **Step 16.1**: Implement `skillfactory/ai/requirements.py` with intent parsing, entity typing, domain heuristic matching, and the `AssumptionRegister`.
2. **Step 16.2**: Implement `skillfactory/ai/test_gen.py` for behavioral unit test generation mapped to acceptance criteria.
3. **Step 16.3**: Implement `skillfactory/ai/evaluator.py` for independent correctness verification and fixture validation.
4. **Step 16.4**: Enhance `skillfactory/ai/engine.py` to integrate requirements extraction, test generation, bounded repair, and non-AI fallback.
5. **Step 16.5**: Enhance `skillfactory/guide.py` with OS-specific path guidance and complete lifecycle instructions.
6. **Step 16.6**: Add comprehensive unit tests in `tests/test_requirements.py`, `tests/test_test_gen.py`, and `tests/test_beginner_experience.py`.
7. **Step 16.7**: Run all tests, verify 0 regressions, execute simulated beginner journeys, and compile `docs/final-development/phase16Report.md`.

---

## 4. Acceptance Criteria

- All 4 reference test cases ("Excel compare", "Attendance CSV", "RAID log", "Invoice discrepancies") produce structured specifications with non-empty assumption registers.
- Generated tests execute under standard library `unittest` without external dependencies.
- Bounded repair loop handles syntax/assertion errors up to 3 times before failing safely.
- Non-AI fallback generates a complete, valid, passing skill scaffold when no AI model is online.
- All new and existing unit tests pass cleanly.
