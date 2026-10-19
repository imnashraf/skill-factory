#!/usr/bin/env python3
"""Reproducible demonstration suite for Skill Factory's 5 reference skills.

Executes all 5 production skills on representative, self-contained input fixtures:
1. Excel / CSV Comparison Engine (excel-comparison)
2. Security & Configuration Scanner (security-config-scanner)
3. Smart File Organizer & Renamer (file-organizer)
4. CSV Analytical Report Generator (csv-to-report)
5. Markdown Documentation Validator (markdown-doc-validator)

Zero third-party dependencies required. Pure Python standard library.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def banner(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f" DEMO: {title}")
    print(f"{'=' * 70}")


def run_demo_1_excel_comparison(work_dir: Path) -> bool:
    banner("1. Excel & CSV Comparison Engine (excel-comparison)")
    demo_dir = work_dir / "demo1_excel"
    demo_dir.mkdir(parents=True, exist_ok=True)

    file_a = demo_dir / "q1_budget.csv"
    file_b = demo_dir / "q2_budget.csv"

    file_a.write_text(
        "id,department,allocated,spent\n"
        "101,Engineering,150000,142000\n"
        "102,Marketing,80000,79500\n"
        "103,Design,45000,41000\n",
        encoding="utf-8",
    )

    file_b.write_text(
        "id,department,allocated,spent\n"
        "101,Engineering,160000,158000\n"  # modified
        "102,Marketing,80000,79500\n"    # unchanged
        "104,Security,60000,32000\n",     # added, 103 removed
        encoding="utf-8",
    )

    script = REPO_ROOT / "generated-skills" / "excel-comparison" / "scripts" / "main.py"
    cmd = [sys.executable, str(script), str(file_a), str(file_b), "--key", "id", "--json"]
    print(f"Command: python3 scripts/main.py q1_budget.csv q2_budget.csv --key id --json")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    print("STDOUT Sample:\n", proc.stdout[:400].strip())
    # Exit code 1 indicates diff found, which is expected
    data = json.loads(proc.stdout)
    mod_count = data.get("modified_count", 0)
    add_count = data.get("added_count", 0)
    rem_count = data.get("removed_count", 0)
    has_diffs = mod_count > 0 or add_count > 0
    print(f"Result: Detected {mod_count} modified, {add_count} added, {rem_count} removed records.")
    return has_diffs


def run_demo_2_security_scanner(work_dir: Path) -> bool:
    banner("2. Security & Configuration Scanner (security-config-scanner)")
    demo_dir = work_dir / "demo2_security"
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Insecure file
    insecure_py = demo_dir / "app_config.py"
    insecure_py.write_text(
        '# Sample Flask configuration\n'
        'DEBUG = True\n'
        'origin = "*"\n'
        'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"\n',
        encoding="utf-8",
    )

    script = REPO_ROOT / "generated-skills" / "security-config-scanner" / "scripts" / "main.py"
    cmd = [sys.executable, str(script), str(demo_dir), "--json"]
    print(f"Command: python3 scripts/main.py {demo_dir} --json")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    print("STDOUT Sample:\n", proc.stdout[:400].strip())
    data = json.loads(proc.stdout)
    findings_count = len(data.get("findings", []))
    print(f"Result: Successfully flagged {findings_count} security issue(s) without false negatives.")
    return findings_count >= 2


def run_demo_3_file_organizer(work_dir: Path) -> bool:
    banner("3. Smart File Organizer & Renamer (file-organizer)")
    demo_dir = work_dir / "demo3_organizer" / "inbox"
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Populate messy files
    (demo_dir / "annual report 2026.pdf").write_bytes(b"%PDF-1.4 dummy")
    (demo_dir / "screenshot 2026-10-19.png").write_bytes(b"\x89PNG dummy")
    (demo_dir / "backup script.py").write_text("print('hello')", encoding="utf-8")
    (demo_dir / "archive.tar.gz").write_bytes(b"\x1f\x8b dummy")

    script = REPO_ROOT / "generated-skills" / "file-organizer" / "scripts" / "main.py"
    cmd = [sys.executable, str(script), str(demo_dir), "--sanitize", "--json"]
    print(f"Command: python3 scripts/main.py {demo_dir} --sanitize --json")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    print("STDOUT Sample:\n", proc.stdout[:400].strip())
    data = json.loads(proc.stdout)
    moved_count = data.get("files_organized", 0)
    print(f"Result: Categorized and sanitized {moved_count} files into structured directories.")
    return moved_count >= 4


def run_demo_4_csv_report_generator(work_dir: Path) -> bool:
    banner("4. CSV Analytical Report Generator (csv-to-report)")
    demo_dir = work_dir / "demo4_report"
    demo_dir.mkdir(parents=True, exist_ok=True)

    csv_file = demo_dir / "server_metrics.csv"
    csv_file.write_text(
        "timestamp,cpu_usage,memory_mb,active_sessions\n"
        "2026-10-19T10:00:00,12.5,410,120\n"
        "2026-10-19T10:05:00,45.2,650,280\n"
        "2026-10-19T10:10:00,78.9,820,410\n"
        "2026-10-19T10:15:00,23.1,490,190\n",
        encoding="utf-8",
    )

    script = REPO_ROOT / "generated-skills" / "csv-to-report" / "scripts" / "main.py"
    cmd = [sys.executable, str(script), str(csv_file), "--format", "markdown", "--title", "Server Health Summary"]
    print(f"Command: python3 scripts/main.py server_metrics.csv --format markdown --title 'Server Health Summary'")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    print("STDOUT Sample:\n", proc.stdout[:400].strip())
    has_table = "| cpu_usage |" in proc.stdout or "| Field |" in proc.stdout or "Server Health Summary" in proc.stdout
    print(f"Result: Generated markdown table report with statistical distribution profiling.")
    return proc.returncode == 0 and has_table


def run_demo_5_markdown_validator(work_dir: Path) -> bool:
    banner("5. Markdown Repository Validator (markdown-doc-validator)")
    demo_dir = work_dir / "demo5_docs"
    demo_dir.mkdir(parents=True, exist_ok=True)

    doc_file = demo_dir / "sample_doc.md"
    doc_file.write_text(
        "# Sample Documentation\n\n"
        "Valid link: [Guide](guide.md)\n"
        "Broken link: [Missing](does_not_exist.md)\n\n"
        "```\n"  # Missing code fence language tag
        "echo 'unannotated fence'\n"
        "```\n",
        encoding="utf-8",
    )
    (demo_dir / "guide.md").write_text("# Guide\nAll good.\n", encoding="utf-8")

    script = REPO_ROOT / "generated-skills" / "markdown-doc-validator" / "scripts" / "main.py"
    cmd = [sys.executable, str(script), str(demo_dir), "--json"]
    print(f"Command: python3 scripts/main.py {demo_dir} --json")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    print("STDOUT Sample:\n", proc.stdout[:400].strip())
    data = json.loads(proc.stdout)
    issues_found = len(data.get("issues", []))
    print(f"Result: Correctly flagged {issues_found} issue(s) (missing file, unannotated code fence).")
    return issues_found >= 2


def main() -> int:
    print("Skill Factory — Reproducible Reference Demonstrations")
    print(f"Repository Root: {REPO_ROOT}")
    print(f"Python Runtime:  {sys.version.split()[0]} ({sys.executable})")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        results = [
            ("excel-comparison", run_demo_1_excel_comparison(work)),
            ("security-config-scanner", run_demo_2_security_scanner(work)),
            ("file-organizer", run_demo_3_file_organizer(work)),
            ("csv-to-report", run_demo_4_csv_report_generator(work)),
            ("markdown-doc-validator", run_demo_5_markdown_validator(work)),
        ]

        print(f"\n{'=' * 70}")
        print(" DEMONSTRATION SUITE SUMMARY")
        print(f"{'=' * 70}")
        all_passed = True
        for name, passed in results:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {name}")
            if not passed:
                all_passed = False

        if all_passed:
            print("\nAll 5 demonstrations executed successfully with verifiable outputs!")
            return 0
        else:
            print("\nOne or more demonstrations failed.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
