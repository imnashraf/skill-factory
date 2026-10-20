# Release Notes: Skill Factory v1.2.2

- **Distribution Name**: `agent-skill-factory`
- **Core Package**: `skillfactory`
- **Release Target**: `v1.2.2`
- **Release Type**: Maintenance Patch Release
- **Date**: October 2026

---

## Highlights

Skill Factory `v1.2.2` is a targeted maintenance patch release delivering CLI simulation improvements, full IDE and static type checker compliance, and complete project closure documentation.

### 1. CLI Simulation Support (`--dry-run`)

- Added full dry-run simulation support to `skillfactory install` and `skillfactory uninstall`.
- When passing `--dry-run`, Skill Factory checks target platform directories, validates source skill integrity, checks for existing collisions, and outputs simulated operations without creating directories or writing/removing files on disk.
- Added comprehensive regression tests in `tests/test_installer.py`.

### 2. Static Typing & IDE Diagnostics

- Remediated Pyrefly and static type analysis warnings in `skillfactory/yaml_util.py` and `tests/test_compat.py`.
- Enforced non-None assertions on platform detection and path resolution helpers.

### 3. Markdown Quality & Generator Assurance

- Preserved full zero-violation compliance across all 152+ Markdown files enforcing MD022, MD031, and MD032 standards.
- 13 continuous automated regression tests in `tests/test_markdown_lint.py`.

---

## Upgrade Instructions

```bash
python3 -m pip install --upgrade agent-skill-factory
```

Verify installation:

```bash
skillfactory --version
# Output: skillfactory 1.2.2
```

---

## Full Commit Changelog

- `eb2119a`: fix(types): apply verified pyrefly type diagnostics in yaml_util and test_compat
- `95deb46`: feat(installer): support dry-run simulation in install and uninstall workflows
- `docs`: add final project closure package and update release state
