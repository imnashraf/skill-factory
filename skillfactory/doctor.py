"""System diagnostics and guided environment troubleshooting (Phase 12, Task T12.01, AC12.01).

Zero third-party dependencies. Pure Python standard library implementation.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.compat.detect import detect_all_platforms
from skillfactory.compat.platform_db import detect_os_key, get_all_platforms
from skillfactory.ui_util import format_status


@dataclass
class DiagnosticCheck:
    """Individual diagnostic check result."""
    name: str
    category: str
    status: str  # OK, WARNING, FAIL, INFO
    message: str
    remediation: Optional[str] = None


@dataclass
class HealthReport:
    """Comprehensive environment health and diagnostics report."""
    python_version: str
    python_executable: str
    python_compatible: bool
    os_name: str
    os_platform: str
    project_dir: str
    project_writable: bool
    home_dir: str
    home_writable: bool
    skillfactory_on_path: bool
    detected_platforms: List[str]
    checks: List[DiagnosticCheck] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)

    @property
    def is_ready(self) -> bool:
        return self.python_compatible and self.project_writable

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["is_ready"] = self.is_ready
        return data


def run_diagnostics(
    project_dir: Optional[Path | str] = None,
    home_dir: Optional[Path | str] = None,
) -> HealthReport:
    """Run full diagnostic checks on system, filesystem permissions, and AI platform paths."""
    p_dir = Path(project_dir).resolve() if project_dir else Path.cwd().resolve()
    h_dir = Path(home_dir).resolve() if home_dir else Path.home().resolve()

    py_ver = sys.version_info
    py_ver_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    py_compatible = py_ver >= (3, 9)
    os_name = detect_os_key()

    # Permission checks
    proj_writable = os.access(p_dir, os.W_OK) if p_dir.exists() else os.access(p_dir.parent, os.W_OK)
    home_writable = os.access(h_dir, os.W_OK)

    # CLI executable check
    sf_cmd = shutil.which("skillfactory")
    on_path = sf_cmd is not None

    checks: List[DiagnosticCheck] = []
    actions: List[str] = []

    # 1. Python version check
    if py_compatible:
        checks.append(
            DiagnosticCheck(
                name="Python Version",
                category="Runtime",
                status="OK",
                message=f"Python {py_ver_str} meets requirements (3.9+).",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="Python Version",
                category="Runtime",
                status="FAIL",
                message=f"Python {py_ver_str} is unsupported. Skill Factory requires Python 3.9 or higher.",
                remediation="Install Python 3.9+ from https://www.python.org/downloads/ or via your system package manager.",
            )
        )
        actions.append("Upgrade your Python runtime to version 3.9 or newer.")

    # 2. Permissions check
    if proj_writable:
        checks.append(
            DiagnosticCheck(
                name="Project Directory Permissions",
                category="Filesystem",
                status="OK",
                message=f"Write access verified for '{p_dir}'.",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="Project Directory Permissions",
                category="Filesystem",
                status="FAIL",
                message=f"Project directory '{p_dir}' is read-only.",
                remediation=f"Ensure write permissions for the directory: chmod u+w '{p_dir}'",
            )
        )
        actions.append(f"Grant write permissions to project folder: chmod u+w '{p_dir}'")

    # 3. PATH accessibility check
    if on_path:
        checks.append(
            DiagnosticCheck(
                name="CLI Command in PATH",
                category="Environment",
                status="OK",
                message=f"'skillfactory' binary found at '{sf_cmd}'.",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="CLI Command in PATH",
                category="Environment",
                status="WARNING",
                message="'skillfactory' command is not in your current PATH. You can invoke it using 'python3 -m skillfactory'.",
                remediation="Add Python user scripts directory to your PATH (e.g. export PATH=\"$HOME/.local/bin:$PATH\"), or run 'pip install -e .'.",
            )
        )
        actions.append("Add the Python scripts directory to your shell PATH or use 'python3 -m skillfactory'.")

    # 4. Platform discovery check
    platform_results = detect_all_platforms(project_dir=p_dir, home_dir=h_dir)
    detected_list = [pid for pid, r in platform_results.items() if r.detected]

    if detected_list:
        display_names = [platform_results[pid].display_name for pid in detected_list]
        checks.append(
            DiagnosticCheck(
                name="AI Coding Assistants",
                category="Compatibility",
                status="OK",
                message=f"Detected {len(detected_list)} platform(s): {', '.join(display_names)}.",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="AI Coding Assistants",
                category="Compatibility",
                status="INFO",
                message="No AI assistant configuration directories were detected in this workspace.",
                remediation="You can install skills directly to the shared '.agents/skills/' directory, or install an assistant like Claude Code or Cursor.",
            )
        )
        actions.append("Skills will install into the shared '.agents/skills/' directory by default.")

    return HealthReport(
        python_version=py_ver_str,
        python_executable=sys.executable,
        python_compatible=py_compatible,
        os_name=os_name,
        os_platform=sys.platform,
        project_dir=str(p_dir),
        project_writable=proj_writable,
        home_dir=str(h_dir),
        home_writable=home_writable,
        skillfactory_on_path=on_path,
        detected_platforms=detected_list,
        checks=checks,
        action_items=actions,
    )


def format_guided_setup(report: HealthReport) -> str:
    """Render a guided, beginner-oriented environment setup view."""
    lines: List[str] = []
    lines.append("=" * 68)
    lines.append(" Skill Factory — Guided Beginner Setup & Environment Diagnostics")
    lines.append("=" * 68)

    lines.append("\n[1/4] Runtime & Prerequisite Check")
    for chk in report.checks:
        lines.append(f"  {format_status(chk.status, chk.name)}")
        lines.append(f"    {chk.message}")
        if chk.remediation:
            lines.append(f"    --> Remediation: {chk.remediation}")

    lines.append("\n[2/4] Readiness Assessment")
    if report.is_ready:
        lines.append(f"  {format_status('OK', 'Environment is ready to build and install skills!')}")
    else:
        lines.append(f"  {format_status('FAIL', 'Environment requires setup adjustments before proceeding.')}")

    if report.action_items:
        lines.append("\n[3/4] Recommended Action Items")
        for idx, action in enumerate(report.action_items, 1):
            lines.append(f"  {idx}. {action}")
    else:
        lines.append("\n[3/4] Recommended Action Items")
        lines.append("  • None! All system checks are passing.")

    lines.append("\n[4/4] Beginner Quick Commands")
    lines.append("  • Create your first skill:")
    lines.append("      skillfactory new my-first-skill")
    lines.append("  • Validate your skill:")
    lines.append("      skillfactory validate ./my-first-skill")
    lines.append("  • Run the reference demonstrations:")
    lines.append("      python3 scripts/run_demos.py")

    lines.append("\n[Maintenance & Lifecycle]")
    lines.append("  • Update Skill Factory:")
    lines.append("      pip install --upgrade git+https://github.com/imnashraf/skill-factory.git")
    lines.append("  • Uninstall Skill Factory:")
    lines.append("      pip uninstall skill-factory")
    lines.append("      rm -rf ~/.skillfactory")

    lines.append("=" * 68)
    return "\n".join(lines)
