# Dependency Manifest Reviewer — Problem Statement

## Domain

Cybersecurity and Software Engineering (Application Security / Software Supply Chain Integrity).

## Business Problem

Software engineering and AppSec teams need to audit third-party dependency manifests (`requirements.txt`, `package.json`, `pyproject.toml`) during CI/CD builds, code reviews, and supplier assessments. In practice:

- Developers frequently add unpinned dependencies (`requests` or `express: "*"`), leaving applications vulnerable to breaking upstream changes and unexpected malicious releases.
- Insecure plaintext protocols (`http://` package repositories) expose internal build pipelines to man-in-the-middle (MITM) package tampering.
- Mutable VCS references (e.g. `git+https://...` without commit SHA pins) allow external code updates to alter build artifacts silently without review.
- Conflicting version pins in multi-author manifests trigger silent resolution mismatches between local and production environments.
- Offline environments often lack real-time access to cloud CVE databases, needing deterministic configuration reviews that do NOT misrepresent configuration warnings as verified CVE vulnerabilities.

## Intended Users

- **Application Security (AppSec) Engineers**: Auditing dependency manifests for software supply chain hygiene.
- **Lead Developers & Code Reviewers**: Screening PRs for unpinned, duplicate, or conflicting dependencies.
- **Release Engineers & DevSecOps Specialists**: Verifying immutable build reproducibility prior to production tagging.

## Input Data Requirements

A standardized software dependency manifest:

1. Python `requirements.txt`
2. Node.js `package.json`

## Key Capabilities & Deterministic Audit Rules

- **Insecure Protocol Flagging (`DEP-01`)**: Detects unencrypted `http://` repository and wheel links (Severity: CRITICAL).
- **Mutable VCS Link Detection (`DEP-02`)**: Detects git/svn references missing immutable commit SHAs (Severity: HIGH).
- **Conflicting Requirements Detection (`DEP-03`)**: Flags mutually incompatible version constraints for the same package in one manifest (Severity: HIGH).
- **Duplicate Declaration Detection (`DEP-04`)**: Identifies redundant declarations of the same dependency (Severity: MEDIUM).
- **Unpinned Version Detection (`DEP-05`)**: Flags bare packages lacking version bounds (Severity: MEDIUM).
- **Unbounded Wildcard Detection (`DEP-06`)**: Flags wildcards (`*`) and unbounded minimums (`>=X.Y` without `<`) (Severity: LOW).

## Strict Cybersecurity Scope & Governance Boundaries

- **Static Configuration Review Only**: This tool performs deterministic pattern-matching on dependency declarations.
- **No Unverified Vulnerability Claims**: The tool does NOT claim that a package has an active CVE/vulnerability without a verified authoritative vulnerability advisory database source (e.g., OSV, CVE, NVD).
- **Offline & Air-Gapped Safe**: Does not query external package registries (PyPI, npm) or make outbound network calls.
