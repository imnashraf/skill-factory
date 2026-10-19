# Skill Factory — Quality Evaluation Standards

This document formalizes the objective quality evaluation standards and scoring rubric used by Skill Factory (`skillfactory eval`) to audit Agent Skills before publication and inclusion in the reference catalog.

---

## 1. Evaluation Philosophy

Skill Factory applies an automated, deterministic 100-point rubric across five critical engineering dimensions. The scoring model is designed to:

- **Reward Completeness:** Encourage automated tests, modular documentation, and explicit operational limitations.
- **Enforce Safety:** Heavily penalize hardcoded credentials, untrusted shell executions, and prompt injection attempts.
- **Ensure Portability:** Verify that paths, line endings, and file names function smoothly across macOS, Linux, and Windows.

> **Important Security Notice:** An automated high score or Grade A rating indicates technical compliance and clean static analysis; it **does not** constitute an absolute guarantee of security or functional correctness. All community-contributed skills must be treated as untrusted code and subjected to human review before production deployment.

---

## 2. The 100-Point Scoring Rubric

| Dimension | Identifier | Max Points | Key Focus Areas |
| :--- | :---: | :---: | :--- |
| **Spec Compliance & Structure** | `EV-01` | 25 | File structure, valid YAML frontmatter, kebab-case naming, link integrity |
| **Cross-Platform Portability** | `EV-02` | 20 | Zero absolute paths, Windows reserved names, UTF-8/LF normalization |
| **Documentation & Disclosure** | `EV-03` | 20 | SKILL.md conciseness (<= 500 lines), examples, operational boundaries |
| **Test Coverage & Execution** | `EV-04` | 20 | Subprocess test execution, <= 10s timeout, non-placeholder assertions |
| **Code Safety & Secrets Scan** | `EV-05` | 15 | Zero credentials/tokens, AST safety (no `eval`/`shell=True`), SHA-256 hashes |

---

## 3. Detailed Dimension Breakdown

### Dimension EV-01: Spec Compliance & Structure (25 Points)

1. **Mandatory Files (5 pts):** `SKILL.md` and `README.md` must both exist in the skill root.
2. **Valid Frontmatter (5 pts):** YAML frontmatter must parse without syntax errors and contain `name` and `description`.
3. **Naming Conformance (5 pts):** Skill identifier must conform strictly to lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) and stay between 1 and 64 characters.
4. **Description Quality (5 pts):** Description must be 10–1024 characters and provide clear context on when an AI assistant should trigger the skill.
5. **Relative File Links (5 pts):** All relative markdown links in `SKILL.md` and `README.md` must resolve to existing files on disk.

### Dimension EV-02: Cross-Platform Portability (20 Points)

1. **No Absolute Paths (5 pts):** Zero hardcoded root paths (e.g., `/Users/`, `/home/`, `C:\`) in specifications or scripts.
2. **Reserved Filenames (5 pts):** Zero platform-reserved names (e.g., `CON`, `PRN`, `AUX`, `NUL`, `COM1`, `LPT1`, `.git`, `.venv`).
3. **Encoding & Line Endings (5 pts):** All text files must be valid UTF-8 with standard LF (`\n`) line endings.
4. **Portable Interpreters (5 pts):** Scripts must use portable execution patterns (`#!/usr/bin/env python3` or invocation via `sys.executable`).

### Dimension EV-03: Documentation & Progressive Disclosure (20 Points)

1. **Concise Main Spec (5 pts):** `SKILL.md` must not exceed 500 lines. Extensive instructions must be split into `references/` or `examples/`.
2. **Progressive Disclosure (5 pts):** Modular subdirectories (`examples/`, `references/`) are utilized for complex skills.
3. **Usage Examples (5 pts):** At least one concrete usage example with sample inputs, commands, and expected outputs must be provided.
4. **Limitations Disclosed (5 pts):** Prerequisites, operational boundaries, and unsupported platforms must be explicitly documented.

### Dimension EV-04: Test Coverage & Execution (20 Points)

1. **Test Suite Present (5 pts):** The `tests/` directory must contain at least one runnable Python test file.
2. **Structural Tests Pass (5 pts):** Baseline test structure executes without syntax errors.
3. **Behavioral Execution (5 pts):** Tests run in an isolated subprocess and pass within the strict 10.0-second timeout.
4. **Honest Assertions (5 pts):** Tests must assert real behavioral conditions rather than empty pass statements or unconditional skips.

### Dimension EV-05: Code Safety & Secrets Scan (15 Points)

1. **Clean Secret Scan (5 pts):** Zero exposed AWS keys, GitHub tokens, OpenAI keys, private certificates, or generic high-entropy secrets.
2. **AST Code Safety (5 pts):** Zero dangerous dynamic calls (`eval`, `exec`, `__import__`, `os.system`, or `subprocess.*(..., shell=True)`).
3. **Manifest Integrity (5 pts):** All files match their recorded SHA-256 cryptographic hashes in `.skillfactory/manifest.json`.

---

## 4. Grading Scale & Thresholds

| Total Score | Grade | Classification | Action / Eligibility |
| :---: | :---: | :--- | :--- |
| **90 – 100** | **Grade A** | **Production Ready** | Eligible for immediate inclusion in reference catalog. Safe, portable, fully tested. |
| **80 – 89** | **Grade B** | **Good Quality** | Eligible for community review. Usable and safe, but may have minor test/doc gaps. |
| **60 – 79** | **Grade C** | **Needs Improvement** | Not eligible for reference catalog. Missing behavioral tests or incomplete metadata. |
| **0 – 59** | **Grade F** | **Failing / Insecure** | Rejected. Fails specification rules, contains security findings, or has broken tests. |

---

## 5. Review Criteria for Reference Catalog Inclusion

To be accepted into the official bundled reference catalog:

1. Must score **>= 90 points [Grade A]**.
2. Must report **0 CRITICAL** and **0 HIGH** findings in `skillfactory scan`.
3. Must implement pure Python standard library (zero external pip packages).
4. Must maintain full functional reproducibility in `scripts/run_demos.py`.
