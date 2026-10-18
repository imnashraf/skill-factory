"""Deterministic keyword heuristic template router (Phase 2, Task T2.04).

Selects the most appropriate Agent Skill template family based on user intent and problem description.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

FILE_TRANSFORM_KEYWORDS = {
    "convert", "converter", "transform", "transformer", "parse", "parser",
    "extract", "extractor", "csv", "json", "yaml", "xml", "excel", "pdf",
    "tsv", "html", "markdown", "format", "formatter", "compress", "resize",
    "clean data", "migrate", "transpile", "export", "import data",
}

CHECKLIST_REVIEW_KEYWORDS = {
    "checklist", "review", "reviewer", "audit", "auditor", "inspect",
    "inspector", "compliance", "verify", "verification", "check", "checker",
    "pr review", "code review", "assessment", "guidelines", "lint", "linter",
    "quality check", "security review", "standards",
}

WORKFLOW_RUNBOOK_KEYWORDS = {
    "deploy", "deployment", "incident", "runbook", "step-by-step", "release",
    "procedure", "recovery", "operations", "devops", "setup environment",
    "troubleshoot", "playbook", "disaster recovery", "rollback", "migration runbook",
    "onboarding", "maintenance",
}

INSTRUCTIONS_ONLY_KEYWORDS = {
    "prompt", "instructions", "guide", "guidelines", "writing", "brainstorm",
    "draft", "explain", "explanation", "advice", "tutor", "coaching",
    "interview prep", "documentation style", "copywriting", "summary",
}

PYTHON_SCRIPT_KEYWORDS = {
    "script", "automate", "automation", "tool", "cli", "algorithm",
    "calculate", "calculator", "fetch", "fetcher", "scrape", "scraper",
    "crawler", "api", "client", "sdk", "subprocess", "benchmark",
}


def _tokenize(text: str) -> set[str]:
    """Extract lowercased alphanumeric words and 2-word phrases from text."""
    lower = text.lower()
    words = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", lower)
    tokens = set(words)
    # Add bigrams for phrases like 'code review', 'clean data'
    for i in range(len(words) - 1):
        tokens.add(f"{words[i]} {words[i+1]}")
    return tokens


def route_template(
    description: str,
    requires_scripts: Optional[bool] = None,
) -> Tuple[str, str]:
    """Determine the optimal template family for a skill based on description keywords.

    Args:
        description: Plain-language problem or skill description.
        requires_scripts: Explicit user preference for executable code (True/False/None).

    Returns:
        (template_family, reason)
    """
    tokens = _tokenize(description)

    # 1. Instructions Only (check if strong instruction keywords like prompt, writing, draft are present)
    if requires_scripts is False:
        return (
            "instructions-only",
            "User specified no custom executable scripts are required.",
        )

    instruction_matches = tokens & INSTRUCTIONS_ONLY_KEYWORDS
    if instruction_matches and not (tokens & FILE_TRANSFORM_KEYWORDS) and not (tokens & WORKFLOW_RUNBOOK_KEYWORDS) and requires_scripts is not True:
        # If it contains prompt or writing or drafting without script keywords, choose instructions-only
        if tokens & {"prompt", "writing", "draft", "brainstorm", "explain"}:
            matched = ", ".join(sorted(instruction_matches)[:3])
            return (
                "instructions-only",
                f"Detected advisory/instructions-only keywords ({matched}).",
            )

    # 2. Checklist / Review
    checklist_matches = tokens & CHECKLIST_REVIEW_KEYWORDS
    if checklist_matches:
        matched = ", ".join(sorted(checklist_matches)[:3])
        return (
            "checklist-review",
            f"Detected verification/review keywords ({matched}).",
        )

    # 2. File Transform / Parsing
    transform_matches = tokens & FILE_TRANSFORM_KEYWORDS
    if transform_matches:
        matched = ", ".join(sorted(transform_matches)[:3])
        return (
            "file-transform",
            f"Detected data transformation/file conversion keywords ({matched}).",
        )

    # 3. Workflow Runbook
    runbook_matches = tokens & WORKFLOW_RUNBOOK_KEYWORDS
    if runbook_matches:
        matched = ", ".join(sorted(runbook_matches)[:3])
        return (
            "workflow-runbook",
            f"Detected operational procedure/runbook keywords ({matched}).",
        )

    # 4. Instructions Only
    if requires_scripts is False:
        return (
            "instructions-only",
            "User specified no custom executable scripts are required.",
        )

    instruction_matches = tokens & INSTRUCTIONS_ONLY_KEYWORDS
    if instruction_matches and requires_scripts is not True:
        matched = ", ".join(sorted(instruction_matches)[:3])
        return (
            "instructions-only",
            f"Detected advisory/instructions-only keywords ({matched}).",
        )

    # 5. Python Script Automation
    script_matches = tokens & PYTHON_SCRIPT_KEYWORDS
    if script_matches:
        matched = ", ".join(sorted(script_matches)[:3])
        return (
            "python-script",
            f"Detected scripting/automation keywords ({matched}).",
        )

    # Default fallback
    if requires_scripts is True:
        return (
            "python-script",
            "Executable script requested by user.",
        )

    return (
        "python-script",
        "Defaulting to standard executable python-script scaffold.",
    )
