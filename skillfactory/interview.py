"""Offline Guided Interview Engine and Batch Spec Builder (Phase 2, Tasks T2.02, T2.03).

Provides both an interactive terminal questionnaire and non-interactive batch answers execution.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skillfactory.spec import (
    NAME_PATTERN,
    PLATFORM_RESERVED_NAMES,
    WINDOWS_RESERVED_NAMES,
    SkillSpec,
)
from skillfactory.templates.router import route_template


def derive_skill_name(text: str) -> str:
    """Derive a valid kebab-case skill name from a plain English problem description (FR-NL-04)."""
    # Lowercase and convert non-alphanumeric characters to hyphens
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    # Strip leading and trailing hyphens
    cleaned = cleaned.strip("-")
    # Collapse multiple consecutive hyphens
    cleaned = re.sub(r"-+", "-", cleaned)

    if not cleaned:
        cleaned = "custom-skill"

    # Truncate to 64 chars at word boundary if possible
    if len(cleaned) > 64:
        truncated = cleaned[:64].rstrip("-")
        # Try cutting at last hyphen
        last_dash = truncated.rfind("-")
        if last_dash > 10:
            cleaned = truncated[:last_dash]
        else:
            cleaned = truncated

    # Check for reserved names
    if cleaned in WINDOWS_RESERVED_NAMES or cleaned in PLATFORM_RESERVED_NAMES:
        cleaned = f"{cleaned}-skill"

    return cleaned


def prompt_user(question: str, default: str = "") -> str:
    """Prompt the user with an optional default value."""
    if default:
        prompt_str = f"{question} [{default}]: "
    else:
        prompt_str = f"{question}: "
    try:
        ans = input(prompt_str).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInterview cancelled.", file=sys.stderr)
        sys.exit(1)
    return ans if ans else default


def build_spec_from_answers(answers: Dict[str, Any]) -> SkillSpec:
    """Construct a validated SkillSpec from an answers mapping."""
    problem = answers.get("problem", "").strip()
    desc = answers.get("description", "").strip()
    if not desc and problem:
        desc = problem

    if not desc:
        desc = "Agent skill created with Skill Factory."

    # Derive or validate name
    raw_name = answers.get("name", "").strip()
    if raw_name:
        name = raw_name
    else:
        name = derive_skill_name(problem or desc)

    # Route template if not explicitly specified
    requires_scripts = answers.get("requires_scripts")
    template_family = answers.get("template_family")
    if not template_family:
        template_family, _ = route_template(desc, requires_scripts=requires_scripts)

    # Format inputs, outputs, steps
    inputs = answers.get("inputs", [])
    if isinstance(inputs, str):
        inputs = [i.strip() for i in inputs.split(",") if i.strip()]

    outputs = answers.get("outputs", [])
    if isinstance(outputs, str):
        outputs = [o.strip() for o in outputs.split(",") if o.strip()]

    steps = answers.get("steps", [])
    if isinstance(steps, str):
        steps = [s.strip() for s in steps.splitlines() if s.strip()]

    author = answers.get("author", "")
    license_choice = answers.get("license", "MIT")

    spec = SkillSpec(
        name=name,
        description=desc,
        template_family=template_family,
        inputs=inputs,
        outputs=outputs,
        steps=steps,
        author=author,
        license=license_choice,
    )
    return spec


def run_interactive_interview() -> SkillSpec:
    """Run an interactive guided terminal questionnaire."""
    print("=" * 60)
    print(" Skill Factory — Guided Skill Builder")
    print("=" * 60)
    print("Answer the questions below to design your Agent Skill.\n")

    # Q1: Problem
    problem = prompt_user("1. What problem or task does this skill solve?")
    while not problem:
        print("   Please provide a brief problem description.")
        problem = prompt_user("1. What problem or task does this skill solve?")

    # Q2: Suggested Name
    suggested_name = derive_skill_name(problem)
    name = prompt_user("2. Skill identifier (lowercase kebab-case)", default=suggested_name)

    # Q3: Description
    description = prompt_user(
        "3. Clear description for agent trigger (1-1024 characters)",
        default=problem,
    )

    # Q4: Executable code requirement
    scripts_input = prompt_user(
        "4. Does this skill require custom Python scripts? (y/n)",
        default="y",
    ).lower()
    requires_scripts = scripts_input in ("y", "yes", "true", "1")

    # Template suggestion
    suggested_template, reason = route_template(description, requires_scripts=requires_scripts)
    print(f"\n   [Recommendation] Template: '{suggested_template}' ({reason})")
    template_family = prompt_user(
        "5. Template family (instructions-only, python-script, checklist-review, file-transform, workflow-runbook)",
        default=suggested_template,
    )

    # Q6: Inputs & Outputs
    inputs_str = prompt_user("6. Expected inputs (comma-separated, optional)", default="")
    outputs_str = prompt_user("7. Expected outputs (comma-separated, optional)", default="")

    # Q8: Steps
    print("8. Main workflow steps (press enter on an empty line when done):")
    steps: List[str] = []
    step_num = 1
    while True:
        step = prompt_user(f"   Step {step_num}")
        if not step:
            break
        steps.append(step)
        step_num += 1

    # Q9: Author & License
    author = prompt_user("9. Author name or handle (optional)", default="")
    license_choice = prompt_user("10. License (MIT, Apache-2.0, Unlicense, none)", default="MIT")

    answers = {
        "problem": problem,
        "name": name,
        "description": description,
        "requires_scripts": requires_scripts,
        "template_family": template_family,
        "inputs": inputs_str,
        "outputs": outputs_str,
        "steps": steps,
        "author": author,
        "license": license_choice,
    }
    return build_spec_from_answers(answers)


def load_batch_answers(answers_path: Path) -> SkillSpec:
    """Load answers from a JSON file and construct a SkillSpec."""
    if not answers_path.exists():
        raise FileNotFoundError(f"Answers file not found: {answers_path}")
    data = json.loads(answers_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Answers file root must be a JSON object")
    return build_spec_from_answers(data)
