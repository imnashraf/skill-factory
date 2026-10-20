---
name: test-inventory
description: Scans codebases using AST to catalog test suites, detect duplicate test cases, and identify untested source modules without unverified coverage claims.
---

# Test Inventory Analyzer

Deterministic software engineering utility for inspecting test suites, cataloging test cases and assertions, grouping tests by module, detecting duplicate test names, and highlighting untested source components.

## When to Use This Skill

Activate this skill when:

- Auditing test assets across legacy or expanding codebases.
- Identifying source modules that have no corresponding test files in `tests/`.
- Detecting duplicate test case names and dormant `@skip` decorators.
- Performing fast pre-commit or CI test asset discovery without executing test suites.

## Workflow Instructions

1. Identify the project root directory containing `src/` and `tests/`.
2. Run standard test inventory audit:

   ```bash
   python3 scripts/main.py /path/to/project --output test_inventory.md
   ```

3. Specify custom source and tests directories:

   ```bash
   python3 scripts/main.py /path/to/project --src-dir lib --tests-dir spec --output test_inventory.md
   ```

4. Export structured JSON for quality dashboards:

   ```bash
   python3 scripts/main.py /path/to/project --json --output test_inventory.json
   ```

## Limitations & Best Practices

- Performs static AST analysis only; does not execute test code.
- Does not measure dynamic line/branch execution coverage (requires runtime instrumentation).
- Relies on standard Python naming conventions (`test_*.py`, `*_test.py`).
- Operates 100% offline and safely on local filesystem paths.
