# Test Strategy & Quality Assurance

Skill Factory is built to be a rock-solid, dependable tool. Because users will rely on it to author and install code across different AI platforms and operating systems, our testing strategy must be thorough, deterministic, and fast.

---

## 1. Testing Principles

1. **Standard Library Only:** Tests are written using Python's built-in `unittest` framework. Anyone can run the complete test suite immediately without installing `pytest` or other packages.
2. **Speed & Responsiveness:** The entire test suite must complete in **less than 60 seconds** on any modern computer or CI runner.
3. **Hermetic & Isolated:** Tests never touch the user's real home directory (`~`) or real platform skill directories. Every test creates temporary sandbox directories using `tempfile.TemporaryDirectory` and cleans them up automatically.
4. **Deterministic:** Tests do not rely on network connectivity, external APIs, random seeds, or wall-clock timing.
5. **Cross-Platform Parity:** Every test must pass equally on **macOS**, **Linux**, and **Windows**.

---

## 2. Test Levels & Categories (`TS-xx`)

### TS-01: Unit Tests

Test individual functions and classes in isolation:

- `SkillSpec` schema validation (invalid names, missing descriptions).
- Safe YAML serializer handling problematic strings (colons, hashtags, quotes, unicode).
- Path sanitization and name normalization.
- AST safety scanner node detection.

### TS-02: Integration Tests

Test multi-step workflows end-to-end:

- `new` -> `validate` -> `test` -> `eval` -> `install` -> `update` -> `rollback` -> `uninstall`.
- Verify that registry files and manifests are updated accurately at each step.

### TS-03: Golden-File Determinism Tests

Verify that given a fixed `skill-spec.json`, the generated folder produces byte-identical files against a verified "golden" reference directory (excluding timestamp fields in `manifest.json`).

### TS-04: Negative & Failure-Recovery Tests

Verify graceful failure handling and no half-written states:

- Write failure during atomic generation (simulated by read-only permissions in temp dir).
- Refusal to overwrite an unmanaged directory.
- Rejection of malicious zip archives containing Zip-Slip paths (`../../`).

### TS-05: Zero External Runtime Dependencies Test (`tests/test_no_third_party_imports.py`)

An automated test that scans all imports in the `skillfactory/` package and verifies that 100% of imported modules belong to Python's standard library. Fails immediately if any third-party package is imported.

### TS-06: Strict Offline Test (`tests/test_offline.py`)

An automated test that temporarily monkey-patches `socket.socket` to raise an error if any network connection is attempted. All core commands (`new`, `validate`, `test`, `eval`, `install`) are executed under this constraint to prove 100% offline capability.

### TS-07: Cross-Platform Path & Encoding Tests (`tests/test_paths.py`)

Tests executing operations inside paths with spaces (e.g., `C:\My Documents\Skill Factory`), non-ASCII characters (`/tmp/skills-测试`), and long path structures. Enforces UTF-8 file reading and LF line endings.

### TS-08: Subprocess Timeout & Crash Protection Tests

Tests that the test runner correctly catches and kills scripts with infinite loops (`while True: pass`), reports memory or exit-code errors, and does not hang the CLI.

---

## 3. Test Suite Directory Layout

```text
tests/
├── __init__.py
├── test_generator.py             # Existing Phase 0 tests + Core generation tests
├── test_yaml_util.py             # Safe YAML escaping and edge cases (colons, quotes)
├── test_validator.py             # Spec compliance, reserved names, relative links
├── test_installer.py             # Install, update, collision, rollback, registry
├── test_tester.py                # Subprocess test execution, timeout handling
├── test_eval.py                  # Evaluation scoring, AST safety scanner
├── test_library.py               # Local indexing, zip export, Zip-Slip import defense
├── test_paths.py                 # Windows compatibility, spaces in paths, unicode
├── test_no_third_party_imports.py # Zero third-party dependency enforcement
├── test_offline.py               # Zero network call guarantee
└── test_golden.py                # Byte-for-byte deterministic output checks
```

---

## 4. How to Run Tests

### Run all tests

```bash
python3 -m unittest discover -s tests -v
```

### Run a specific test module

```bash
python3 -m unittest tests/test_validator.py -v
```

### Run in CI

Automated across `ubuntu-latest`, `macos-latest`, and `windows-latest` on Python 3.9, 3.11, and 3.13 on every push and pull request.
