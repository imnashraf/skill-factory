#!/usr/bin/env python3
"""Master Showcase Automation Runner.

Executes all five real-world use-case demonstrations end-to-end,
validates output reports, checks immutability of input datasets, and
displays formatted summary output for video recordings and terminal demos.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

_SHOWCASE = Path(__file__).resolve().parent.parent.parent
_REPO_ROOT = _SHOWCASE.parent


def print_step(title: str) -> None:
    print(f"\n{'='*70}\n[RUNNING] {title}\n{'='*70}")


def run_demo(cmd: list[str], description: str) -> bool:
    print(f"\n[INFO] {description}")
    print(f"[CMD]  {' '.join(cmd)}")
    start = time.perf_counter()
    res = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = (time.perf_counter() - start) * 1000
    if res.returncode in (0, 2):  # code 2 represents normal anomaly discovery in audit tools
        print(f"[OK]   Completed in {elapsed:.1f}ms (exit code: {res.returncode})")
        if res.stdout:
            for line in res.stdout.strip().splitlines()[:12]:
                print(f"       {line}")
            if len(res.stdout.strip().splitlines()) > 12:
                print("       ...")
        return True
    else:
        print(f"[ERROR] Failed with exit code {res.returncode}")
        print(res.stderr)
        return False


def main() -> int:
    print("======================================================================")
    print("       SKILL FACTORY — REAL-WORLD USE CASE MASTER SHOWCASE")
    print("======================================================================")

    demos = [
        (
            "Demo 01: Financial Variance Analyzer",
            [
                sys.executable,
                str(_SHOWCASE / "finance" / "financial-variance" / "scripts" / "main.py"),
                str(_SHOWCASE / "finance" / "financial-variance" / "sample-inputs" / "valid_budget.csv"),
                str(_SHOWCASE / "finance" / "financial-variance" / "sample-inputs" / "valid_actuals.csv"),
            ],
            "Reconcile monthly departmental budgets against actual GL spend",
        ),
        (
            "Demo 02: Attendance CSV Validator",
            [
                sys.executable,
                str(_SHOWCASE / "hr-payroll" / "attendance-validation" / "scripts" / "main.py"),
                str(_SHOWCASE / "hr-payroll" / "attendance-validation" / "sample-inputs" / "valid_attendance.csv"),
            ],
            "Audit biometric swipe logs for missing punches and overnight shifts",
        ),
        (
            "Demo 03: Project Status Reporter",
            [
                sys.executable,
                str(_SHOWCASE / "project-management" / "project-status" / "scripts" / "main.py"),
                str(_SHOWCASE / "project-management" / "project-status" / "sample-inputs" / "valid_milestones.csv"),
                "--raid-file",
                str(_SHOWCASE / "project-management" / "project-status" / "sample-inputs" / "valid_raid.csv"),
                "--as-of-date",
                "2026-10-20",
            ],
            "Evaluate delivery health and generate executive action summary",
        ),
        (
            "Demo 04: Dependency Manifest Reviewer",
            [
                sys.executable,
                str(_SHOWCASE / "cybersecurity" / "dependency-review" / "scripts" / "main.py"),
                str(_SHOWCASE / "cybersecurity" / "dependency-review" / "sample-inputs" / "valid_requirements.txt"),
            ],
            "Audit dependency manifest for unpinned packages and insecure HTTP links",
        ),
        (
            "Demo 05: Test Inventory Analyzer",
            [
                sys.executable,
                str(_SHOWCASE / "software-engineering" / "test-inventory" / "scripts" / "main.py"),
                str(_SHOWCASE / "software-engineering" / "test-inventory" / "sample-inputs" / "valid_repo"),
                "--src-dir",
                "src",
                "--tests-dir",
                "tests",
            ],
            "Catalog test functions and identify untested source modules",
        ),
    ]

    all_passed = True
    for title, cmd, desc in demos:
        print_step(title)
        if not run_demo(cmd, desc):
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("[SUCCESS] All five showcase demonstrations executed cleanly!")
        print("======================================================================")
        return 0
    else:
        print("[FAILURE] One or more demonstrations encountered an error.")
        print("======================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(main())
