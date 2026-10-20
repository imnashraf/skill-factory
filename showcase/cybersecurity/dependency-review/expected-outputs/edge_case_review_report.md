# Dependency Manifest Review: `edge_case_requirements.txt`

## Executive Summary

- **Manifest File Type:** `requirements.txt`
- **Audit Status:** **ATTENTION REQUIRED (Configuration Risks Found)**
- **Total Dependencies Evaluated:** 7
- **Unique Package Declarations:** 5
- **Total Configuration Findings:** 7

## Detailed Findings & Remediation Register

| Line | Rule ID | Severity | Category | Dependency | Issue Description & Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| L2 | `DEP-01` | **CRITICAL** | Insecure Protocol | `http://insecure-internal-mirror.local/packages/custom-auth-1.0.tar.gz` | Unencrypted HTTP repository or package URL detected (risk of MITM attack). *Action: Enforce HTTPS with certificate validation (https://) for all package indexes and wheels.* |
| L5 | `DEP-02` | **HIGH** | Mutable VCS Reference | `git+https://github.com/mock-org/helper-utils.git` | VCS dependency declared without commit SHA pin (risk of non-reproducible builds). *Action: Pin VCS dependencies to an immutable 40-character commit hash (e.g. git+https://...@commit-sha).* |
| L9 | `DEP-06` | **LOW** | Unbounded / Wildcard Version | `urllib3` | Package 'urllib3' uses wildcard or unbounded constraint '>=2.0.0'. *Action: Apply an upper-bound constraint or exact pin to prevent unexpected breaking changes.* |
| L9 | `DEP-03` | **HIGH** | Conflicting Requirements | `urllib3` | Conflicting specifications for package 'urllib3' found on L8, L9: ['urllib3==1.26.15', 'urllib3>=2.0.0'] *Action: Consolidate to a single consistent version specification across the project.* |
| L14 | `DEP-04` | **MEDIUM** | Duplicate Requirement | `certifi` | Duplicate specification for package 'certifi' declared on L12, L14. *Action: Remove redundant dependency declaration.* |
| L17 | `DEP-05` | **MEDIUM** | Unpinned Dependency | `flask` | Package 'flask' has no version constraint; accepts arbitrary releases. *Action: Specify an explicit pinned version constraint (e.g. flask==X.Y.Z).* |
| L20 | `DEP-06` | **LOW** | Unbounded / Wildcard Version | `fastapi` | Package 'fastapi' uses wildcard or unbounded constraint '>=0.95.0'. *Action: Apply an upper-bound constraint or exact pin to prevent unexpected breaking changes.* |

## Cybersecurity Advisory & Boundary Disclaimer

> [!IMPORTANT]
> **Scope Boundary Notice**: This analysis is a deterministic static configuration review
> targeting version pinning, dependency conflicts, and protocol safety. It does NOT claim
> that any package contains active Common Vulnerabilities and Exposures (CVEs) without
> verification against an authenticated external vulnerability database (e.g. OSV, NVD, GitHub Advisory).
