# Showcase Demo 05 — Test Inventory Analyzer

Deterministic software quality utility scanning codebases to catalog test suites, detect duplicate test cases, and identify untested source modules.

## Quick Summary

- **Domain**: Software Engineering & Quality Assurance (Test Architecture / Coverage Gap Assessment)
- **Problem**: Teams lack quick visibility into which modules lack test suites and where duplicate or skipped tests exist.
- **Solution**: Sub-second AST-based test cataloging and source module mapping without running slow dynamic instrumentation.
- **Integrity**: Clear distinction between static test inventory and dynamic runtime line-coverage instrumentation.

## Package Contents

- [problem-statement.md](file:///Users/mna/skill-factory/skill-factory/showcase/software-engineering/test-inventory/problem-statement.md): Business problem, user personas, input data specs, and QA boundaries.
- [demo-guide.md](file:///Users/mna/skill-factory/skill-factory/showcase/software-engineering/test-inventory/demo-guide.md): Step-by-step terminal walkthrough for generation, validation, testing, grading, installation, and execution.
- [SKILL.md](file:///Users/mna/skill-factory/skill-factory/showcase/software-engineering/test-inventory/SKILL.md): Agent Skills compliant instruction document.
- `scripts/main.py`: Fully executable reference script with AST parsing.
- `tests/test_main.py`: Automated unit tests covering valid, invalid, and edge cases.
- `sample-inputs/`: Synthetic test codebases (valid_repo, edge_case_repo).
- `expected-outputs/`: Verified markdown reports and machine-readable JSON files.

## Quick Start Command

```bash
python3 showcase/software-engineering/test-inventory/scripts/main.py \
  showcase/software-engineering/test-inventory/sample-inputs/valid_repo \
  --src-dir src \
  --tests-dir tests
```
