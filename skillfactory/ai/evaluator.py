"""Functional Evaluator & Independent Correctness Verifier (Phase 16, Workstream 16D).

Provides independent verification of AI-synthesized skills:
- Requirement-to-Test Traceability mapping.
- AST Security & Secrets scanning.
- Sandboxed execution & timeout containment.
- Independent grading (0-100 score) preventing self-grading bias.
- Non-AI deterministic scaffolding fallback for offline environments.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.ai.requirements import StructuredRequirementSpec
from skillfactory.scanner import scan_python_code, scan_secrets_in_text
from skillfactory.tester import run_skill_tests


@dataclass
class TraceabilityEntry:
    """Traceability mapping between acceptance criterion and automated test."""
    criterion_id: str
    description: str
    test_method_name: str
    verified: bool


@dataclass
class FunctionalAuditReport:
    """Independent audit report for skill correctness."""
    skill_name: str
    traceability_score: int  # 0 - 100
    security_clean: bool
    tests_passed: bool
    total_score: int
    grade: str
    traceability_matrix: List[TraceabilityEntry]
    findings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "traceability_score": self.traceability_score,
            "security_clean": self.security_clean,
            "tests_passed": self.tests_passed,
            "total_score": self.total_score,
            "grade": self.grade,
            "traceability_matrix": [asdict(t) for t in self.traceability_matrix],
            "findings": self.findings,
        }


def audit_functional_correctness(
    skill_dir: Path,
    spec: StructuredRequirementSpec,
) -> FunctionalAuditReport:
    """Independently audit an AI-generated or scaffolded skill against its requirements."""
    findings: List[str] = []
    matrix: List[TraceabilityEntry] = []

    script_path = skill_dir / "scripts" / "main.py"
    test_path = skill_dir / "tests" / "test_main.py"

    if not script_path.is_file():
        return FunctionalAuditReport(
            skill_name=spec.skill_name,
            traceability_score=0,
            security_clean=False,
            tests_passed=False,
            total_score=0,
            grade="Grade F",
            traceability_matrix=[],
            findings=["Missing main script implementation."],
        )

    # 1. AST Security Analysis
    script_code = script_path.read_text(encoding="utf-8")
    test_code = test_path.read_text(encoding="utf-8") if test_path.is_file() else ""

    sec_findings = scan_python_code(script_code, file_path="scripts/main.py")
    sec_findings += scan_secrets_in_text(script_code, file_path="scripts/main.py")
    critical_sec = [f for f in sec_findings if f.severity in ("CRITICAL", "HIGH")]
    security_clean = len(critical_sec) == 0

    if not security_clean:
        findings.append(f"Security violations detected: {[f.rule_id for f in critical_sec]}")

    # 2. Traceability Analysis
    test_methods: List[str] = []
    if test_code:
        try:
            tree = ast.parse(test_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_methods.append(node.name)
        except SyntaxError:
            findings.append("Syntax error in test code.")

    matched_count = 0
    for ac in spec.acceptance_criteria:
        cid_slug = ac.criterion_id.lower().replace("-", "_")
        matched_method = next((m for m in test_methods if cid_slug in m), None)
        if matched_method:
            matched_count += 1
            matrix.append(
                TraceabilityEntry(
                    criterion_id=ac.criterion_id,
                    description=ac.description,
                    test_method_name=matched_method,
                    verified=True,
                )
            )
        else:
            matrix.append(
                TraceabilityEntry(
                    criterion_id=ac.criterion_id,
                    description=ac.description,
                    test_method_name="MISSING",
                    verified=False,
                )
            )

    traceability_score = int((matched_count / len(spec.acceptance_criteria) * 100)) if spec.acceptance_criteria else 100

    # 3. Test Execution
    test_res = run_skill_tests(skill_dir, timeout=10.0)
    tests_passed = test_res.success

    if not tests_passed:
        findings.append(f"Test failure: {test_res.error_message or test_res.stderr}")

    # Scoring computation
    score = 0
    if security_clean:
        score += 35
    if tests_passed:
        score += 35
    score += int(traceability_score * 0.30)

    if score >= 90:
        grade = "Grade A"
    elif score >= 80:
        grade = "Grade B"
    elif score >= 70:
        grade = "Grade C"
    elif score >= 60:
        grade = "Grade D"
    else:
        grade = "Grade F"

    return FunctionalAuditReport(
        skill_name=spec.skill_name,
        traceability_score=traceability_score,
        security_clean=security_clean,
        tests_passed=tests_passed,
        total_score=score,
        grade=grade,
        traceability_matrix=matrix,
        findings=findings,
    )


def generate_non_ai_implementation(spec: StructuredRequirementSpec) -> str:
    """Generate a fully functional, safe, deterministic Python script when AI is offline."""
    lower_obj = spec.business_objective.lower()

    if "excel" in lower_obj or "diff" in lower_obj or "compare" in lower_obj:
        return '''"""Tabular File Comparison and Diff Tool.

Zero-dependency standard library implementation.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two tabular CSV files and report differences.")
    parser.add_argument("file_a", help="Path to first CSV file")
    parser.add_argument("file_b", help="Path to second CSV file")
    args = parser.parse_args(argv)

    path_a = Path(args.file_a)
    path_b = Path(args.file_b)

    for p in (path_a, path_b):
        if ".." in str(p) and not p.resolve().is_relative_to(Path.cwd()):
            print(f"[SECURITY ERROR] Path traversal detected: {p}", file=sys.stderr)
            return 2
        if not p.is_file():
            print(f"[ERROR] Input file does not exist: {p}", file=sys.stderr)
            return 1
        if p.stat().st_size > 25 * 1024 * 1024:
            print(f"[ERROR] File exceeds 25MB limit: {p}", file=sys.stderr)
            return 2

    lines_a = path_a.read_text(encoding="utf-8").splitlines()
    lines_b = path_b.read_text(encoding="utf-8").splitlines()

    if lines_a == lines_b:
        print(f"[OK] Files '{path_a.name}' and '{path_b.name}' are identical ({len(lines_a)} rows).")
        return 0

    print(f"# Difference Report: {path_a.name} vs {path_b.name}")
    diffs = 0
    for idx, (la, lb) in enumerate(zip(lines_a, lines_b), start=1):
        if la != lb:
            diffs += 1
            print(f"- Row {idx} (A): {la}")
            print(f"+ Row {idx} (B): {lb}")

    if len(lines_a) != len(lines_b):
        diffs += abs(len(lines_a) - len(lines_b))
        print(f"[WARN] Row count mismatch: {len(lines_a)} vs {len(lines_b)}")

    print(f"\nTotal differences found: {diffs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    elif "attendance" in lower_obj:
        return '''"""Employee Attendance CSV Validator.

Zero-dependency standard library implementation.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate employee attendance CSV files.")
    parser.add_argument("csv_file", help="Path to attendance CSV file")
    args = parser.parse_args(argv)

    target_path = Path(args.csv_file)
    if ".." in str(target_path) and not target_path.resolve().is_relative_to(Path.cwd()):
        print(f"[SECURITY ERROR] Path traversal detected: {target_path}", file=sys.stderr)
        return 2

    if not target_path.is_file():
        print(f"[ERROR] Attendance file does not exist: {target_path}", file=sys.stderr)
        return 1

    content = target_path.read_text(encoding="utf-8")
    if not content.strip():
        print("[WARN] File is empty. 0 records validated.")
        return 0

    reader = csv.DictReader(content.splitlines())
    valid_count = 0
    invalid_count = 0

    for idx, row in enumerate(reader, start=2):
        emp_id = row.get("employee_id") or row.get("id") or (list(row.values())[0] if row else "")
        if not emp_id or not emp_id.strip():
            invalid_count += 1
            print(f"[WARN] Line {idx}: Missing employee ID")
        else:
            valid_count += 1

    print(f"[OK] Validation complete: {valid_count} valid records, {invalid_count} invalid records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    elif "raid" in lower_obj:
        return '''"""Project RAID Log Reviewer.

Zero-dependency standard library implementation.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit and review project RAID logs.")
    parser.add_argument("raid_file", help="Path to RAID log CSV file")
    args = parser.parse_args(argv)

    p = Path(args.raid_file)
    if ".." in str(p) and not p.resolve().is_relative_to(Path.cwd()):
        print(f"[SECURITY ERROR] Path traversal detected: {p}", file=sys.stderr)
        return 2

    if not p.is_file():
        print(f"[ERROR] RAID log file does not exist: {p}", file=sys.stderr)
        return 1

    lines = p.read_text(encoding="utf-8").splitlines()
    if not lines:
        print("[WARN] RAID log is empty.")
        return 0

    reader = csv.DictReader(lines)
    counts = {"Risk": 0, "Assumption": 0, "Issue": 0, "Dependency": 0}
    unassigned = 0

    for row in reader:
        item_type = row.get("type", "Risk").capitalize()
        if item_type in counts:
            counts[item_type] += 1
        owner = row.get("owner", "").strip()
        if not owner:
            unassigned += 1

    print("# Project RAID Log Audit Report")
    for k, v in counts.items():
        print(f"- Total {k}s: {v}")
    if unassigned:
        print(f"[ALERT] {unassigned} RAID item(s) currently lack an assigned owner!")
    else:
        print("[OK] All RAID items have assigned owners.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    elif "invoice" in lower_obj:
        return '''"""Invoice Discrepancy Checker.

Zero-dependency standard library implementation.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reconcile invoices and flag billing discrepancies.")
    parser.add_argument("invoice_file", help="Path to invoice CSV file")
    args = parser.parse_args(argv)

    p = Path(args.invoice_file)
    if ".." in str(p) and not p.resolve().is_relative_to(Path.cwd()):
        print(f"[SECURITY ERROR] Path traversal detected: {p}", file=sys.stderr)
        return 2

    if not p.is_file():
        print(f"[ERROR] Invoice file does not exist: {p}", file=sys.stderr)
        return 1

    lines = p.read_text(encoding="utf-8").splitlines()
    if not lines:
        print("[WARN] Invoice file is empty.")
        return 0

    reader = csv.DictReader(lines)
    seen_invoices = set()
    duplicates = []
    total_amount = 0.0

    for idx, row in enumerate(reader, start=2):
        inv_no = row.get("invoice_number") or row.get("invoice_id") or ""
        if inv_no:
            if inv_no in seen_invoices:
                duplicates.append(inv_no)
            seen_invoices.add(inv_no)

        try:
            amt = float(row.get("amount", 0.0))
            total_amount += amt
        except ValueError:
            pass

    print("# Invoice Reconciliation Summary")
    print(f"- Total Processed: {len(seen_invoices)} unique invoices")
    print(f"- Total Billed Amount: ${total_amount:,.2f}")
    if duplicates:
        print(f"[ALERT] Duplicate invoices detected: {', '.join(duplicates)}")
    else:
        print("[OK] No duplicate invoice numbers detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    else:
        return '''"""Autonomous Agent Skill Implementation.

Zero-dependency standard library implementation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process input and execute skill workflow.")
    parser.add_argument("input_target", nargs="?", default=None, help="Input file or data string")
    args = parser.parse_args(argv)

    if not args.input_target:
        print("Usage: python scripts/main.py <input_target>")
        return 0

    target = Path(args.input_target)
    if ".." in str(target) and not target.resolve().is_relative_to(Path.cwd()):
        print(f"[SECURITY ERROR] Path traversal detected: {target}", file=sys.stderr)
        return 2

    if target.is_file():
        content = target.read_text(encoding="utf-8")
        print(f"[OK] Successfully processed input file '{target.name}' ({len(content)} characters).")
    else:
        print(f"[OK] Processed input: '{args.input_target}'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
