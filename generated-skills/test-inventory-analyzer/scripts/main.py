#!/usr/bin/env python3
"""Test Inventory Analyzer (Developer & Security Pack).

Scans software source trees and test directories to catalog unit, integration,
and e2e tests, counting test cases, assertions, and skipped suites.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestFileVisitor(ast.NodeVisitor):
    """AST visitor to catalog test functions and classes."""

    def __init__(self) -> None:
        self.test_cases: List[str] = []
        self.assertions_count: int = 0
        self.skipped_count: int = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name.startswith("test_"):
            self.test_cases.append(node.name)
            # Check decorators for skip
            for dec in node.decorator_list:
                dec_repr = ast.unparse(dec) if hasattr(ast, "unparse") else ""
                if "skip" in dec_repr.lower():
                    self.skipped_count += 1

        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.assertions_count += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Check for self.assert* in unittest
        if isinstance(node.func, ast.Attribute) and node.func.attr.startswith("assert"):
            self.assertions_count += 1
        self.generic_visit(node)


def analyze_test_directory(target_path: Path) -> Dict[str, Any]:
    """Inspect directory and catalog test files."""
    root = Path(target_path).resolve()
    test_files: List[Dict[str, Any]] = []

    total_tests = 0
    total_assertions = 0
    total_skipped = 0

    if root.is_file() and root.name.endswith(".py"):
        candidate_paths = [root]
    elif root.is_dir():
        candidate_paths = sorted(root.rglob("test_*.py")) + sorted(root.rglob("*_test.py"))
    else:
        candidate_paths = []

    seen = set()
    for p in candidate_paths:
        if p in seen or ".git" in p.parts or "__pycache__" in p.parts:
            continue
        seen.add(p)

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(content, filename=str(p))
            visitor = TestFileVisitor()
            visitor.visit(tree)

            count = len(visitor.test_cases)
            total_tests += count
            total_assertions += visitor.assertions_count
            total_skipped += visitor.skipped_count

            rel_path = str(p.relative_to(root)) if root.is_dir() else p.name
            test_files.append({
                "file": rel_path,
                "test_count": count,
                "assertions_count": visitor.assertions_count,
                "skipped_count": visitor.skipped_count,
                "tests": visitor.test_cases,
            })
        except Exception:
            continue

    return {
        "root_path": str(root),
        "test_files_count": len(test_files),
        "total_test_functions": total_tests,
        "total_assertions": total_assertions,
        "total_skipped_tests": total_skipped,
        "files": test_files,
    }


def format_markdown_report(data: Dict[str, Any]) -> str:
    """Format inventory data into clean GitHub-flavored markdown."""
    out = ["# Test Inventory & Suite Audit Report", ""]
    out.append("## Executive Test Metrics")
    out.append(f"- **Test Files Discovered:** {data['test_files_count']}")
    out.append(f"- **Total Test Functions (`test_*`):** {data['total_test_functions']}")
    out.append(f"- **Total Assertions Detected:** {data['total_assertions']}")
    out.append(f"- **Marked Skipped Tests:** {data['total_skipped_tests']}")
    out.append("")
    out.append("## Test File Breakdown")
    out.append("| File | Tests | Assertions | Skipped |")
    out.append("| :--- | :--- | :--- | :--- |")

    for f in data["files"]:
        out.append(f"| `{f['file']}` | {f['test_count']} | {f['assertions_count']} | {f['skipped_count']} |")
    out.append("")

    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze and catalog test inventory in a Python codebase.")
    parser.add_argument("path", default=".", nargs="?", help="Path to test directory or file (default: .)")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        print(f"[ERROR] Path not found: {path}", file=sys.stderr)
        return 1

    data = analyze_test_directory(path)

    if args.json:
        res = json.dumps(data, indent=2)
    else:
        res = format_markdown_report(data)

    if args.output:
        Path(args.output).write_text(res, encoding="utf-8")
        print(f"[OK] Test inventory report written to {args.output}")
    else:
        print(res)

    return 0


if __name__ == "__main__":
    sys.exit(main())
