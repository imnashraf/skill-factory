# Skill Factory — Production Security Threat Model & Hardening Audit

**Document Status:** Production Security Audit  
**Phase:** Phase 14 — Production Hardening and Ecosystem Expansion (AC14.03)  
**Security Architecture:** Local-First, Zero-Telemetry, Pure Python Standard Library  
**Date:** 2026-10-19  

---

## 1. Security Architecture & Threat Boundary

Skill Factory operates entirely locally on developer machines. It does not communicate with external clouds, telemetry collectors, or remote APIs.

```text
  [ Developer Workstation ]
  ┌────────────────────────────────────────────────────────┐
  │                                                        │
  │  [ Untrusted Community Skills / Archives ]             │
  │                     │                                  │
  │                     ▼                                  │
  │       [ Skill Factory Security Pipeline ]              │
  │       ├─ Zip Slip Traversal Guard                      │
  │       ├─ Prompt Injection Scanner (INJ001–INJ004)      │
  │       ├─ AST Code Safety Engine (AST001–AST007)        │
  │       ├─ Secret & Credential Regex Scanner             │
  │       ├─ SHA-256 Manifest Cryptographic Integrity     │
  │       └─ Allow-List File Filtering                     │
  │                     │                                  │
  │                     ▼ (Verified Safe)                  │
  │       [ Target AI Assistant Directory ]                │
  │       (.agents/skills, .claude/skills)                 │
  │                                                        │
  └────────────────────────────────────────────────────────┘
```

---

## 2. Threat Analysis Matrix (14 Attack Vectors)

| ID | Attack Vector | Threat Description | Defense Mechanism & Implementation | Automated Regression Test |
| :--- | :--- | :--- | :--- | :--- |
| **TH-01** | **Zip Slip / Path Traversal** | Archive contains relative entries (`../../evil.sh`) to escape target directory. | Strict path resolution check in `import_skill_from_zip()` rejecting any entry whose resolved path escapes destination root. | `tests/test_hardening.py` (`test_zip_path_traversal_and_symlink_defense`) |
| **TH-02** | **Decompression Bomb** | Tiny zip archive expanding to hundreds of gigabytes to exhaust disk. | Uncompressed file size limits and member count validation prior to extraction. | `tests/test_fuzz.py` & `skillfactory/packaging.py` |
| **TH-03** | **Symlink Escape** | Malicious symlink inside skill pointing to sensitive host directories (`/etc`, `~/.ssh`). | Packaging and installation engines resolve symlinks and reject targets escaping the skill directory boundary. | `tests/test_paths.py` & `skillfactory/packaging.py` |
| **TH-04** | **Manifest Tampering** | Attacker alters script logic after skill creation without updating manifest. | Cryptographic verification calculates SHA-256 digests of all tracked files; flags any discrepancies immediately. | `tests/test_hardening.py` (`test_tampered_manifest_detection`) |
| **TH-05** | **Prompt Injection** | Adversarial instructions (`ignore previous instructions`, `you are now DAN`) hijack AI assistant. | Static regex and AST analysis (`INJ001`–`INJ004`) detects jailbreak attempts, persona shifts, and remote pipelines. | `tests/test_catalog.py` (`test_prompt_injection_scanner_rules`) |
| **TH-06** | **Dangerous Code Constructs** | Code contains arbitrary execution calls (`eval`, `exec`, `subprocess(shell=True)`). | AST visitor (`AST001`–`AST007`) parses Python syntax trees and fails security scans on dynamic execution. | `tests/test_hardening.py` (`test_ast_safety_scanner_catches_eval_exec_subprocess`) |
| **TH-07** | **Credential Leakage** | Hardcoded API keys, private keys, or passwords inside instructions or templates. | Shannon entropy analysis and regex rules detect AWS, GitHub, SSH, Slack, and generic secret tokens. | `tests/test_scanner.py` & `tests/test_eval.py` |
| **TH-08** | **Unsafe File Permissions** | Malicious world-writable permissions or unexpected SUID flags on scripts. | Installation applies strict user-owned POSIX permissions (`0o755` for scripts, `0o644` for files). | `skillfactory/installer.py` |
| **TH-09** | **Untrusted Dependencies** | Malicious packages introduced via third-party pip dependencies. | Zero runtime dependency policy; core engine operates 100% on standard library; community rules mandate pure stdlib. | `tests/test_no_third_party_imports.py` |
| **TH-10** | **Partial Installation** | Process crashes midway, leaving half-copied or broken skill directories. | Atomic staging directory pattern: skill is assembled in temporary staging before atomic rename or rollback. | `tests/test_paths.py` (`test_atomic_rollback_on_failure`) |
| **TH-11** | **Uninstallation Collision** | Uninstallation deletes user-authored files outside the installed skill package. | Manifest-aware uninstaller removes only files tracked in registry manifest; preserves user data and unmanaged files. | `tests/test_installer.py` & `tests/test_hardening.py` |
| **TH-12** | **Subprocess Hijack / Hangs** | Skill test runner hangs indefinitely when executing test suites. | Strict subprocess timeouts (10.0s max timeout), pipe isolation, and clean process termination. | `tests/test_tester.py` & `skillfactory/tester.py` |
| **TH-13** | **Reserved Name Collision** | Windows crashes or exhibits undefined behavior on reserved device names (`CON`, `PRN`, `NUL`). | Explicit validation against `WINDOWS_RESERVED_NAMES` and target platform reserved identifiers (e.g. `synced`). | `tests/test_hardening.py` (`test_windows_reserved_names_rejected`) |
| **TH-14** | **Unicode Normalization** | Unicode visual spoofing or case-folding collisions in filenames. | UTF-8 enforcement, LF line-ending normalization, and lowercase kebab-case naming standard. | `tests/test_hardening.py` (`test_unicode_and_nested_filesystem_paths`) |

---

## 3. Defense-in-Depth Summary

1. **Non-Execution Principle:** Skill Factory never executes untrusted code during creation, inspection, catalog searching, or validation. Subprocess execution only occurs during explicit, user-initiated test runs (`skillfactory test`).
2. **Quarantine by Default:** Imported zip archives are unpacked in isolated scratch locations and scanned before installation.
3. **Immutable Manifest Ledger:** Every skill directory includes `.skillfactory/manifest.json` recording cryptographic SHA-256 hashes of all component files.
