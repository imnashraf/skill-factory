#!/usr/bin/env python3
"""Security & Configuration Scanner (security-config-scanner).

Scans directories for exposed credentials, secret keys, and insecure configuration settings.
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
from typing import Dict, List, Optional

SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

PATTERNS = [
    # Exposed Credentials
    (
        "SEC-01",
        "AWS Access Key ID",
        "CRITICAL",
        re.compile(r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])"),
        "Revoke key immediately and rotate IAM credentials.",
    ),
    (
        "SEC-02",
        "GitHub Personal Access Token",
        "CRITICAL",
        re.compile(r"ghp_[0-9a-zA-Z]{36}"),
        "Revoke personal access token in GitHub Settings > Developer settings.",
    ),
    (
        "SEC-03",
        "OpenAI Secret API Key",
        "CRITICAL",
        re.compile(r"sk-[a-zA-Z0-9]{32,48}"),
        "Revoke key in OpenAI platform dashboard and use environment variables.",
    ),
    (
        "SEC-04",
        "Private Key Block",
        "CRITICAL",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        "Remove private key from source control and store in secure secret manager.",
    ),
    (
        "SEC-05",
        "Hardcoded Database Password",
        "HIGH",
        re.compile(r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"]([^'\"]{6,})['\"]"),
        "Replace hardcoded credentials with environment variable lookups.",
    ),
    # Insecure Configurations
    (
        "CFG-01",
        "Permissive CORS Wildcard",
        "HIGH",
        re.compile(r"(?i)(?:Access-Control-Allow-Origin\s*[:=]\s*['\"]?\*|origin\s*[:=]\s*['\"]\*(?!.)['\"])"),
        "Restrict Allowed Origins to specific trusted domains instead of '*'.",
    ),
    (
        "CFG-02",
        "Debug Mode Enabled",
        "MEDIUM",
        re.compile(r"(?i)(?:DEBUG\s*=\s*True|app\.debug\s*=\s*True|ENVIRONMENT\s*=\s*['\"]development['\"])"),
        "Ensure debug mode is disabled in production configurations.",
    ),
    (
        "CFG-03",
        "Insecure Plaintext HTTP URL",
        "LOW",
        re.compile(r"http://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s'\"]*)?"),
        "Upgrade plaintext HTTP URLs to HTTPS.",
    ),
]

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".egg-info",
    "dist",
    "build",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".woff",
    ".woff2",
    ".ttf",
}


@dataclass
class Finding:
    rule_id: str
    rule_title: str
    severity: str
    file_path: str
    line_number: int
    snippet: str
    remediation: str

    def to_dict(self) -> dict:
        return asdict(self)


def is_ignored(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    return False


def mask_secret(text: str) -> str:
    if len(text) <= 6:
        return "***"
    return text[:3] + "..." + text[-3:]


def scan_directory(target_dir: Path, min_severity: str = "LOW") -> List[Finding]:
    findings: List[Finding] = []
    min_idx = SEVERITY_LEVELS.index(min_severity.upper())

    if not target_dir.exists():
        raise FileNotFoundError(f"Target directory does not exist: {target_dir}")

    for root, dirs, files in os.walk(target_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for fname in files:
            file_path = Path(root) / fname
            if is_ignored(file_path):
                continue

            try:
                # Read text with replacement for non-utf8 characters
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel_path = str(file_path.relative_to(target_dir))
            lines = content.splitlines()

            for line_idx, line in enumerate(lines, 1):
                # Skip comments in this scanner to avoid false positives on self-references
                if "re.compile" in line:
                    continue

                for rule_id, title, sev, pattern, remed in PATTERNS:
                    if SEVERITY_LEVELS.index(sev) < min_idx:
                        continue

                    match = pattern.search(line)
                    if match:
                        matched_str = match.group(0)
                        # Mask snippet
                        masked_line = line.replace(matched_str, mask_secret(matched_str)).strip()
                        findings.append(
                            Finding(
                                rule_id=rule_id,
                                rule_title=title,
                                severity=sev,
                                file_path=rel_path,
                                line_number=line_idx,
                                snippet=masked_line[:120],
                                remediation=remed,
                            )
                        )

    return findings


def format_report_text(findings: List[Finding], target_dir: Path) -> str:
    out = [f"Security & Configuration Scan Report: {target_dir.resolve()}"]
    out.append("=" * 60)
    if not findings:
        out.append("[OK] Clean scan: 0 security or configuration issues detected.")
        return "\n".join(out)

    by_sev: Dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1

    summary = ", ".join(f"{s}: {by_sev[s]}" for s in reversed(SEVERITY_LEVELS) if s in by_sev)
    out.append(f"Total Findings: {len(findings)} ({summary})\n")

    for idx, f in enumerate(findings, 1):
        out.append(f"[{f.severity}] #{idx} {f.rule_title} ({f.rule_id})")
        out.append(f"  Location: {f.file_path}:{f.line_number}")
        out.append(f"  Snippet:  {f.snippet}")
        out.append(f"  Fix:      {f.remediation}")
        out.append("")

    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="security-config-scanner",
        description="Scan project directory for exposed credentials and insecure configs.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Target directory to scan (default: current directory)")
    parser.add_argument("--severity", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], default="LOW", help="Minimum severity threshold")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit with code 1 if any HIGH or CRITICAL issues are found")

    args = parser.parse_args(argv)
    target = Path(args.path)

    try:
        findings = scan_directory(target, min_severity=args.severity)
    except Exception as err:
        if args.json:
            print(json.dumps({"status": "error", "message": str(err)}, indent=2))
        else:
            print(f"[ERROR] Scan failed: {err}", file=sys.stderr)
        return 2

    if args.json:
        report = {
            "status": "success",
            "target": str(target.resolve()),
            "total_findings": len(findings),
            "findings": [f.to_dict() for f in findings],
        }
        print(json.dumps(report, indent=2))
    else:
        print(format_report_text(findings, target))

    if args.fail_on_findings:
        critical_or_high = any(f.severity in ("CRITICAL", "HIGH") for f in findings)
        if critical_or_high:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
