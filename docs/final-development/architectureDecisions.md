# Architectural Decision Records (ADRs): Skill Factory Master Execution

This document formally records all key architectural decisions, rationale, trade-offs, and compliance constraints established during the Skill Factory master development program (Phases 15–18).

---

## ADR Index

1. [D15-01: PyPI Identifier & Dual Entry Points](#d15-01-pypi-identifier--dual-entry-points)
2. [D15-02: Zero Telemetry & Privacy-by-Default Policy](#d15-02-zero-telemetry--privacy-by-default-policy)
3. [D15-03: Provider-Neutral AI Engine with Pre-Execution AST Quarantine](#d15-03-provider-neutral-ai-engine-with-pre-execution-ast-quarantine)
4. [D16-01: Explicit Assumption Register for Natural-Language Requirements](#d16-01-explicit-assumption-register-for-natural-language-requirements)
5. [D16-02: Independent Functional Correctness Checking & Anti-Self-Grading Bias](#d16-02-independent-functional-correctness-checking--anti-self-grading-bias)
6. [D16-03: Deterministic Non-AI Scaffolding Fallback for Offline Environments](#d16-03-deterministic-non-ai-scaffolding-fallback-for-offline-environments)
7. [D17-01: Extensible 3-Tier Domain Taxonomy with Dynamic Registration](#d17-01-extensible-3-tier-domain-taxonomy-with-dynamic-registration)
8. [D17-02: Pack Preview & Pre-Installation Conflict Detection](#d17-02-pack-preview--pre-installation-conflict-detection)
9. [D17-03: Strict Community Submission Security Quarantine](#d17-03-strict-community-submission-security-quarantine)
10. [D18-01: 100% Python Standard Library Core Purity](#d18-01-100-python-standard-library-core-purity)

---

### D15-01: PyPI Identifier & Dual Entry Points

- **Status**: Accepted & Implemented
- **Context**: A legacy unrelated project exists on PyPI under `skill-factory`. The canonical name for this project is `skillfactory`.
- **Decision**: Publish on PyPI as `skillfactory` while providing dual entrypoints (`skillfactory` and `skill-factory`) in `pyproject.toml` pointing to `skillfactory.cli:main`.
- **Consequences**: Zero naming collision on PyPI; seamless developer experience whether using hyphen or no hyphen.

---

### D15-02: Zero Telemetry & Privacy-by-Default Policy

- **Status**: Accepted & Implemented
- **Context**: Open-source users expect strict privacy when processing local code, documents, and credentials.
- **Decision**: Zero telemetry by default. No network calls to phone home, track usage, or report errors. Community adoption is tracked purely through public GitHub repository metrics (stars, forks, releases).
- **Consequences**: Completely safe for enterprise, air-gapped, and privacy-sensitive development environments.

---

### D15-03: Provider-Neutral AI Engine with Pre-Execution AST Quarantine

- **Status**: Accepted & Implemented
- **Context**: Subprocess timeouts alone do not constitute a security sandbox. Untrusted or LLM-generated code could attempt arbitrary system command execution.
- **Decision**: Implement a decoupled provider interface (`AIProvider`) with drivers for local Ollama and OpenAI-compatible endpoints. Before executing any generated script in a subprocess, run static AST inspection (`scan_python_code`) to intercept `eval()`, `exec()`, `subprocess.Popen(..., shell=True)`, and credential leaks.
- **Consequences**: Model-generated code is safely intercepted before execution; no lock-in to proprietary cloud APIs.

---

### D16-01: Explicit Assumption Register for Natural-Language Requirements

- **Status**: Accepted & Implemented
- **Context**: Natural-language skill prompts are often ambiguous (e.g. unspecified date formats, default currencies, header matching). Guessing blindly leads to silent defects.
- **Decision**: The requirements interpreter must construct an explicit `AssumptionRegister` documenting every assumed business rule, the rationale, and clear user instructions on how to correct the assumption.
- **Consequences**: Complete transparency for beginners and technical users alike.

---

### D16-02: Independent Functional Correctness Checking & Anti-Self-Grading Bias

- **Status**: Accepted & Implemented
- **Context**: Allowing an AI model to declare its own output correct introduces positive bias and hallucinated passing grades.
- **Decision**: All functional correctness checking is performed independently by deterministic standard library test runners and AST scanners. The model generates code and tests, but independent harness tools evaluate traceability and execution results.
- **Consequences**: Reliable, reproducible quality scores (Grade A to F) with zero self-grading bias.

---

### D16-03: Deterministic Non-AI Scaffolding Fallback for Offline Environments

- **Status**: Accepted & Implemented
- **Context**: Users running in offline or resource-constrained environments may not have a running local LLM.
- **Decision**: When no provider is detected or when requested, provide deterministic, functional standard-library implementations for common domains (diffing, validation, log review, reconciliation).
- **Consequences**: The core product remains 100% useful without mandatory AI or cloud dependencies.

---

### D17-01: Extensible 3-Tier Domain Taxonomy with Dynamic Registration

- **Status**: Accepted & Implemented
- **Context**: Skills need consistent categorization across Personal, Professional, and Developer domains while supporting future domain expansions.
- **Decision**: Maintain a canonical 3-tier hierarchy covering 31 domain categories, with a runtime registration API (`register_custom_domain`) allowing plugins and community extensions to register new domains without touching core codebase.
- **Consequences**: Future-proof classification structure.

---

### D17-02: Pack Preview & Pre-Installation Conflict Detection

- **Status**: Accepted & Implemented
- **Context**: Installing a multi-skill pack into an assistant directory could silently overwrite existing user skills.
- **Decision**: Implement `skillfactory pack preview <pack> --target <platform>` which resolves destination directories, scans for colliding folders, and flags conflicts before any write operations occur.
- **Consequences**: Safe, collision-free batch operations.

---

### D17-03: Strict Community Submission Security Quarantine

- **Status**: Accepted & Implemented
- **Context**: Community-submitted pull requests and third-party skills represent untrusted code.
- **Decision**: Automated CI and screening tools (`scripts/validate_submission.py`) must NEVER execute community code automatically. All PR checks must be strictly static (manifest verification, spec checks, AST security screening). Subprocess execution requires explicit operator authorization (`--run-untrusted`).
- **Consequences**: Complete protection against malicious PR supply-chain attacks.

---

### D18-01: 100% Python Standard Library Core Purity

- **Status**: Accepted & Implemented
- **Context**: External runtime dependencies introduce supply chain vulnerabilities, version conflicts, installation hurdles, and packaging bloat.
- **Decision**: The entire core runtime (`skillfactory/`) must have zero third-party dependencies and run purely on Python 3.9+ standard library (`pathlib`, `json`, `argparse`, `urllib`, `ast`, `tempfile`, `unittest`).
- **Consequences**: Instant startup (<10ms), zero dependency conflicts, clean wheel size (<70KB), and universal cross-platform compatibility.
