# Contributing to Skill Factory

Thank you for your interest in contributing to Skill Factory! We welcome contributions from developers, technical writers, and AI practitioners of all skill levels.

Skill Factory is a **free, open-source project** dedicated to democratizing AI agent skills development. We adhere to a strict **zero runtime third-party dependency** principle and support **Python 3.9+** on macOS, Windows, and Linux.

---

## 1. Guiding Principles

1. **Standard Library Only**: Skill Factory requires zero `pip install` dependencies for core functionality. We strictly utilize Python standard libraries (`pathlib`, `json`, `subprocess`, `ast`, `re`, `zipfile`, etc.).
2. **Dual-Mode Operation**:
   - **Host-AI Mode**: Orchestrated interactively by host AI coding assistants reading the root `SKILL.md`.
   - **Offline Mode**: Operates completely locally via deterministic questionnaires without internet access or API keys.
3. **Safety & Containment**: Never execute untrusted third-party code directly. Skill tests must execute in isolated subprocesses with strict timeouts. Archives must be protected against Zip-Slip path traversal.
4. **Beginner Empathy**: Every error message must explain **What happened**, **Why it happened**, and **What to do next** without exposing raw Python tracebacks to beginners.
5. **Cross-Platform Parity**: Features must function seamlessly across macOS, Linux, and Windows (including PowerShell and Command Prompt).

---

## 2. Setting Up Your Development Environment

You only need Git and Python 3.9+ installed:

```bash
# 1. Clone the repository
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# 2. Run the test suite to verify your setup
python3 -m unittest discover -s tests -v
```

No virtual environments, poetry, pipenv, or node_modules required!

---

## 3. Development Workflow

### Running Tests

Run the full automated test suite using Python's built-in `unittest`:

```bash
# On macOS / Linux:
python3 -m unittest discover -s tests -v

# On Windows:
python -m unittest discover -s tests -v
```

To run a specific test file:

```bash
python3 -m unittest tests/test_core.py -v
```

### Code Style Guidelines

- Follow **PEP 8** conventions.
- Use explicit type annotations (`from __future__ import annotations`, `typing.Optional`, `typing.List`, etc.).
- Ensure all public functions and classes have clear, accurate docstrings.
- Maintain UTF-8 encoding with standard LF (`\n`) line endings.
- Do not import third-party modules in `skillfactory/`.

---

## 4. How to Add a New Template Family

1. Create the new template module under `skillfactory/templates/<family_name>.py`.
2. Implement file generators returning relative file maps:
   - `SKILL.md` with valid YAML frontmatter.
   - `README.md` and `LICENSE`.
   - Minimal runnable examples or test stubs.
3. Register the family name in `VALID_TEMPLATE_FAMILIES` inside `skillfactory/spec.py`.
4. Add routing heuristics to `skillfactory/templates/router.py`.
5. Add unit and validation tests in `tests/test_templates.py`.

---

## 5. Submitting Pull Requests

1. **Fork and branch**: Create a descriptive feature branch from `main` (e.g. `feature/support-xyz-adapter` or `fix/windows-path-bug`).
2. **Write tests**: Every new feature or defect fix must include automated unit tests under `tests/`.
3. **Commit messages**: Use Conventional Commits formatting:
   - `feat(scope): short description`
   - `fix(scope): short description`
   - `docs(scope): short description`
   - `test(scope): short description`
4. **Verify quality gates**:
   - 100% of unit tests must pass.
   - No non-standard library imports.
   - Documentation must be updated.
5. **Open a Pull Request**: Submit your PR with a concise summary of changes and reference any related issues.

---

## 6. Community and Code of Conduct

All contributors and participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, welcoming, and collaborative.
