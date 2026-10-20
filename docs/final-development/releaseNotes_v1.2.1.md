# Skill Factory v1.2.1 — Production Patch Release Notes

**Release Tag**: `v1.2.1`  
**Release Title**: Skill Factory v1.2.1 — PyPI Distribution Release  
**Target Branch**: `main`  
**Publication Status**: PREPARED — PENDING MAINTAINER AUTHORIZATION  

---

## Executive Summary

Skill Factory `v1.2.1` is a dedicated distribution patch release that transitions the PyPI distribution package name to **`agent-skill-factory`**. This resolves PyPI package name similarity collisions with legacy unmaintained packages while fully preserving:

- The Python runtime import package: **`skillfactory`** (e.g. `import skillfactory`).
- Both established CLI entry points: **`skillfactory`** and **`skill-factory`**.
- 100% Python Standard Library purity (zero third-party runtime dependencies).
- Full compatibility with all 8 supported AI coding assistants.

---

## What Changed in v1.2.1

### 1. PyPI Distribution Package Renamed to `agent-skill-factory`

- In `pyproject.toml`, `[project].name` is set to `agent-skill-factory`.
- PyPI installation command is now:

  ```bash
  pip install agent-skill-factory
  ```

- The existing release `v1.2.0` on GitHub and all Git history remain preserved and unmodified.

### 2. Preserved Runtime Names & CLI Commands

- The internal Python package remains `skillfactory`.
- Users and scripts continue to invoke:

  ```bash
  skillfactory --version
  skill-factory --version
  ```

- All subcommands (`guide`, `doctor`, `new`, `validate`, `test`, `eval`, `scan`, `pack`, `search`, `install`, `update`, `uninstall`) function identically.

### 3. GitHub Actions OIDC Trusted Publishing Configuration

- Updated `.github/workflows/pypi-publish.yml` to target `https://pypi.org/p/agent-skill-factory` under the `pypi` environment.
- Configured to publish via GitHub Actions OpenID Connect (OIDC) Trusted Publisher registered under PyPI project `agent-skill-factory`.

---

## Installation & Upgrade Instructions

### From PyPI

```bash
pip install --upgrade agent-skill-factory
```

### From GitHub Release Artifacts

```bash
pip install https://github.com/imnashraf/skill-factory/releases/download/v1.2.1/agent_skill_factory-1.2.1-py3-none-any.whl
```

### Verification

```bash
skillfactory --version
# Expected: skillfactory 1.2.1

skill-factory --version
# Expected: skillfactory 1.2.1

skillfactory doctor
# System & multi-agent diagnostics report
```
