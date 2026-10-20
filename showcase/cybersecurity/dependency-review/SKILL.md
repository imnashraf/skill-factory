---
name: dependency-review
description: Audits package dependency manifests for unpinned versions, conflicting requirements, and insecure HTTP/git references without unverified vulnerability claims.
---

# Dependency Manifest Reviewer

Deterministic software supply chain security utility for auditing `requirements.txt` and `package.json` manifests against configuration hygiene best practices.

## When to Use This Skill

Activate this skill when:

- Auditing dependency manifests in pull requests or security screening pipelines.
- Detecting unpinned dependencies and wildcard version specifiers.
- Isolating conflicting or duplicate version requirements across multi-contributor projects.
- Identifying insecure plaintext `http://` repository URLs and mutable VCS branch references.

## Workflow Instructions

1. Identify the manifest file to review (`requirements.txt` or `package.json`).
2. Run standard security review:

   ```bash
   python3 scripts/main.py requirements.txt --output dependency_report.md
   ```

3. Export machine-readable JSON for CI/CD gating:

   ```bash
   python3 scripts/main.py requirements.txt --json --output dependency_report.json
   ```

## Limitations & Best Practices

- Performs static configuration and pinning analysis only.
- Does not query external vulnerability advisory databases (OSV, NVD) or claim active CVEs without verified source data.
- Does not install packages or execute subprocess pip/npm commands.
- Operates 100% offline and air-gap compatible.
