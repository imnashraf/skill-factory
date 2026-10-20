# Deployment, Release & Distribution Strategy

This document defines how Skill Factory is versioned, tested in CI/CD, packaged, and distributed to users worldwide.

---

## 1. Versioning Policy (SemVer 2.0.0)

Skill Factory adheres strictly to [Semantic Versioning 2.0.0](https://semver.org/):

$$\text{Format: } \mathbf{MAJOR}.\mathbf{MINOR}.\mathbf{PATCH}$$

- **`MAJOR` (e.g., `1.0.0` -> `2.0.0`):** Incompatible public CLI changes, removing previously supported flags, or breaking changes to the `SkillSpec` schema.
- **`MINOR` (e.g., `1.0.0` -> `1.1.0`):** Adding new commands, new platform adapters, new template families, or non-breaking features.
- **`PATCH` (e.g., `1.0.0` -> `1.0.1`):** Backward-compatible bug fixes, platform path updates, or documentation improvements.
- **Pre-Release Track:** During Phase 1 through Phase 8, versions will be tagged under `0.x.y` (starting at `0.1.0`), indicating active development before the stable `1.0.0` release in Phase 9.

---

## 2. Git & Commit Workflow

- **Primary Branch (`main`):** Represents the tested, deployable state of Skill Factory. Every commit pushed to `main` must pass 100% of automated GitHub Actions tests.
- **Commit Formatting (Conventional Commits):**
  - `feat:` A new feature or user-facing capability.
  - `fix:` A bug fix or error correction.
  - `docs:` Documentation additions or updates.
  - `test:` Adding or updating tests.
  - `chore:` Maintenance, CI configuration, or housekeeping tasks.
- **Tagging:** Releases are marked with annotated git tags: `git tag -a v1.0.0 -m "Release v1.0.0"`.

---

## 3. Automated CI / CD Pipeline

### 3.1 Push & Pull Request Workflow (`.github/workflows/tests.yml`)

Runs automatically on every push to `main` and on all Pull Requests:

1. **OS Matrix:** Runs parallel jobs on:
   - `ubuntu-latest` (Linux)
   - `macos-latest` (macOS)
   - `windows-latest` (Windows)
2. **Python Matrix:** Tests across:
   - Python 3.9 (minimum supported runtime)
   - Python 3.11 (stable baseline)
   - Python 3.13 (modern release)
3. **Automated Checks:**
   - Execute all unit and integration tests (`python3 -m unittest discover -s tests -v`).
   - Run the zero-dependency validator (`tests/test_no_third_party_imports.py`).
   - Run the strict offline validator (`tests/test_offline.py`).
   - Run a live generator smoke test.

### 3.2 Automated Release Workflow (`.github/workflows/release.yml`)

Triggered automatically when a tag matching `v*` is pushed:

1. Runs full test matrix across all 3 operating systems.
2. Generates release assets:
   - `skill-factory-<version>.zip` (clean source package excluding `.git` and caches).
   - Generates SHA-256 checksums file `checksums.txt`.
3. Creates official GitHub Release draft with automatically generated changelog.

---

## 4. Distribution Channels

Skill Factory provides three simple ways for users to obtain and use the tool:

### Method 1: Git Clone (Recommended for developers & early adopters)

```bash
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory
python3 -m skillfactory
```

- **Benefits:** Instant updates via `git pull`; easy contribution; zero package managers needed.

### Method 2: Standalone Zip Download (For beginners without Git)

- Download `skill-factory-v1.0.0.zip` from GitHub Releases.
- Extract anywhere on your machine.
- Double-click or run `python3 -m skillfactory`.
- Requires zero installation, compilation, or root privileges.

### Method 3: Optional PyPI Package (Phase 9+)

- For users who prefer global CLI installation: `pip install skill-factory`.
- Uses a lightweight, standard `pyproject.toml` (PEP 517/621).
- Maintained with **zero runtime dependencies** so it installs in seconds without polluting the user's Python environment.

---

## 5. Pre-Release Verification Checklist (Phase 9 Gate)

Before tagging any release:

- [ ] All 10 phases completed and accepted against `docs/acceptanceCriteria.md`.
- [ ] All automated tests passing across Linux, macOS, Windows on Python 3.9, 3.11, 3.13.
- [ ] No hardcoded secrets, personal paths, or credentials in any file (`SEC-02`).
- [ ] `docs/compatibilityMatrix.md` verified against latest platform documentation.
- [ ] `CHANGELOG.md` updated with release highlights and upgrade notes.
- [ ] `README.md` quickstart commands verified on a clean machine.
