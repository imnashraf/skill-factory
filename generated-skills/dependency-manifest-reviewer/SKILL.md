---
name: dependency-manifest-reviewer
description: Audits software dependency manifest files for security risks including unpinned packages, wildcards, mutable VCS references, and insecure HTTP download protocols.
---

# Dependency Manifest Reviewer

Security utility for auditing package requirements against software supply chain best practices.

## When to Use This Skill

Activate this skill when:
- Reviewing pull requests that introduce new third-party dependencies.
- Auditing `requirements.txt` or package manifests for supply-chain vulnerabilities.
- Enforcing deterministic version pinning prior to production deployments.

## Workflow Instructions

1. Locate the dependency manifest (e.g. `requirements.txt`).
2. Run the audit reviewer:
   ```bash
   python3 scripts/main.py requirements.txt --output dependency_audit.md
   ```
3. Export JSON report:
   ```bash
   python3 scripts/main.py requirements.txt --json
   ```

## Limitations & Best Practices

- Performs static syntax and pinning inspection.
- Does not contact external package indices (PyPI, npm) without user authorization.
- Zero external Python dependencies required.
