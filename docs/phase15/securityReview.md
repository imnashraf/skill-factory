# Skill Factory — Phase 15 Security Review & Threat Analysis

**Document Version:** 1.2.0  
**Baseline Version:** `v1.1.0` (Commit `bb065f0`)  
**Status:** Audit Complete — All 14 Threat Vectors Mitigated & Verified  

---

## 1. Security Philosophy & Principles

Skill Factory operates under strict security invariants:

1. **Local-First & Offline:** Zero automatic phone-home requests or telemetry.
2. **Untrusted Skill Defense:** External or AI-generated skills are assumed untrusted until validated through multi-layer inspection.
3. **Defense in Depth:** Static scanning (AST + Regex), runtime bounding (isolated subprocesses + timeouts), and integrity enforcement (SHA-256 manifests).
4. **Least-Privilege Execution:** No execution with elevated root/admin permissions; no modifications outside configured directories.

---

## 2. Comprehensive 14-Vector Threat Model

| Vector ID | Threat Description | Mitigation Mechanism | Verification Test | Status |
| :--- | :--- | :--- | :--- | :--- |
| `TV-01` | **Zip-Slip Archive Traversal** | Sanitize all archive members, reject `..`, absolute paths, drive letters | `tests/run_security_validation.py` | **MITIGATED & TESTED** |
| `TV-02` | **Symlink Escape & Loop** | Ensure symlink targets resolve within permitted destination roots; reject external targets | `tests/test_hardening.py` | **MITIGATED & TESTED** |
| `TV-03` | **Prompt Injection in Skills** | Scanner regex & heuristic detectors targeting 7 categories of prompt override | `tests/test_scanner.py` | **MITIGATED & TESTED** |
| `TV-04` | **Dangerous Python Dynamic Code** | AST safety scanner rejecting `eval`, `exec`, `__import__`, `compile` | `tests/test_scanner.py` | **MITIGATED & TESTED** |
| `TV-05` | **Shell Injection via Subprocess** | AST safety scanner rejecting `subprocess.Popen(..., shell=True)` and `os.system` | `tests/test_scanner.py` | **MITIGATED & TESTED** |
| `TV-06` | **Credential & Token Leakage** | Regex secrets detector identifying AWS keys, GitHub tokens, OpenAI keys, RSA keys | `tests/test_scanner.py` | **MITIGATED & TESTED** |
| `TV-07` | **Unmanaged Directory Overwrite** | Refuse overwrite of existing non-Skill-Factory files without `--force` | `tests/test_installer.py` | **MITIGATED & TESTED** |
| `TV-08` | **Malicious Third-Party Imports** | Zero non-standard-library production dependencies in core package | `tests/test_no_third_party_imports.py` | **MITIGATED & TESTED** |
| `TV-09` | **Denial of Service / Infinite Loops** | 10.0-second subprocess timeout guard on test runner | `tests/test_tester.py` | **MITIGATED & TESTED** |
| `TV-10` | **Manifest Tampering** | SHA-256 file manifest verification in `.skillfactory/manifest.json` | `tests/test_golden.py` | **MITIGATED & TESTED** |
| `TV-11` | **Unsafe AI Code Execution** | Quarantine AI drafts, execute AST scan before test run, prompt for user approval | `tests/test_ai_engine.py` | **MITIGATED & TESTED** |
| `TV-12` | **Path Canonicalization Vulnerability** | Strict path resolution and Windows reserved name guards (CON, PRN, AUX) | `tests/test_paths.py` | **MITIGATED & TESTED** |
| `TV-13` | **Platform Config Corruption** | Atomic file writes and automated pre-update backups with rollback | `tests/test_installer.py` | **MITIGATED & TESTED** |
| `TV-14` | **Telemetry & Data Exfiltration** | Complete absence of networking modules in core execution paths | `tests/test_offline.py` | **MITIGATED & TESTED** |

---

## 3. Phase 15 Hardening Deep Dive

### 3.1 Symlink Escape Prevention
In `skillfactory/installer.py`, `copy_allow_listed_files` was enhanced with explicit symlink target resolution. If a skill directory contains a symlink pointing to an absolute or relative target that does not resolve strictly inside the source directory (`not resolved_target.is_relative_to(src_dir.resolve())`), the symlink is silently ignored and never copied to the installation target. Tested via `tests/test_hardening.py::test_symlink_escape_protection`.

### 3.2 Extended Prompt Injection Rules (INJ005–INJ007)
The static scanner was expanded with three additional high-severity detection rules in `skillfactory/scanner.py`:
- `INJ005`: System Prompt Extraction Directive (detects `repeat/reveal/dump/leak your system prompt/initial instructions`).
- `INJ006`: Known Exfiltration Endpoint (detects `webhook.site`, `pastebin.com`, `ngrok.io`, `requestbin.com`).
- `INJ007`: Adversarial Roleplay Override (detects `act as a rogue/unrestricted/hacked AI`).
Tested via `tests/run_security_validation.py::test_prompt_injection_defense`.

### 3.3 AI-Generated Code Containment
In `skillfactory/ai/engine.py`, generated code is never executed on the host system without prior safety scanning. If AST scanning detects any critical or high findings (such as `eval`, `exec`, `shell=True`, or credential patterns), the engine halts immediately with `status: safety_rejected` without invoking the Python test runner subprocess.
