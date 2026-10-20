#!/usr/bin/env python3
"""Dependency Manifest Reviewer (Showcase Demo 04).

Domain: Cybersecurity and Software Engineering.
Audits package dependency manifests (requirements.txt, package.json, pyproject.toml)
for unpinned versions, conflicting requirements, unencrypted HTTP links, and mutable
git references without making unverified CVE vulnerability claims.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION_OP_PATTERN = re.compile(r"([=><~^!]+)")


def audit_requirements_txt(lines: List[str], file_name: str) -> Dict[str, Any]:
    """Audit Python requirements.txt manifest line-by-line."""
    findings: List[Dict[str, Any]] = []
    packages_map: Dict[str, List[Tuple[int, str]]] = {}
    total_deps = 0

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Ignore pip flags like -r other.txt, -i https://..., --extra-index-url
        if line.startswith("-") and not line.startswith(("-e", "--editable")):
            continue

        # Insecure HTTP protocol check (DEP-01)
        if "http://" in line:
            findings.append({
                "line": idx,
                "dependency": line,
                "rule_id": "DEP-01",
                "severity": "CRITICAL",
                "category": "Insecure Protocol",
                "description": "Unencrypted HTTP repository or package URL detected (risk of MITM attack).",
                "recommendation": "Enforce HTTPS with certificate validation (https://) for all package indexes and wheels.",
            })

        # Mutable VCS reference check (DEP-02)
        if ("git+" in line or "git://" in line or "svn+" in line or "hg+" in line) and "@" not in line:
            findings.append({
                "line": idx,
                "dependency": line,
                "rule_id": "DEP-02",
                "severity": "HIGH",
                "category": "Mutable VCS Reference",
                "description": "VCS dependency declared without commit SHA pin (risk of non-reproducible builds).",
                "recommendation": "Pin VCS dependencies to an immutable 40-character commit hash (e.g. git+https://...@commit-sha).",
            })

        # Extract package name and version specification
        # Handle lines with environment markers or inline comments
        clean_spec = line.split(";")[0].split("#")[0].strip()
        if clean_spec.startswith("-e "):
            clean_spec = clean_spec[3:].strip()

        is_url_or_vcs = "@" in clean_spec or "git+" in clean_spec or "http" in clean_spec

        if not is_url_or_vcs:
            parts = VERSION_OP_PATTERN.split(clean_spec)
            pkg_name = parts[0].strip().lower()

            if pkg_name:
                total_deps += 1
                packages_map.setdefault(pkg_name, []).append((idx, clean_spec))

                # Unpinned dependency check (DEP-05)
                if len(parts) == 1:
                    findings.append({
                        "line": idx,
                        "dependency": pkg_name,
                        "rule_id": "DEP-05",
                        "severity": "MEDIUM",
                        "category": "Unpinned Dependency",
                        "description": f"Package '{pkg_name}' has no version constraint; accepts arbitrary releases.",
                        "recommendation": f"Specify an explicit pinned version constraint (e.g. {pkg_name}==X.Y.Z).",
                    })
                elif len(parts) > 2:
                    op = parts[1].strip()
                    ver = parts[2].strip()
                    # Wildcard or unbounded check (DEP-06)
                    if ver in ("*", "latest") or (op in (">=", ">") and "<" not in clean_spec):
                        findings.append({
                            "line": idx,
                            "dependency": pkg_name,
                            "rule_id": "DEP-06",
                            "severity": "LOW",
                            "category": "Unbounded / Wildcard Version",
                            "description": f"Package '{pkg_name}' uses wildcard or unbounded constraint '{op}{ver}'.",
                            "recommendation": "Apply an upper-bound constraint or exact pin to prevent unexpected breaking changes.",
                        })

    # Conflicting or duplicate declarations check (DEP-03 / DEP-04)
    for pkg, occurrences in packages_map.items():
        if len(occurrences) > 1:
            specs = [spec for _, spec in occurrences]
            lines_str = ", ".join(f"L{ln}" for ln, _ in occurrences)
            if len(set(specs)) > 1:
                # Different constraints -> Conflict
                findings.append({
                    "line": occurrences[1][0],
                    "dependency": pkg,
                    "rule_id": "DEP-03",
                    "severity": "HIGH",
                    "category": "Conflicting Requirements",
                    "description": f"Conflicting specifications for package '{pkg}' found on {lines_str}: {specs}",
                    "recommendation": "Consolidate to a single consistent version specification across the project.",
                })
            else:
                # Identical constraints -> Duplicate
                findings.append({
                    "line": occurrences[1][0],
                    "dependency": pkg,
                    "rule_id": "DEP-04",
                    "severity": "MEDIUM",
                    "category": "Duplicate Requirement",
                    "description": f"Duplicate specification for package '{pkg}' declared on {lines_str}.",
                    "recommendation": "Remove redundant dependency declaration.",
                })

    return {
        "manifest_file": file_name,
        "manifest_type": "requirements.txt",
        "total_dependencies_declared": total_deps,
        "unique_packages_count": len(packages_map),
        "total_findings": len(findings),
        "is_clean": len(findings) == 0,
        "findings": sorted(findings, key=lambda f: f["line"]),
    }


def audit_package_json(content: str, file_name: str) -> Dict[str, Any]:
    """Audit npm package.json dependencies."""
    findings: List[Dict[str, Any]] = []
    try:
        data = json.loads(content)
    except Exception as exc:
        return {
            "manifest_file": file_name,
            "manifest_type": "package.json",
            "total_dependencies_declared": 0,
            "unique_packages_count": 0,
            "total_findings": 1,
            "is_clean": False,
            "findings": [{
                "line": 1,
                "dependency": file_name,
                "rule_id": "DEP-PARSE-ERR",
                "severity": "CRITICAL",
                "category": "Syntax Error",
                "description": f"Failed to parse package.json: {exc}",
                "recommendation": "Ensure package.json is valid JSON.",
            }],
        }

    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_pkgs: Dict[str, List[str]] = {}

    for name, ver in deps.items():
        all_pkgs.setdefault(name, []).append(f"dependencies: {ver}")
    for name, ver in dev_deps.items():
        all_pkgs.setdefault(name, []).append(f"devDependencies: {ver}")

    for name, versions in all_pkgs.items():
        if len(versions) > 1:
            findings.append({
                "line": 1,
                "dependency": name,
                "rule_id": "DEP-03",
                "severity": "HIGH",
                "category": "Conflicting Requirements",
                "description": f"Package '{name}' declared in both dependencies and devDependencies: {versions}",
                "recommendation": "Define package in only one dependency section.",
            })

        for v_str in versions:
            ver = v_str.split(": ", 1)[1].strip()
            if ver.startswith("http://"):
                findings.append({
                    "line": 1,
                    "dependency": name,
                    "rule_id": "DEP-01",
                    "severity": "CRITICAL",
                    "category": "Insecure Protocol",
                    "description": f"Dependency '{name}' uses unencrypted HTTP URL '{ver}'.",
                    "recommendation": "Use HTTPS or official npm registry.",
                })
            elif ver in ("*", "latest"):
                findings.append({
                    "line": 1,
                    "dependency": name,
                    "rule_id": "DEP-06",
                    "severity": "LOW",
                    "category": "Unbounded / Wildcard Version",
                    "description": f"Dependency '{name}' uses wildcard version '{ver}'.",
                    "recommendation": "Pin to a specific semantic version.",
                })

    return {
        "manifest_file": file_name,
        "manifest_type": "package.json",
        "total_dependencies_declared": len(deps) + len(dev_deps),
        "unique_packages_count": len(all_pkgs),
        "total_findings": len(findings),
        "is_clean": len(findings) == 0,
        "findings": findings,
    }


def format_markdown_report(data: Dict[str, Any]) -> str:
    """Format dependency review report in GitHub-flavored markdown."""
    status_str = "**CLEAN (All dependencies securely configured)**" if data["is_clean"] else "**ATTENTION REQUIRED (Configuration Risks Found)**"

    out: List[str] = [
        f"# Dependency Manifest Review: `{data['manifest_file']}`",
        "",
        "## Executive Summary",
        "",
        f"- **Manifest File Type:** `{data['manifest_type']}`",
        f"- **Audit Status:** {status_str}",
        f"- **Total Dependencies Evaluated:** {data['total_dependencies_declared']}",
        f"- **Unique Package Declarations:** {data['unique_packages_count']}",
        f"- **Total Configuration Findings:** {data['total_findings']}",
        "",
    ]

    if data["findings"]:
        out.append("## Detailed Findings & Remediation Register")
        out.append("")
        out.append("| Line | Rule ID | Severity | Category | Dependency | Issue Description & Recommendation |")
        out.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for f in data["findings"]:
            out.append(
                f"| L{f['line']} | `{f['rule_id']}` | **{f['severity']}** | {f['category']} | "
                f"`{f['dependency']}` | {f['description']} *Action: {f['recommendation']}* |"
            )
        out.append("")

    out.append("## Cybersecurity Advisory & Boundary Disclaimer")
    out.append("")
    out.append("> [!IMPORTANT]")
    out.append("> **Scope Boundary Notice**: This analysis is a deterministic static configuration review")
    out.append("> targeting version pinning, dependency conflicts, and protocol safety. It does NOT claim")
    out.append("> that any package contains active Common Vulnerabilities and Exposures (CVEs) without")
    out.append("> verification against an authenticated external vulnerability database (e.g. OSV, NVD, GitHub Advisory).")
    out.append("")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit dependency manifest files for configuration and pinning risks.")
    parser.add_argument("manifest_file", help="Path to requirements.txt or package.json")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--output", help="Write report to specified output path")
    args = parser.parse_args(argv)

    path = Path(args.manifest_file)
    if not path.is_file():
        print(f"[ERROR] Manifest file not found: {path}", file=sys.stderr)
        return 1

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"[ERROR] Could not read file '{path}': {exc}", file=sys.stderr)
        return 1

    if path.name == "package.json":
        data = audit_package_json(content, path.name)
    else:
        data = audit_requirements_txt(content.splitlines(), path.name)

    if args.json:
        output_text = json.dumps(data, indent=2)
    else:
        output_text = format_markdown_report(data)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output_text, encoding="utf-8")
        print(f"[OK] Dependency review report written to {args.output}")
    else:
        print(output_text)

    return 0 if data["is_clean"] else 2


if __name__ == "__main__":
    sys.exit(main())
