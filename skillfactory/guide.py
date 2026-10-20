"""Beginner Guided Onboarding Wizard (Phases 15 & 16, Workstream 16A).

Provides an interactive, beginner-friendly walkthrough:
1. Pre-flight health and prerequisite diagnostics.
2. AI assistant discovery and selection with OS-specific path guidance (macOS, Linux, Windows).
3. Guided skill specification (name, purpose, template).
4. Deterministic scaffolding generation.
5. Immediate validation and unit test execution.
6. Optional platform installation with backup and collision defense.
7. Complete end-to-end lifecycle guidance (Test, Eval, Scan, Update, Rollback, Uninstall).
"""
from __future__ import annotations

import os
import platform as sys_platform
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from skillfactory import __version__
from skillfactory.compat.detect import detect_all_platforms
from skillfactory.compat.platform_db import get_all_platforms, normalize_platform_id
from skillfactory.core import generate_skill
from skillfactory.doctor import format_guided_setup, run_diagnostics
from skillfactory.errors import SkillFactoryError
from skillfactory.installer import install_skill
from skillfactory.spec import SkillSpec
from skillfactory.tester import run_skill_tests
from skillfactory.ui_util import format_status
from skillfactory.validator import validate_skill


def get_os_friendly_name() -> str:
    """Return a human-readable operating system descriptor."""
    os_name = sys_platform.system()
    if os_name == "Darwin":
        return "macOS"
    elif os_name == "Windows":
        return "Windows"
    elif os_name == "Linux":
        return "Linux"
    return os_name or "Unknown OS"


def get_os_path_guidance(platform_id: str) -> str:
    """Return OS-specific directory guidance for the target AI coding assistant."""
    os_type = sys_platform.system()
    home = Path.home()

    if platform_id == "antigravity":
        if os_type == "Windows":
            return r"%USERPROFILE%\.agents\skills"
        return f"{home}/.agents/skills"
    elif platform_id == "claude-code":
        if os_type == "Windows":
            return r"%APPDATA%\Claude\skills or %USERPROFILE%\.claude\skills"
        elif os_type == "Darwin":
            return f"{home}/Library/Application Support/Claude/skills or ~/.claude/skills"
        return f"{home}/.config/claude/skills or ~/.claude/skills"
    elif platform_id == "cursor":
        if os_type == "Windows":
            return r"%USERPROFILE%\.cursor\skills"
        return f"{home}/.cursor/skills"
    elif platform_id == "codex":
        if os_type == "Windows":
            return r"%USERPROFILE%\.codex\skills"
        return f"{home}/.codex/skills"
    elif platform_id == "windsurf":
        if os_type == "Windows":
            return r"%USERPROFILE%\.codeium\windsurf\skills"
        return f"{home}/.codeium/windsurf/skills"
    elif platform_id == "continue":
        if os_type == "Windows":
            return r"%USERPROFILE%\.continue\prompts"
        return f"{home}/.continue/prompts"
    elif platform_id == "cline":
        if os_type == "Windows":
            return r"%USERPROFILE%\.cline\skills"
        return f"{home}/.cline/skills"
    elif platform_id == "copilot":
        if os_type == "Windows":
            return r"%USERPROFILE%\.github\skills"
        return f"{home}/.github/skills"
    return str(home / "skills")


def run_beginner_guide(
    non_interactive: bool = False,
    skill_name: Optional[str] = None,
    platform: Optional[str] = None,
    output_dir: Optional[Path] = None,
    input_func: Callable[[str], str] = input,
    print_func: Callable[..., None] = print,
) -> int:
    """Run the interactive beginner onboarding wizard with OS-specific path guidance."""
    os_desc = get_os_friendly_name()

    print_func("\n" + "=" * 72)
    print_func(f" Skill Factory v{__version__} — Guided Onboarding Wizard ({os_desc})")
    print_func("=" * 72)
    print_func("Welcome! This wizard guides you through creating, testing, validating,")
    print_func("and installing your first Agent Skill with zero manual setup.\n")

    # Step 1: System Health & Diagnostic Check
    print_func(f"[Step 1/5] Checking System Prerequisites ({os_desc})...")
    report = run_diagnostics()
    if not report.is_ready:
        print_func(format_status("FAIL", "System prerequisites not met."))
        for item in report.action_items:
            print_func(f"  • {item}")
        return 1
    print_func(format_status("OK", f"Python {report.python_version} ready | Directory writable | Platform: {os_desc}"))

    # Step 2: AI Coding Assistant Selection & OS Path Guidance
    print_func("\n[Step 2/5] Selecting Target AI Assistant...")
    detected = detect_all_platforms()
    detected_ids = [d.platform_id for d in detected.values() if d.detected]

    all_plats = get_all_platforms()
    available_platforms = [
        ("claude-code", "Claude Code (Anthropic)"),
        ("antigravity", "Google Antigravity (Google)"),
        ("cursor", "Cursor (Anysphere)"),
        ("codex", "OpenAI Codex (OpenAI)"),
        ("windsurf", "Windsurf (Codeium)"),
        ("continue", "Continue (Continue.dev)"),
        ("cline", "Cline"),
        ("copilot", "GitHub Copilot"),
        ("standalone", "Local / Standalone Directory (No Assistant)"),
    ]

    selected_platform = platform
    if not selected_platform:
        if non_interactive or not sys.stdin.isatty():
            # In non-interactive mode, default to detected or claude-code
            selected_platform = detected_ids[0] if detected_ids else "claude-code"
            print_func(f"Non-interactive mode: defaulting to target platform '{selected_platform}'.")
        else:
            print_func(f"Available AI coding assistants for {os_desc}:")
            for idx, (p_id, p_name) in enumerate(available_platforms, start=1):
                marker = " [DETECTED]" if p_id in detected_ids else ""
                path_hint = get_os_path_guidance(p_id) if p_id != "standalone" else "Local directory"
                print_func(f"  [{idx}] {p_name}{marker}")
                print_func(f"      Default path: {path_hint}")

            try:
                choice = input_func("\nEnter number [1-9] (default: 1): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(available_platforms):
                    selected_platform = available_platforms[int(choice) - 1][0]
                else:
                    selected_platform = available_platforms[0][0]
            except (EOFError, KeyboardInterrupt):
                print_func("\nSetup cancelled.")
                return 1

    guidance_path = get_os_path_guidance(selected_platform)
    print_func(format_status("OK", f"Target platform: {selected_platform} (Folder: {guidance_path})"))

    # Step 3: Skill Definition
    print_func("\n[Step 3/5] Defining Your Skill...")
    chosen_name = skill_name
    if not chosen_name:
        if non_interactive or not sys.stdin.isatty():
            chosen_name = "my-first-skill"
        else:
            try:
                inp_name = input_func("Enter skill name (e.g. 'excel-diff', default: 'my-first-skill'): ").strip()
                chosen_name = inp_name if inp_name else "my-first-skill"
            except (EOFError, KeyboardInterrupt):
                print_func("\nSetup cancelled.")
                return 1

    # Sanitize name to kebab-case
    sanitized_name = chosen_name.lower().replace(" ", "-").replace("_", "-")
    sanitized_name = "".join(c for c in sanitized_name if c.isalnum() or c == "-").strip("-")
    if not sanitized_name:
        sanitized_name = "my-first-skill"

    desc = f"Agent skill for {sanitized_name.replace('-', ' ')}."
    target_out = output_dir or (Path.cwd() / "skills")

    spec = SkillSpec(
        name=sanitized_name,
        description=desc,
        template_family="python-script",
        author="Skill Factory Beginner",
        license="MIT",
    )

    # Step 4: Scaffolding Generation
    print_func("\n[Step 4/5] Generating Skill Scaffolding...")
    gen_result = generate_skill(spec, target_out)
    skill_dir = target_out / sanitized_name
    print_func(format_status("OK", f"Skill created at: {skill_dir}"))

    # Step 5: Validation & Testing
    print_func("\n[Step 5/5] Validating Structure & Testing...")
    val_report = validate_skill(skill_dir)
    if not val_report.is_valid:
        print_func(format_status("FAIL", f"Validation failed: {val_report.errors}"))
        return 1
    print_func(format_status("OK", "Specification and directory integrity verified!"))

    test_res = run_skill_tests(skill_dir)
    if not test_res.success:
        print_func(format_status("WARN", f"Test runner notice: {test_res.error_message}"))
    else:
        print_func(format_status("OK", f"Baseline tests executed in {test_res.duration_sec:.2f}s."))

    # Optional Installation
    if selected_platform and selected_platform != "standalone":
        do_install = False
        if non_interactive:
            do_install = True
        else:
            try:
                ans = input_func(f"\nInstall '{sanitized_name}' into {selected_platform} now? [Y/n]: ").strip().lower()
                do_install = ans in ("", "y", "yes")
            except (EOFError, KeyboardInterrupt):
                do_install = False

        if do_install:
            try:
                inst_res = install_skill(
                    skill_path=skill_dir,
                    target_platform=selected_platform,
                    scope="project",
                )
                print_func(format_status("OK", f"Installed into {selected_platform}: {inst_res.installed_path}"))
            except Exception as e:
                print_func(format_status("WARN", f"Installation note: {e}"))

    # Summary & Complete Lifecycle Guide
    print_func("\n" + "=" * 72)
    print_func(" Skill Created Successfully! Full Lifecycle Commands:")
    print_func("=" * 72)
    print_func("1. Implementation:")
    print_func(f"   Edit logic in: {skill_dir / 'scripts' / 'main.py'}")
    print_func("2. Testing (Run after modifying code):")
    print_func(f"   skillfactory test {skill_dir}")
    print_func("3. Quality Evaluation (Scores Grade A to F):")
    print_func(f"   skillfactory eval {skill_dir}")
    print_func("4. Security Scanning (Intercepts vulnerabilities):")
    print_func(f"   skillfactory scan {skill_dir}")
    print_func("5. Deployment & Updates:")
    print_func(f"   Install:   skillfactory install {skill_dir} --platform {selected_platform}")
    print_func(f"   Update:    skillfactory update {sanitized_name}")
    print_func(f"   Rollback:  skillfactory rollback {sanitized_name}")
    print_func(f"   Uninstall: skillfactory uninstall {sanitized_name} --platform {selected_platform}\n")

    return 0
