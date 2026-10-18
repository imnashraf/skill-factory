"""AST safety scanner and secret detector (Phase 5, Tasks T5.02, T8.01).

Uses Python's built-in `ast` module to analyze Python scripts for dangerous
calls, untrusted shell executions, and destructive file system operations without
executing the code. Also scans files for hardcoded secrets, tokens, and private keys.
"""
from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Secret pattern definitions (SEC-02, T8.01)
SECRET_PATTERNS = [
    (
        "SEC001",
        "AWS Access Key ID",
        re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),
        "CRITICAL",
    ),
    (
        "SEC002",
        "GitHub Personal Access Token",
        re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,255}\b"),
        "CRITICAL",
    ),
    (
        "SEC003",
        "OpenAI API Key",
        re.compile(r"\b(sk-[A-Za-z0-9]{20,T3BlbkFJ[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{20,})\b"),
        "CRITICAL",
    ),
    (
        "SEC004",
        "Private Cryptographic Key",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        "CRITICAL",
    ),
    (
        "SEC005",
        "Generic High-Entropy Secret / Token Assignment",
        re.compile(
            r"""(?i)\b(?:api[_-]?key|secret|auth[_-]?token|access[_-]?token|private[_-]?key)\s*[:=]\s*["']([A-Za-z0-9+/=_\-]{24,})["']"""
        ),
        "HIGH",
    ),
]

# File patterns to exclude from secret scanning (test fixtures, caches, etc.)
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "node_modules",
}


@dataclass
class Finding:
    rule_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    file_path: str
    line_number: int
    description: str
    snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SafetyReport:
    is_clean: bool
    findings: List[Finding]
    files_scanned: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_clean": self.is_clean,
            "files_scanned": self.files_scanned,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "findings": [f.to_dict() for f in self.findings],
        }


class CodeSafetyVisitor(ast.NodeVisitor):
    """AST Visitor detecting dangerous constructs in Python source code."""

    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.findings: List[Finding] = []

    def _get_snippet(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1].strip()
        return ""

    def _add_finding(self, rule_id: str, severity: str, lineno: int, description: str):
        self.findings.append(
            Finding(
                rule_id=rule_id,
                severity=severity,
                file_path=self.file_path,
                line_number=lineno,
                description=description,
                snippet=self._get_snippet(lineno),
            )
        )

    def visit_Call(self, node: ast.Call):
        func = node.func
        lineno = getattr(node, "lineno", 1)

        # 1. Direct built-in calls: eval, exec, compile, __import__
        if isinstance(func, ast.Name):
            if func.id in ("eval", "exec"):
                self._add_finding(
                    rule_id="AST001",
                    severity="CRITICAL",
                    lineno=lineno,
                    description=f"Dangerous dynamic code execution call '{func.id}()'",
                )
            elif func.id == "__import__":
                self._add_finding(
                    rule_id="AST002",
                    severity="HIGH",
                    lineno=lineno,
                    description="Dynamic module loading via '__import__()'",
                )

        # 2. Attribute calls: os.system, os.popen, shutil.rmtree, subprocess.*
        elif isinstance(func, ast.Attribute):
            attr = func.attr
            # os.system, os.popen
            if isinstance(func.value, ast.Name) and func.value.id == "os":
                if attr in ("system", "popen", "popen2", "popen3", "popen4"):
                    self._add_finding(
                        rule_id="AST003",
                        severity="CRITICAL",
                        lineno=lineno,
                        description=f"Arbitrary shell execution via 'os.{attr}()'",
                    )
                elif attr in ("remove", "unlink", "rmdir"):
                    # Check if removing root or dangerous variable
                    if node.args:
                        arg0 = node.args[0]
                        if isinstance(arg0, ast.Constant) and arg0.value in ("/", "\\", "C:\\"):
                            self._add_finding(
                                rule_id="AST004",
                                severity="CRITICAL",
                                lineno=lineno,
                                description=f"Dangerous file deletion on root directory via 'os.{attr}()'",
                            )

            # shutil.rmtree
            elif isinstance(func.value, ast.Name) and func.value.id == "shutil":
                if attr == "rmtree":
                    # Check first argument for root directory or critical path
                    is_dangerous_root = False
                    if node.args:
                        arg0 = node.args[0]
                        if isinstance(arg0, ast.Constant) and arg0.value in ("/", "\\", "C:\\"):
                            is_dangerous_root = True

                    if is_dangerous_root:
                        self._add_finding(
                            rule_id="AST005",
                            severity="CRITICAL",
                            lineno=lineno,
                            description="Destructive directory wipe of system root via 'shutil.rmtree()'",
                        )
                    else:
                        self._add_finding(
                            rule_id="AST006",
                            severity="MEDIUM",
                            lineno=lineno,
                            description="Recursive directory deletion via 'shutil.rmtree()'",
                        )

            # subprocess calls with shell=True
            elif isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                # Check keyword arguments for shell=True
                for kw in node.keywords:
                    if kw.arg == "shell":
                        if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            self._add_finding(
                                rule_id="AST007",
                                severity="CRITICAL",
                                lineno=lineno,
                                description=f"Subprocess call 'subprocess.{attr}()' executed with shell=True",
                            )

        self.generic_visit(node)


def scan_python_code(code_str: str, file_path: str = "<string>") -> List[Finding]:
    """Scan a Python code string using AST analysis."""
    findings: List[Finding] = []
    lines = code_str.splitlines()

    try:
        tree = ast.parse(code_str, filename=file_path)
    except SyntaxError as err:
        findings.append(
            Finding(
                rule_id="AST000",
                severity="HIGH",
                file_path=file_path,
                line_number=err.lineno or 1,
                description=f"Python syntax error in script: {err.msg}",
                snippet=lines[err.lineno - 1].strip() if err.lineno and err.lineno <= len(lines) else "",
            )
        )
        return findings

    visitor = CodeSafetyVisitor(file_path=file_path, source_lines=lines)
    visitor.visit(tree)
    findings.extend(visitor.findings)
    return findings


def scan_secrets_in_text(text: str, file_path: str = "<text>") -> List[Finding]:
    """Scan text content for hardcoded secrets, credentials, and API keys."""
    findings: List[Finding] = []
    lines = text.splitlines()

    for line_idx, line in enumerate(lines, 1):
        # Ignore comments or mock documentation explicitly mentioning dummy/example
        line_clean = line.strip()
        if line_clean.startswith("#") and "example" in line_clean.lower():
            continue

        for rule_id, rule_name, pattern, severity in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                # Mask secret snippet for security in logs/reports
                matched_text = match.group(0)
                if len(matched_text) > 8:
                    masked = matched_text[:4] + "..." + matched_text[-4:]
                else:
                    masked = "***"
                snippet = line_clean.replace(matched_text, masked)

                findings.append(
                    Finding(
                        rule_id=rule_id,
                        severity=severity,
                        file_path=file_path,
                        line_number=line_idx,
                        description=f"Hardcoded credential detected: {rule_name}",
                        snippet=snippet,
                    )
                )

    return findings


def scan_file(file_path: Path) -> List[Finding]:
    """Scan a single file for both secrets and (if Python) AST safety issues."""
    path = Path(file_path)
    if not path.is_file():
        return []

    findings: List[Finding] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as err:
        findings.append(
            Finding(
                rule_id="IO001",
                severity="LOW",
                file_path=str(path),
                line_number=1,
                description=f"Could not read file for safety scan: {err}",
            )
        )
        return findings

    # 1. Secret scan on all text files
    findings.extend(scan_secrets_in_text(content, file_path=str(path)))

    # 2. AST scan on Python files (.py)
    if path.suffix == ".py":
        findings.extend(scan_python_code(content, file_path=str(path)))

    return findings


def scan_skill_directory(skill_dir: Path, exclude_tests: bool = False) -> SafetyReport:
    """Scan all relevant files in a skill directory for safety and secrets.

    Args:
        skill_dir: Directory containing the agent skill.
        exclude_tests: If True, skips files inside tests/ directory.

    Returns:
        SafetyReport detailing all findings and counts.
    """
    root = Path(skill_dir).resolve()
    all_findings: List[Finding] = []
    files_scanned = 0

    if not root.exists() or not root.is_dir():
        return SafetyReport(
            is_clean=False,
            findings=[
                Finding(
                    rule_id="DIR001",
                    severity="CRITICAL",
                    file_path=str(root),
                    line_number=1,
                    description=f"Skill directory does not exist or is not a directory: {root}",
                )
            ],
            files_scanned=0,
            critical_count=1,
            high_count=0,
            medium_count=0,
            low_count=0,
        )

    for item in root.rglob("*"):
        if not item.is_file():
            continue

        # Skip excluded dirs
        rel_parts = item.relative_to(root).parts
        if any(part in DEFAULT_EXCLUDE_DIRS for part in rel_parts):
            continue

        if exclude_tests and "tests" in rel_parts:
            continue

        # Skip binary files, git files, temporary files
        if item.suffix in (".pyc", ".png", ".jpg", ".jpeg", ".ico", ".zip", ".tar", ".gz"):
            continue

        findings = scan_file(item)
        all_findings.extend(findings)
        files_scanned += 1

    crit = sum(1 for f in all_findings if f.severity == "CRITICAL")
    high = sum(1 for f in all_findings if f.severity == "HIGH")
    med = sum(1 for f in all_findings if f.severity == "MEDIUM")
    low = sum(1 for f in all_findings if f.severity == "LOW")

    is_clean = (crit == 0 and high == 0)

    return SafetyReport(
        is_clean=is_clean,
        findings=all_findings,
        files_scanned=files_scanned,
        critical_count=crit,
        high_count=high,
        medium_count=med,
        low_count=low,
    )
