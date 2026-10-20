# Showcase Demo 04 — Dependency Manifest Reviewer

Deterministic software supply chain utility auditing dependency manifests for insecure protocols, mutable VCS links, conflicts, and unpinned packages.

## Quick Summary

- **Domain**: Cybersecurity & Software Engineering (AppSec / Supply Chain Integrity)
- **Problem**: Insecure protocols, mutable git branch links, and unpinned dependencies introduce supply chain risks into build pipelines.
- **Solution**: Automated, deterministic manifest parsing that detects configuration defects and flags exact remediation actions.
- **Integrity**: Clear distinction between static configuration findings and live CVE intelligence; zero unverified vulnerability claims.

## Package Contents

- [problem-statement.md](file:///Users/mna/skill-factory/skill-factory/showcase/cybersecurity/dependency-review/problem-statement.md): Business problem, user personas, input data specs, and security boundaries.
- [demo-guide.md](file:///Users/mna/skill-factory/skill-factory/showcase/cybersecurity/dependency-review/demo-guide.md): Step-by-step terminal walkthrough for generation, validation, testing, grading, installation, and execution.
- [SKILL.md](file:///Users/mna/skill-factory/skill-factory/showcase/cybersecurity/dependency-review/SKILL.md): Agent Skills compliant instruction document.
- `scripts/main.py`: Fully executable reference script with AST/regex rule checking.
- `tests/test_main.py`: Automated unit tests covering valid, invalid, and edge cases.
- `sample-inputs/`: Synthetic test datasets (valid, invalid, edge-case).
- `expected-outputs/`: Verified markdown reports and machine-readable JSON files.

## Quick Start Command

```bash
python3 showcase/cybersecurity/dependency-review/scripts/main.py \
  showcase/cybersecurity/dependency-review/sample-inputs/valid_requirements.txt
```
