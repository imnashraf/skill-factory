"""Beginner Guided Onboarding Wizard (Phase 15, Workstream B).

Provides an interactive step-by-step walkthrough for first-time users:
1. Pre-flight health and prerequisite diagnostics.
2. AI assistant discovery and selection.
3. Guided skill specification (name, purpose, template).
4. Deterministic scaffolding generation.
5. Immediate validation and unit test execution.
6. Optional platform installation with backup and collision defense.
7. Clear actionable instructions for next steps and activation.
"""
from __future__ import annotations

import os
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


def run_beginner_guide(
    non_interactive: bool = False,
    skill_name: Optional[str] = None,
    platform: Optional[str] = None,
    output_dir: Optional[Path] = None,
    input_func: Callable[[str], str] = input,
    print_func: Callable[..., None] = print,
) -> int:
    """Run the interactive beginner onboarding wizard."""
    print_func("\n" + "=" * 70)
    print_func(f" Skill Factory v{__version__} — Interactive Beginner Onboarding Wizard")
    print_func("=" * 70)
    print_func("Welcome! This wizard will guide you through creating, testing, and")
    print_func("installing your first Agent Skill in just a few simple steps.\n")

    # Step 1: System Health & Diagnostic Check
    print_func("[Step 1/5] Checking System Prerequisites...")
    report = run_diagnostics()
    if not report.is_ready:
        print_func(format_status("FAIL", "System prerequisites not met."))
        for item in report.action_items:
            print_func(f"  • {item}")
        return 1
    print_func(format_status("OK", f"Python {report.python_version} ready | Directory writable"))

    # Step 2: AI Coding Assistant Selection
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
            print_func("Which AI coding assistant do you want to create this skill for?")
            for idx, (p_id, p_name) in enumerate(available_platforms, start=1):
                marker = " [DETECTED]" if p_id in detected_ids else ""
                print_func(f"  [{idx}] {p_name}{marker}")

            try:
                choice = input_func("\nEnter number [1-9] (default: 1): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(available_platforms):
                    selected_platform = available_platforms[int(choice) - 1][0]
                else:
                    selected_platform = available_platforms[0][0]
            except (EOFError, KeyboardInterrupt):
                print_func("\nSetup cancelled.")
                return 1

    print_func(format_status("OK", f"Target platform: {selected_platform}"))

    # Step 3: Skill Definition
    print_func("\n[Step 3/5] Defining Your Skill...")
    chosen_name = skill_name
    if not chosen_name:
        if non_interactive or not sys.stdin.isatty():
            chosen_name = "my-first-skill"
        else:
            try:
                inp_name = input_func("Enter skill name (lowercase, e.g. 'pdf-extractor', default: 'my-first-skill'): ").strip()
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
    print_func(format_status("OK", f"Skill generated at: {skill_dir}"))

    # Step 5: Validation & Testing
    print_func("\n[Step 5/5] Validating & Verifying Tests...")
    val_report = validate_skill(skill_dir)
    if not val_report.is_valid:
        print_func(format_status("FAIL", f"Validation failed: {val_report.errors}"))
        return 1
    print_func(format_status("OK", "Specification and structure verified!"))

    test_res = run_skill_tests(skill_dir)
    if not test_res.success:
        print_func(format_status("WARN", f"Test runner notice: {test_res.error_message}"))
    else:
        print_func(format_status("OK", f"Passed baseline tests in {test_res.duration_sec:.2f}s."))

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
                print_func(format_status("WARN", f"Installation notice: {e}"))

    # Summary & Actionable Next Steps
    print_func("\n" + "=" * 70)
    print_func(" Skill Created Successfully! What to do next:")
    print_func("=" * 70)
    print_func(f"1. Open the implementation file:")
    print_func(f"   {skill_dir / 'scripts' / 'main.py'}")
    print_func(f"2. Add your custom task logic or ask your AI coding assistant:")
    print_func(f"   'Implement scripts/main.py for {sanitized_name}'")
    print_func(f"3. Re-run tests anytime:")
    print_func(f"   skillfactory test {skill_dir}")
    print_func(f"4. Re-evaluate quality:")
    print_func(f"   skillfactory eval {skill_dir}\n")

    return 0
