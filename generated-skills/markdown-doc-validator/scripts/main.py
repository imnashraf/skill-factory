#!/usr/bin/env python3
"""Markdown Documentation Validator (markdown-doc-validator).

Validates Markdown documentation repositories for broken relative links,
missing code block language tags, invalid table separators, and empty headings.
Pure Python standard library implementation with zero external dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FENCE_REGEX = re.compile(r"^(`{3,}|~{3,})(.*)$")
HEADING_REGEX = re.compile(r"^(#{1,6})\s*(.*)$")
TABLE_SEP_REGEX = re.compile(r"^\|(?:[-:]+\|)+$")


@dataclass
class MarkdownIssue:
    file_path: str
    line_number: int
    rule_id: str
    severity: str
    message: str
    suggestion: str

    def to_dict(self) -> dict:
        return asdict(self)


def validate_file(file_path: Path, repo_root: Path) -> List[MarkdownIssue]:
    issues: List[MarkdownIssue] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as err:
        issues.append(
            MarkdownIssue(
                file_path=str(file_path.relative_to(repo_root)),
                line_number=0,
                rule_id="MD-READ-ERR",
                severity="ERROR",
                message=f"Cannot read file: {err}",
                suggestion="Check file permissions and UTF-8 encoding.",
            )
        )
        return issues

    lines = content.splitlines()
    in_code_block = False
    fence_char = ""
    fence_len = 0
    h1_count = 0
    rel_path = str(file_path.relative_to(repo_root))

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check code fences
        fence_match = FENCE_REGEX.match(stripped)
        if fence_match:
            marker, lang = fence_match.groups()
            if not in_code_block:
                in_code_block = True
                fence_char = marker[0]
                fence_len = len(marker)
                lang = lang.strip()
                if not lang:
                    issues.append(
                        MarkdownIssue(
                            file_path=rel_path,
                            line_number=idx,
                            rule_id="MD-NO-LANG",
                            severity="WARN",
                            message="Code block is missing language identifier.",
                            suggestion="Add language tag (e.g. ```bash, ```python, ```json, ```text).",
                        )
                    )
            else:
                if marker.startswith(fence_char) and len(marker) >= fence_len:
                    in_code_block = False
            continue

        if in_code_block:
            continue

        # Check headings
        head_match = HEADING_REGEX.match(line)
        if head_match:
            hashes, text = head_match.groups()
            title = text.strip()
            if not title:
                issues.append(
                    MarkdownIssue(
                        file_path=rel_path,
                        line_number=idx,
                        rule_id="MD-EMPTY-HEAD",
                        severity="ERROR",
                        message="Heading contains no text.",
                        suggestion="Provide a descriptive heading title or remove the heading line.",
                    )
                )
            if len(hashes) == 1:
                h1_count += 1
                if h1_count > 1:
                    issues.append(
                        MarkdownIssue(
                            file_path=rel_path,
                            line_number=idx,
                            rule_id="MD-MULTI-H1",
                            severity="WARN",
                            message=f"Multiple top-level H1 headings detected in document ('{title}').",
                            suggestion="Use H2 (##) or lower for subheadings; reserve H1 (#) for document title.",
                        )
                    )

        # Check table separators without spacing (MD060)
        if stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped and TABLE_SEP_REGEX.match(stripped):
                # Check for unspaced pipes: |---|---| vs | --- | --- |
                if "|---" in stripped or "---||" in stripped or "---|" in stripped:
                    issues.append(
                        MarkdownIssue(
                            file_path=rel_path,
                            line_number=idx,
                            rule_id="MD-TABLE-SEP",
                            severity="WARN",
                            message="Table separator row lacks consistent whitespace padding around pipes.",
                            suggestion="Use padded pipes format: '| --- | --- |'.",
                        )
                    )

        # Check relative links
        for m in LINK_REGEX.finditer(line):
            link_text, link_target = m.groups()
            link_target = link_target.strip()
            # Skip external links, mailto, and anchors
            if link_target.startswith(("http://", "https://", "mailto:", "#")):
                continue

            # Strip query strings or fragment anchors
            target_path_str = link_target.split("#")[0].split("?")[0]
            if not target_path_str:
                continue

            target_file = (file_path.parent / target_path_str).resolve()
            if not target_file.exists():
                issues.append(
                    MarkdownIssue(
                        file_path=rel_path,
                        line_number=idx,
                        rule_id="MD-BROKEN-LINK",
                        severity="ERROR",
                        message=f"Broken relative link: '{link_target}' points to nonexistent path.",
                        suggestion=f"Verify target path '{target_path_str}' exists relative to '{file_path.parent}'.",
                    )
                )

    return issues


def validate_repository(repo_path: Path) -> List[MarkdownIssue]:
    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    issues: List[MarkdownIssue] = []
    if repo_path.is_file():
        files = [repo_path]
        root = repo_path.parent
    else:
        root = repo_path
        files = [
            p
            for p in sorted(repo_path.rglob("*.md"))
            if ".git" not in p.parts and "node_modules" not in p.parts
        ]

    for f in files:
        issues.extend(validate_file(f, root))

    return issues


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="markdown-doc-validator",
        description="Validate Markdown files for broken links, syntax issues, and table style.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Target file or directory to validate (default: .)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--fail-on-errors", action="store_true", help="Exit code 1 if ERROR-level issues exist")

    args = parser.parse_args(argv)
    target = Path(args.path)

    try:
        issues = validate_repository(target)
    except Exception as err:
        print(f"[ERROR] Validation failed: {err}", file=sys.stderr)
        return 2

    if args.json:
        data = {
            "status": "success",
            "target": str(target.resolve()),
            "total_issues": len(issues),
            "errors": sum(1 for i in issues if i.severity == "ERROR"),
            "warnings": sum(1 for i in issues if i.severity == "WARN"),
            "issues": [i.to_dict() for i in issues],
        }
        print(json.dumps(data, indent=2))
    else:
        if not issues:
            print(f"[OK] Markdown documentation in '{target}' is 100% valid. 0 issues detected.")
        else:
            errors = [i for i in issues if i.severity == "ERROR"]
            warns = [i for i in issues if i.severity == "WARN"]
            print(f"Markdown Documentation Audit: {len(errors)} error(s), {len(warns)} warning(s)")
            print("=" * 60)
            for idx, issue in enumerate(issues, 1):
                print(f"[{issue.severity}] #{idx} ({issue.rule_id}) {issue.file_path}:{issue.line_number}")
                print(f"  Problem: {issue.message}")
                print(f"  Fix:     {issue.suggestion}")
                print("")

    if args.fail_on_errors and any(i.severity == "ERROR" for i in issues):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
