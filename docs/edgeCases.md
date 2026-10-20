# Edge-Case & Pitfall Catalogue

Building a robust, cross-platform CLI requires anticipating messy real-world inputs, tricky operating system quirks, and adversarial scenarios.

This catalogue defines known edge cases (`EC-xx`), the expected technical defense, and the automated test verifying each behavior.

---

## Edge-Case Matrix

| ID | Edge-Case Scenario | Trigger / Example | Expected System Behavior | Technical Defense & Verification |
| --- | --- | --- | --- | --- |
| **EC-01** | **YAML Break Characters in Description** (Fixes `DEF-01`) | User enters: `Compare files: report diffs` or `#1 tool for PDFs` or `'quoted'` | Frontmatter is valid YAML; description parses back to the exact original string. | `skillfactory/yaml_util.py` uses safe string quoting/folding; verified by `tests/test_yaml_util.py`. |
| **EC-02** | **Invalid Skill Name Format** | User inputs: `MySkill`, `pdf--tool`, `-test`, `excel tool` | Rejects immediately with clear explanation of naming rules (`[a-z0-9-]`, 1–64 chars, no consecutive hyphens). | Regex validation in `skillfactory/validator.py`; verified in `tests/test_validator.py`. |
| **EC-03** | **Windows & Platform Reserved Names** (Fixes `DEF-02`) | Skill named `con`, `aux`, `nul`, `prn`, `com1`, `lpt1`, or `synced` | Rejects with error: *"Name is reserved by Windows or target platform."* | Hardened blacklist in `validator.py`; verified in `tests/test_validator.py`. |
| **EC-04** | **Unicode & Non-ASCII Characters** | Description contains emojis (`🚀`), accents (`café`), or CJK characters (`技能`) | Fully supported without encoding crashes; writes UTF-8 explicitly. | Explicit `encoding='utf-8'` on all file handles; verified in `tests/test_paths.py`. |
| **EC-05** | **Destination Folder Already Exists** | User runs `new` or `install` where target directory already exists | Never overwrites silently. Halts and asks user or recommends `update`. | Directory existence check before writing; verified in `tests/test_generator.py` & `test_installer.py`. |
| **EC-06** | **Filesystem Permission Denied** | Target directory is read-only or owned by another user | Catches `PermissionError`, exits code 3, and displays friendly path advice. | Exception handler in `cli.py`; verified in `tests/test_installer.py`. |
| **EC-07** | **Windows Symlink Privilege Failure** | User runs `--link` on Windows without Developer Mode or Admin rights | Catches `OSError`, explains Windows symlink policy, falls back to safe copying. | Platform check in `installer.py`; verified in `tests/test_installer.py`. |
| **EC-08** | **Zip-Slip Path Traversal** | Imported `.zip` archive contains paths like `../../.bashrc` | Immediate error; halts extraction; deletes staging files. | Member path validation before `extractall()`; verified in `tests/test_library.py`. |
| **EC-09** | **Description Too Long (>1024 Chars)** | User pastes multiple paragraphs into description field | Rejects with message: *"Description must be ≤ 1024 characters."* Suggests moving detail to `references/`. | Length validation in `spec.py`; verified in `tests/test_validator.py`. |
| **EC-10** | **Windows MAX_PATH (260 Chars) Limit** | Deep nested paths on Windows (`C:\Users\...\generated-skills\...`) | Keeps generated subfolder depth minimal (max 2 levels: `<skill>/scripts/`); paths kept short. | Path length check; verified in `tests/test_paths.py`. |
| **EC-11** | **Spaces in Workspace Paths** | Repository path contains spaces: `/Users/Jane Doe/My Skills/` | CLI handles paths seamlessly without splitting arguments. | Quotes all shell subprocess arguments; uses `pathlib.Path`; verified in `tests/test_paths.py`. |
| **EC-12** | **Infinite Loop in Skill Tests** | Generated script contains `while True: pass` | Test runner terminates subprocess after timeout (default 10s) and reports `TIMEOUT`. | `subprocess.run(timeout=10)` in `tester.py`; verified in `tests/test_tester.py`. |
| **EC-13** | **Script Memory Exhaustion (OOM)** | Script attempts to allocate gigabytes of memory | Test runner captures subprocess crash and reports exit code without crashing host CLI. | Subprocess exit code capture; verified in `tests/test_tester.py`. |
| **EC-14** | **Test Makes Network Calls Offline** | Test tries connecting to external website while offline | Fails test gracefully; reports network dependency warning. | Mocked socket test in `tests/test_offline.py`. |
| **EC-15** | **Process Interrupted Mid-Write (SIGINT / Ctrl+C)** | User presses Ctrl+C during file generation | Atomic staging directory deleted; zero partial files remain at target path. | `try...finally` cleanup and `os.replace` atomicity in `core.py`. |
| **EC-16** | **Outdated Python Interpreter (< 3.9)** | User runs with Python 3.8 or older | Early startup check prints: *"Skill Factory requires Python 3.9 or newer. You are running Python X.Y."* and exits code 3. | Version check at top of `__main__.py` and `scripts/create_skill.py`. |
| **EC-17** | **Shared Folder Collisions** | Installing to `.agents/skills/` when both Cursor and Codex are present | Installs once; reports that both Cursor and Codex will detect it; prevents duplicate installs. | Shared folder detection in `compat/resolve.py`. |
| **EC-18** | **Modified Files in Installed Skill** | User edited files in `~/.claude/skills/my-skill/`, then runs `update` | Compares file hashes against `manifest.json`. Warns that local edits will be lost and asks for confirmation. | Hash comparison in `installer.py`; verified in `tests/test_installer.py`. |
| **EC-19** | **Instruction-Only Skills (No Scripts)** | User wants a pure prompt/workflow skill without Python code | Generates clean skill with no `scripts/` folder; tests verify documentation structure without failing. | Supported by `instructions-only` template; verified in `tests/test_golden.py`. |
| **EC-20** | **Empty or Multiline Description Input** | User presses Enter without typing a description, or pastes raw newlines | Rejects empty description; normalizes newlines into single clean paragraph. | Normalization logic in `spec.py`; verified in `tests/test_validator.py`. |
