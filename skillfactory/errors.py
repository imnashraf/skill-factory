"""Beginner-friendly error modeling and remediation formatting (Phase 7, Task T7.02, AC7.02).

Eliminates raw Python stack traces for beginners by standardizing error reporting into:
1. What happened (clear description of the failure)
2. Why (the root cause or condition triggering it)
3. Next steps (concrete actions to resolve the problem)
"""
from __future__ import annotations

import traceback
from typing import Optional

from skillfactory.ui_util import format_status, wrap_text


class SkillFactoryError(Exception):
    """Base exception for all user-facing Skill Factory errors."""

    def __init__(
        self,
        message: str = "",
        why: Optional[str] = None,
        suggestion: Optional[str] = None,
        exit_code: int = 1,
        what: Optional[str] = None,
        next_step: Optional[str] = None,
        code: Optional[str] = None,
    ):
        msg = what or message
        super().__init__(msg)
        self.message = msg
        self.what = msg
        self.why = why
        self.suggestion = next_step or suggestion
        self.next_step = self.suggestion
        self.exit_code = exit_code
        self.code = code

    def format_user_message(self) -> str:
        """Render a 3-part structured message: What happened, Why it happened, and What to do next."""
        code_tag = f" [{self.code}]" if self.code else ""
        lines = [format_status("ERROR", f"{self.message}{code_tag}")]
        lines.append(f"  What happened: {self.message}")
        if self.why:
            lines.append(f"  Why it happened: {wrap_text(self.why, width=72, indent='')}")
        if self.suggestion:
            lines.append(f"  What to do next: {wrap_text(self.suggestion, width=72, indent='')}")
        return "\n".join(lines)


# Alias for compatibility
SkillFactoryUserError = SkillFactoryError


class SpecError(SkillFactoryError):
    """Raised when a skill specification violates Agent Skills rules."""

    def __init__(self, message: str, why: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            why=why or "The skill specification does not conform to the Agent Skills standard.",
            suggestion=suggestion or "Check the skill name, YAML frontmatter, and required files.",
            exit_code=2,
        )


class PlatformError(SkillFactoryError):
    """Raised when an AI platform discovery path or configuration fails."""

    def __init__(self, message: str, why: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            why=why or "The target AI platform was not found or is misconfigured.",
            suggestion=suggestion or "Run 'python3 -m skillfactory doctor' to verify detected platform paths.",
            exit_code=1,
        )


class InstallError(SkillFactoryError):
    """Raised when installation, update, or uninstall cannot proceed safely."""

    def __init__(self, message: str, why: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            why=why or "An existing folder, collision, or permission issue prevented installation.",
            suggestion=suggestion or "Use --force to overwrite or specify a different target directory.",
            exit_code=1,
        )


class PackageError(SkillFactoryError):
    """Raised when packaging, exporting, or importing encounters safety violations."""

    def __init__(self, message: str, why: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            why=why or "The archive contains path traversal (Zip-Slip) or failed hash checks.",
            suggestion=suggestion or "Only import trusted archives and verify SHA-256 checksums.",
            exit_code=1,
        )


def format_error(error: Exception, debug: bool = False) -> str:
    """Format any exception cleanly without raw tracebacks unless debug is enabled (AC7.02)."""
    if debug:
        return "".join(traceback.format_exception(type(error), error, error.__traceback__))

    if isinstance(error, SkillFactoryError):
        return error.format_user_message()

    # Generic unexpected exception formatting
    err_type = type(error).__name__
    msg = str(error) or err_type
    why = f"An unexpected {err_type} occurred during command execution."
    next_step = "Run with --debug for technical stack trace, or report an issue on GitHub."

    lines = [
        format_status("ERROR", msg),
        f"  Why:  {why}",
        f"  Next: {next_step}",
    ]
    return "\n".join(lines)
