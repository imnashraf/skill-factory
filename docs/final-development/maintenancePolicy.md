# Long-Term Maintenance Policy & Operational Governance

This document establishes the operational governance, issue triage, security vulnerability disclosure, contribution lifecycle, and deprecation policies for Skill Factory (Workstream 18G).

---

## 1. Operational Philosophy

Skill Factory is designed as a self-sustaining, zero-dependency, open-source utility:

- **Zero Third-Party Runtime Dependencies**: The core platform must never add external runtime packages (`pip dependencies = []`). All features must utilize the Python Standard Library.
- **Privacy by Default**: Zero telemetry, zero usage tracking, zero mandatory cloud accounts.
- **Strict Security Quarantine**: Untrusted or community-submitted code is never executed without explicit, sandboxed user authorization.

---

## 2. Issue Triage & Bug Lifecycle

1. **Intake**: Issues are submitted via GitHub Issue templates (`Bug Report`, `Feature Request`, `Skill Submission`).
2. **Classification**:
   - `P0 - Critical`: Security vulnerability, data loss, regression in core CLI commands (`new`, `validate`, `install`). Resolution target: 48 hours.
   - `P1 - High`: Platform compatibility breakage (e.g., changes in Claude Code or Cursor skill paths). Resolution target: 7 days.
   - `P2 - Medium`: Bug with workaround, minor UI/documentation defect. Resolution target: next minor release.
   - `P3 - Low`: Cosmetic improvements, non-essential enhancements.
3. **Reproduction Standard**: All bug reports must include Python version, OS platform, command invocation, and exact error message.

---

## 3. Coordinated Security Vulnerability Disclosure

- **Reporting Channel**: Security concerns must **not** be opened as public issues. Submit reports via GitHub Private Vulnerability Reporting or via email to the project maintainers.
- **Response Timeline**:
  - Initial acknowledgment: Within 24 hours.
  - Triage and impact assessment: Within 72 hours.
  - Patch development and advisory draft: Within 14 days.
  - Coordinated public disclosure and release: Within 30 days of initial report.

---

## 4. Community Contribution Governance

- **Submission Process**: Community skills and code changes are submitted via GitHub Pull Requests.
- **Automated Screening**: Every PR automatically triggers `scripts/validate_submission.py` to check:
  - Manifest SHA-256 integrity.
  - Spec compliance and naming rules.
  - AST security scan for forbidden calls (`eval`, `exec`, `shell=True`, unauthorized network sockets).
- **Quarantine Guarantee**: Untrusted PR code is never executed in CI workflows.
- **Maintainer Approval**: Merges require at least one maintainer code review and clean CI checks across the platform matrix.

---

## 5. Release Versioning & Deprecation Policy

- **Semantic Versioning (SemVer)**:
  - `MAJOR` (X.0.0): Breaking changes to CLI interface, skill specification schema, or dropped Python support.
  - `MINOR` (1.X.0): Backward-compatible new features (new platforms, domain packs, AI drivers).
  - `PATCH` (1.2.X): Backward-compatible bug fixes and documentation updates.
- **Deprecation Policy**:
  - Any feature or CLI option slated for removal must be marked as deprecated for at least **two minor release cycles** (e.g. deprecated in v1.3.0, removed in v2.0.0).
  - Deprecated commands must emit user-friendly warnings (`[WARN] This command is deprecated...`) detailing the recommended replacement without breaking existing automation.

---

## 6. Compatibility Review Schedule

- **New Python Releases**: Validate against Python release candidates within 30 days of general availability.
- **Supported Python Range**: Maintain active support for all Python versions officially supported by the Python Software Foundation (currently Python 3.9 through 3.14).
