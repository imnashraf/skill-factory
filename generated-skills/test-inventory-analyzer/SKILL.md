---
name: test-inventory-analyzer
description: Scans software projects to catalog and audit automated test suites, counting test cases, assertion density, and skipped tests across directories.
---

# Test Inventory Analyzer

Developer QA utility to catalog test suites and measure test density across codebases.

## When to Use This Skill

Activate this skill when:

- Auditing test coverage and test suite sizes prior to releases.
- Cataloging unit, integration, and end-to-end test cases in a repository.
- Identifying silently skipped or disabled test suites.

## Workflow Instructions

1. Identify the project root or tests directory.
2. Run inventory scan:

   ```bash
   python3 scripts/main.py tests/ --output test_inventory.md
   ```

3. Export JSON report:

   ```bash
   python3 scripts/main.py tests/ --json
   ```

## Limitations & Best Practices

- Performs AST parsing without executing test suites.
- Does not modify code or test definitions.
- Works across any Python 3.9+ repository.
