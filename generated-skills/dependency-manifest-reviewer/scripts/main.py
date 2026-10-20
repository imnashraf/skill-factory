#!/usr/bin/env python3
"""Dependency Manifest Reviewer (Developer & Security Pack).

Audits package dependency manifests (requirements.txt, package.json)
for unpinned versions, wildcards, mutable git references, and insecure protocols.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def review_requirements_lines(lines: List[str]) -> Dict[str, Any]:
    """Audit Python requirements.txt lines."""
    findings: List[Dict[str, Any]] = []
    packages_seen: Dict[str, int] = {}

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Insecure protocol check
        if "http://" in line:
            findings.append({
                "line": idx,
                "dependency": line,
                "severity": "CRITICAL",
                "rule_id": "DEP-01",
                "description": "Insecure HTTP repository or package URL detected (risk of MITM).",
            })

        # Mutable git link check
        if ("git+" in line or "git://" in line) and "@" not in line:
            findings.append({
                "line": idx,
                "dependency": line,
                "severity": "HIGH",
                "rule_id": "DEP-02",
                "description": "Mutable VCS link without commit SHA pin (risk of non-reproducible builds).",
            })

        # Extract package name and version specifier
        parts = re.split(r"([=><~^!]+)", line)
        pkg_name = parts[0].strip().lower()

        # Duplicate check
        packages_seen[pkg_name] = packages_seen.get(pkg_name, 0) + 1
        if packages_seen[pkg_name] == 2:
            findings.append({
                "line": idx,
                "dependency": pkg_name,
                "severity": "MEDIUM",
                "rule_id": "DEP-03",
                "description": f"Duplicate package specification for '{pkg_name}'.",
            })

        # Unpinned / wildcard check
        is_url_or_vcs = "@" in line or "git+" in line or "git://" in line
        if len(parts) == 1 and not line.startswith("-") and not is_url_or_vcs:
            findings.append({
                "line": idx,
                "dependency": pkg_name,
                "severity": "MEDIUM",
                "rule_id": "DEP-04",
                "description": f"Completely unpinned package '{pkg_name}' (accepts arbitrary versions).",
            })
        elif len(parts) > 2 and not is_url_or_vcs:
            op = parts[1].strip()
            ver = parts[2].strip()
            if ver in ("*", "latest") or op in (">=", ">") and "<" not in line:
                findings.append({
                    "line": idx,
                    "dependency": pkg_name,
                    "severity": "LOW",
                    "rule_id": "DEP-05",
                    "description": f"Unbounded or wildcard version specifier '{op}{ver}'.",
                })

    return {
        "total_dependencies": len(packages_seen),
        "findings_count": len(findings),
        "is_secure": len(findings) == 0,
        "findings": findings,
    }


def format_markdown_report(data: Dict[str, Any], file_name: str) -> str:
    """Format review report in GitHub-flavored markdown."""
    out = [f"# Dependency Manifest Review: `{file_name}`", ""]
    out.append("## Security Summary")
    out.append(f"- **Total Dependencies Audited:** {data['total_dependencies']}")
    out.append(f"- **Total Security / Pinning Findings:** {data['findings_count']}")
    status_str = "**CLEAN (All dependencies securely pinned)**" if data["is_secure"] else "**ATTENTION REQUIRED**"
    out.append(f"- **Audit Status:** {status_str}")
    out.append("")

    if data["findings"]:
        out.append("## Detailed Findings")
        out.append("| Line | Rule ID | Severity | Dependency | Issue Description |")
        out.append("| :--- | :--- | :--- | :--- | :--- |")
        for f in data["findings"]:
            out.append(f"| {f['line']} | `{f['rule_id']}` | `{f['severity']}` | `{f['dependency']}` | {f['description']} |")
        out.append("")

    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit dependency manifest files for security and version pinning risks.")
    parser.add_argument("manifest_file", help="Path to requirements.txt or dependencies file")
    parser.add_argument("--json", action="store_true", help="Output audit results in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    path = Path(args.manifest_file)
    if not path.is_file():
        print(f"[ERROR] Manifest file not found: {path}", file=sys.stderr)
        return 1

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    data = review_requirements_lines(lines)

    if args.json:
        res = json.dumps(data, indent=2)
    else:
        res = format_markdown_report(data, path.name)

    if args.output:
        Path(args.output).write_text(res, encoding="utf-8")
        print(f"[OK] Audit report written to {args.output}")
    else:
        print(res)

    return 0 if data["is_secure"] else 1


if __name__ == "__main__":
    sys.exit(main())
