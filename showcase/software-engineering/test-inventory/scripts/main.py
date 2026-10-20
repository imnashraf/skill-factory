#!/usr/bin/env python3
"""Test Inventory Analyzer (Showcase Demo 05).

Domain: Software Engineering and Quality Assurance.
Scans codebases using Python's built-in AST parser to catalog test suites, functions,
and assertions, group tests by source module, detect duplicate test cases, and identify
untested source modules without claiming uninstrumented runtime code coverage.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class TestASTVisitor(ast.NodeVisitor):
    """AST visitor extracting test functions, assertions, and skip decorators."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.test_cases: List[Dict[str, Any]] = []
        self.assertions_count = 0
        self.skipped_count = 0
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        prev_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name.startswith("test_") or node.name.endswith("_test"):
            is_skipped = False
            for dec in node.decorator_list:
                dec_repr = ""
                if hasattr(ast, "unparse"):
                    dec_repr = ast.unparse(dec).lower()
                elif isinstance(dec, ast.Name):
                    dec_repr = dec.id.lower()
                elif isinstance(dec, ast.Attribute):
                    dec_repr = dec.attr.lower()

                if "skip" in dec_repr:
                    is_skipped = True
                    self.skipped_count += 1
                    break

            self.test_cases.append({
                "name": node.name,
                "class_name": self.current_class,
                "line": node.lineno,
                "is_skipped": is_skipped,
            })

        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.assertions_count += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Detect unittest self.assert* calls
        if isinstance(node.func, ast.Attribute) and node.func.attr.startswith("assert"):
            self.assertions_count += 1
        self.generic_visit(node)


def infer_module_name(test_filename: str) -> str:
    """Infer source module name from test file name (e.g. test_auth.py -> auth)."""
    base = test_filename.replace(".py", "")
    if base.startswith("test_"):
        return base[5:]
    if base.endswith("_test"):
        return base[:-5]
    return base


def analyze_test_inventory(
    root_dir: Path,
    src_folder: str = "src",
    tests_folder: str = "tests",
) -> Dict[str, Any]:
    """Catalog all test files, test cases, assertions, duplicate tests, and untested modules."""
    project_root = Path(root_dir).resolve()
    tests_path = project_root / tests_folder if (project_root / tests_folder).is_dir() else project_root
    src_path = project_root / src_folder if (project_root / src_folder).is_dir() else project_root

    # 1. Discover all test files
    test_files_map: List[Dict[str, Any]] = []
    all_test_names: Dict[str, List[Dict[str, Any]]] = {}
    tested_modules: Set[str] = set()

    total_tests = 0
    total_assertions = 0
    total_skipped = 0

    candidate_test_files = sorted(tests_path.rglob("test_*.py")) + sorted(tests_path.rglob("*_test.py"))
    seen_paths: Set[Path] = set()

    for tf in candidate_test_files:
        if tf in seen_paths or "__pycache__" in tf.parts or ".git" in tf.parts:
            continue
        seen_paths.add(tf)

        try:
            content = tf.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(content, filename=str(tf))
            visitor = TestASTVisitor(str(tf))
            visitor.visit(tree)

            count = len(visitor.test_cases)
            total_tests += count
            total_assertions += visitor.assertions_count
            total_skipped += visitor.skipped_count

            rel_file = str(tf.relative_to(project_root)) if tf.is_relative_to(project_root) else tf.name
            mod_name = infer_module_name(tf.name)
            tested_modules.add(mod_name)

            for tc in visitor.test_cases:
                tc_info = {
                    "file": rel_file,
                    "line": tc["line"],
                    "class": tc["class_name"],
                    "is_skipped": tc["is_skipped"],
                }
                all_test_names.setdefault(tc["name"], []).append(tc_info)

            test_files_map.append({
                "file": rel_file,
                "inferred_module": mod_name,
                "test_count": count,
                "assertions_count": visitor.assertions_count,
                "skipped_count": visitor.skipped_count,
                "tests": visitor.test_cases,
            })
        except Exception:
            continue

    # 2. Detect duplicate test names across files or classes
    duplicate_tests: List[Dict[str, Any]] = []
    for t_name, occurrences in all_test_names.items():
        if len(occurrences) > 1:
            duplicate_tests.append({
                "test_name": t_name,
                "occurrences_count": len(occurrences),
                "locations": occurrences,
            })

    # 3. Discover source modules and identify untested modules
    source_modules: List[Dict[str, Any]] = []
    untested_modules: List[Dict[str, Any]] = []

    if src_path.is_dir() and src_path != tests_path:
        for py_file in sorted(src_path.rglob("*.py")):
            if py_file.name == "__init__.py" or "__pycache__" in py_file.parts or ".git" in py_file.parts:
                continue
            mod_name = py_file.stem
            rel_file = str(py_file.relative_to(project_root))

            has_test = (mod_name in tested_modules) or any(
                tf["inferred_module"] == mod_name for tf in test_files_map
            )

            mod_info = {
                "module_name": mod_name,
                "file": rel_file,
                "has_test_file": has_test,
            }
            source_modules.append(mod_info)

            if not has_test:
                untested_modules.append(mod_info)

    return {
        "project_root": str(project_root),
        "test_files_count": len(test_files_map),
        "total_test_cases": total_tests,
        "total_assertions": total_assertions,
        "total_skipped_tests": total_skipped,
        "source_modules_count": len(source_modules),
        "tested_modules_count": len(source_modules) - len(untested_modules),
        "untested_modules_count": len(untested_modules),
        "duplicate_tests_count": len(duplicate_tests),
        "test_files": test_files_map,
        "duplicate_tests": duplicate_tests,
        "untested_modules": untested_modules,
    }


def format_markdown_report(data: Dict[str, Any]) -> str:
    """Format inventory and coverage gap metrics into GitHub-flavored markdown."""
    out: List[str] = [
        "# Test Inventory & Suite Audit Report",
        "",
        "## Executive Test Metrics",
        "",
        f"- **Test Suites / Files Discovered:** {data['test_files_count']}",
        f"- **Total Test Functions (`test_*`):** {data['total_test_cases']}",
        f"- **Total Assertions Detected:** {data['total_assertions']}",
        f"- **Marked Skipped Tests:** {data['total_skipped_tests']}",
        f"- **Source Modules Evaluated:** {data['source_modules_count']}",
        f"- **Modules with Dedicated Test Files:** {data['tested_modules_count']} / {data['source_modules_count']}",
        f"- **Untested Modules Flagged:** {data['untested_modules_count']}",
        f"- **Duplicate Test Names Flagged:** {data['duplicate_tests_count']}",
        "",
        "## Test Suite Catalog",
        "",
        "| Test File | Target Module | Test Count | Assertions | Skipped |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for tf in data["test_files"]:
        out.append(
            f"| `{tf['file']}` | `{tf['inferred_module']}` | {tf['test_count']} | "
            f"{tf['assertions_count']} | {tf['skipped_count']} |"
        )
    out.append("")

    if data["untested_modules"]:
        out.append("## Untested Source Modules (Coverage Gap Risk)")
        out.append("")
        out.append("| Module Name | Source File | Status |")
        out.append("| :--- | :--- | :--- |")
        for um in data["untested_modules"]:
            out.append(f"| `{um['module_name']}` | `{um['file']}` | **NO TEST FILE FOUND** |")
        out.append("")

    if data["duplicate_tests"]:
        out.append("## Duplicate Test Function Names")
        out.append("")
        out.append("| Test Name | Occurrences | Locations |")
        out.append("| :--- | :--- | :--- |")
        for dt in data["duplicate_tests"]:
            loc_str = "; ".join(f"`{loc['file']}:L{loc['line']}`" for loc in dt["locations"])
            out.append(f"| `{dt['test_name']}` | {dt['occurrences_count']} | {loc_str} |")
        out.append("")

    out.append("## QA Scope & Instrumentation Disclaimer")
    out.append("")
    out.append("> [!IMPORTANT]")
    out.append("> **Scope Boundary Notice**: This report represents a static structural test inventory")
    out.append("> and module mapping audit. It does NOT claim or measure dynamic line/branch code coverage,")
    out.append("> which requires runtime instrumentation tools (e.g. `coverage.py`, `pytest-cov`, `c8`).")
    out.append("")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze codebase test inventory and identify untested modules.")
    parser.add_argument("path", default=".", nargs="?", help="Path to project root directory (default: .)")
    parser.add_argument("--src-dir", default="src", help="Source folder relative to path (default: src)")
    parser.add_argument("--tests-dir", default="tests", help="Tests folder relative to path (default: tests)")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.is_dir():
        print(f"[ERROR] Path '{root}' is not a directory", file=sys.stderr)
        return 1

    data = analyze_test_inventory(root, src_folder=args.src_dir, tests_folder=args.tests_dir)

    if args.json:
        output_text = json.dumps(data, indent=2)
    else:
        output_text = format_markdown_report(data)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output_text, encoding="utf-8")
        print(f"[OK] Test inventory report written to {args.output}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
