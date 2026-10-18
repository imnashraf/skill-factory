"""Subprocess test runner and test result persistence (Phase 5, Tasks T5.01, T5.05).

Executes skill test suites inside an isolated subprocess with strict timeouts,
restricted environment variables, and structured result persistence (AC5.01, AC5.05).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Match unittest summary lines:
# "Ran 5 tests in 0.012s"
RAN_TESTS_PATTERN = re.compile(r"Ran (\d+) tests? in ([\d\.]+)s")
# "OK" or "OK (skipped=1)"
OK_PATTERN = re.compile(r"OK(?:\s*\((.*)\))?")
# "FAILED (failures=1, errors=2, skipped=1)"
FAILED_PATTERN = re.compile(r"FAILED\s*\((.*)\)")


@dataclass
class TestRunResult:
    success: bool
    tests_run: int
    failures: int
    errors: int
    skipped: int
    duration_sec: float
    timed_out: bool = False
    error_message: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    test_files_found: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_unittest_output(stdout: str, stderr: str, returncode: int) -> Dict[str, Any]:
    """Parse output from standard library unittest discover runner."""
    combined = stderr + "\n" + stdout
    tests_run = 0
    duration_sec = 0.0
    failures = 0
    errors = 0
    skipped = 0

    ran_match = RAN_TESTS_PATTERN.search(combined)
    if ran_match:
        tests_run = int(ran_match.group(1))
        duration_sec = float(ran_match.group(2))

    if returncode == 0:
        success = True
        ok_match = OK_PATTERN.search(combined)
        if ok_match and ok_match.group(1):
            # Parse skipped=N
            for part in ok_match.group(1).split(","):
                part = part.strip()
                if part.startswith("skipped="):
                    skipped = int(part.split("=")[1])
    else:
        success = False
        failed_match = FAILED_PATTERN.search(combined)
        if failed_match and failed_match.group(1):
            for part in failed_match.group(1).split(","):
                part = part.strip()
                if part.startswith("failures="):
                    failures = int(part.split("=")[1])
                elif part.startswith("errors="):
                    errors = int(part.split("=")[1])
                elif part.startswith("skipped="):
                    skipped = int(part.split("=")[1])
        else:
            # Non-zero returncode but no explicit FAILED line (e.g. syntax error or early exit)
            errors = max(1, errors)

    return {
        "success": success,
        "tests_run": tests_run,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "duration_sec": duration_sec,
    }


def find_test_files(skill_dir: Path) -> List[Path]:
    """Find all Python test files in the skill's tests/ directory."""
    tests_dir = Path(skill_dir) / "tests"
    if not tests_dir.exists() or not tests_dir.is_dir():
        return []

    test_files: List[Path] = []
    for path in tests_dir.glob("*.py"):
        if path.name.startswith("test_") or path.name.endswith("_test.py"):
            test_files.append(path)
    return sorted(test_files)


def build_isolated_env(skill_dir: Path) -> Dict[str, str]:
    """Construct an isolated environment for the test subprocess."""
    skill_path = Path(skill_dir).resolve()
    scripts_path = skill_path / "scripts"

    # Minimal environment variables to preserve cross-platform stability
    env: Dict[str, str] = {}
    pass_keys = {
        "PATH",
        "SYSTEMROOT",
        "WINDIR",
        "TEMP",
        "TMP",
        "TMPDIR",
        "USER",
        "HOME",
        "USERPROFILE",
        "LANG",
        "LC_ALL",
    }
    for k in pass_keys:
        if k in os.environ:
            env[k] = os.environ[k]

    # Set restricted PYTHONPATH: skill directory and scripts directory only
    python_paths = [str(skill_path)]
    if scripts_path.exists():
        python_paths.append(str(scripts_path))
    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    # Disable bytecode cache generation in target directory
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["NO_COLOR"] = "1"

    return env


def run_skill_tests(
    skill_dir: Path,
    timeout: float = 10.0,
    save_report: bool = True,
) -> TestRunResult:
    """Execute tests for an Agent Skill in an isolated subprocess.

    Args:
        skill_dir: Root directory of the skill to test.
        timeout: Maximum execution time in seconds (default: 10.0 per AC5.01).
        save_report: If True, writes results to .skillfactory/test-results.json.

    Returns:
        TestRunResult with execution details.
    """
    skill_path = Path(skill_dir).resolve()
    if not skill_path.exists():
        return TestRunResult(
            success=False,
            tests_run=0,
            failures=0,
            errors=1,
            skipped=0,
            duration_sec=0.0,
            test_files_found=0,
            error_message=f"Directory does not exist: {skill_path}",
            stderr=f"Directory does not exist: {skill_path}",
        )

    tests_dir = skill_path / "tests"

    test_files = find_test_files(skill_path)
    if not test_files:
        result = TestRunResult(
            success=True,
            tests_run=0,
            failures=0,
            errors=0,
            skipped=0,
            duration_sec=0.0,
            test_files_found=0,
            stdout="No test files found in tests/",
            stderr="",
        )
        if save_report and skill_path.exists():
            _save_test_report(skill_path, result)
        return result

    env = build_isolated_env(skill_path)
    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(tests_dir),
        "-v",
    ]

    start_time = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(skill_path),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - start_time
        parsed = parse_unittest_output(proc.stdout, proc.stderr, proc.returncode)

        result = TestRunResult(
            success=parsed["success"],
            tests_run=parsed["tests_run"],
            failures=parsed["failures"],
            errors=parsed["errors"],
            skipped=parsed["skipped"],
            duration_sec=round(parsed["duration_sec"] or elapsed, 3),
            timed_out=False,
            stdout=proc.stdout,
            stderr=proc.stderr,
            test_files_found=len(test_files),
        )
    except subprocess.TimeoutExpired as err:
        elapsed = time.monotonic() - start_time
        stdout = err.stdout or ""
        stderr = err.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")

        result = TestRunResult(
            success=False,
            tests_run=0,
            failures=0,
            errors=1,
            skipped=0,
            duration_sec=round(elapsed, 3),
            timed_out=True,
            error_message=f"Test execution timed out after {timeout:.1f} seconds (AC5.01)",
            stdout=stdout,
            stderr=stderr,
            test_files_found=len(test_files),
        )
    except Exception as err:
        elapsed = time.monotonic() - start_time
        result = TestRunResult(
            success=False,
            tests_run=0,
            failures=0,
            errors=1,
            skipped=0,
            duration_sec=round(elapsed, 3),
            timed_out=False,
            error_message=f"Failed to execute tests: {err}",
            test_files_found=len(test_files),
        )

    if save_report:
        _save_test_report(skill_path, result)

    return result


def _save_test_report(skill_path: Path, result: TestRunResult) -> None:
    """Save test results to .skillfactory/test-results.json (AC5.05)."""
    meta_dir = skill_path / ".skillfactory"
    meta_dir.mkdir(parents=True, exist_ok=True)
    report_file = meta_dir / "test-results.json"

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "success": result.success,
        "tests_run": result.tests_run,
        "failures": result.failures,
        "errors": result.errors,
        "skipped": result.skipped,
        "duration_sec": result.duration_sec,
        "timed_out": result.timed_out,
        "test_files_found": result.test_files_found,
        "error_message": result.error_message,
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
    }

    try:
        report_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass  # Non-fatal if report persistence fails
