# Release Readiness & Candidate Verification (v1.2.0)

This document certifies the release readiness of **Skill Factory v1.2.0**, detailing built distribution artifacts, cryptographic checksums, verification results, and release notes (Workstream 18F).

---

## 1. Release Identification & Packaging Artifacts

- **Package Name**: `skillfactory` (PyPI Identifier)
- **Version**: `1.2.0`
- **Dual Console Entrypoints**:
  - `skillfactory` -> `skillfactory.cli:main`
  - `skill-factory` -> `skillfactory.cli:main`
- **License**: MIT
- **Runtime Dependencies**: Zero (100% Python Standard Library, `requires-python = ">=3.9"`)

### Distribution Artifacts & SHA-256 Checksums

| Artifact File | Distribution Type | Size | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `skillfactory-1.2.0-py3-none-any.whl` | Wheel Distribution | ~68 KB | `f3f091813ea1b72a4066149935a4837bf5e7dfbbcd8b8edcdd51bf90963bbed5` |
| `skillfactory-1.2.0.tar.gz` | Source Distribution | ~62 KB | `4154bd1bc61ab5325e967d197906661158ebe52cbbd57dd3bd059561de5bf82f` |

---

## 2. Clean Installation Verification Evidence

The built wheel was tested in a clean virtual environment outside the repository (`/tmp/sf_release_verify`):

- **Command**: `pip install --no-cache-dir dist/skillfactory-1.2.0-py3-none-any.whl`
- **Dual Entrypoint Verification**: Both `skillfactory version` and `skill-factory version` reported `skillfactory 1.2.0` with exit code 0.
- **Isolated Execution**: Successfully executed `new`, `validate`, and `search` from `/tmp` with zero runtime dependency issues.

---

## 3. Release Notes: v1.2.0

### Highlights & Key Features

1. **Interactive Beginner Onboarding (`skillfactory guide`)**:
   - OS-specific directory guidance for macOS, Linux, and Windows.
   - Zero raw stack traces for user commands with structured remediation messages.
2. **Natural-Language Requirements & Assumption Register**:
   - Structured parsing of natural language intent into input/output contracts, validation rules, edge cases, and acceptance criteria.
   - Explicit **Assumption Register** documenting ambiguous business rules and user remediation actions.
3. **Behavioral Test Generation & Bounded Self-Repair**:
   - Automated synthesis of executable `unittest.TestCase` suites mapped 1:1 to acceptance criteria.
   - Bounded self-repair loop (max 3 retries) with stderr feedback and AST security interception.
   - Deterministic non-AI fallback scaffolding for offline environments.
4. **3-Tier Domain Taxonomy & Offline Catalog Search**:
   - Standardized taxonomy covering 31 domain categories across Personal, Professional, and Developer domains.
   - Dynamic domain registration API (`register_custom_domain`).
   - Multi-attribute offline catalog search (`--domain`, `--category`, `--platform`, `--grade`, `--type`) in < 10ms.
5. **Curated Domain Skill Packs with Conflict Detection**:
   - 5 curated packs (`office-productivity`, `finance-erp`, `hr-workforce`, `project-management`, `developer-security`) covering 14 production-grade reference skills (all scoring Grade A ≥90/100).
   - `skillfactory pack preview` with pre-installation conflict detection.
6. **Community PR Screening & Security Quarantine**:
   - Automated screening script (`scripts/validate_submission.py`) enforcing quarantine barriers: untrusted community code is never executed automatically.
7. **Production Hardening**:
   - 16-vector threat model audit.
   - 100% Python Standard Library purity (zero third-party dependencies).
   - Tokenless GitHub Actions OIDC Trusted Publishing.

---

## 4. Maintainer Authorization Notice

> [!IMPORTANT]
> **GOVERNANCE NOTICE**: In compliance with autonomous execution rules (Section 4.3):
>
> - Distribution packages (`.whl` and `.tar.gz`) have been prepared, cryptographically checksummed, and verified in an isolated environment.
> - **No automated publication to PyPI or creation of public GitHub release tags has been performed.**
> - Final publication requires maintainer authorization via standard GitHub Actions workflow (`.github/workflows/pypi-publish.yml`).
