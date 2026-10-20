# Test Inventory Analyzer — Problem Statement

## Domain

Software Engineering and Quality Assurance (Test Architecture / Coverage Gap Assessment).

## Business Problem

Engineering teams maintaining rapidly scaling codebases or inheriting legacy services need to understand what automated tests exist, how they map to production modules, and where blind spots remain. In practice:

- Large codebases accumulate duplicate test cases and redundant test functions written across multiple test files.
- Skipped test suites (`@unittest.skip`, `@pytest.mark.skip`) are committed during urgent releases and forgotten, hiding testing regressions.
- Developers add new source modules to `src/` without creating corresponding test suites in `tests/`, creating untested modules.
- Measuring dynamic code coverage requires executing the full test suite with runtime instrumentation (`coverage.py`), which can take 15–45 minutes in large systems.
- Teams need a fast, sub-second static test inventory audit to catalog test assets and detect structural test gaps without claiming unverified line-level coverage.

## Intended Users

- **QA Leads & Test Automation Architects**: Auditing test suite structures and finding untested source modules.
- **Engineering Managers**: Getting instant visibility into test asset distribution and skipped suites.
- **Developers & Code Reviewers**: Checking whether newly created modules have corresponding test suites before merging.

## Input Data Requirements

A project directory tree containing:

- Source directory (`src/` or package root)
- Tests directory (`tests/` or subpackages)

## Key Capabilities & Deterministic Audit Rules

- **AST-Based Test Discovery**: Uses Python's built-in `ast` parser to discover test classes, functions, and assertions without executing untrusted test code.
- **Module Mapping**: Inferred mapping between test files (`test_*.py`, `*_test.py`) and source components.
- **Untested Module Detection**: Identifies source modules (`*.py`) in `src/` that have zero matching test files in `tests/`.
- **Duplicate Test Detection**: Detects identical test function names declared across separate test files.
- **Skipped Test Cataloging**: Detects `@skip` decorators and reports dormant test cases.

## Strict QA Scope Boundaries

- **Static Structural Inventory Only**: Catalogs test functions, assertions, and module mappings.
- **No Uninstrumented Coverage Claims**: This tool does NOT claim dynamic line, statement, or branch coverage without runtime instrumentation evidence.
- **Offline & Safe**: Does not execute tests or import application modules.
