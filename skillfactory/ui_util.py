"""Terminal UI utilities and accessibility formatting (Phase 7, Task T7.04, AC7.04).

Enforces:
1. `NO_COLOR` standard compliance (https://no-color.org).
2. Elimination of color-only semantic signals (always accompanies color with text symbols).
3. 80-column terminal readability and word wrapping.
"""
from __future__ import annotations

import os
import re
import sys
import textwrap
from typing import Optional

# ANSI escape sequence remover
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def should_use_color() -> bool:
    """Determine whether ANSI colors should be enabled.

    Returns False if NO_COLOR environment variable is present,
    if TERM=dumb, or if output stream is not an interactive terminal.
    """
    if "NO_COLOR" in os.environ:
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


# Alias for compatibility
supports_color = should_use_color


def strip_ansi(text: str) -> str:
    """Remove all ANSI color and formatting escape codes from text."""
    return ANSI_ESCAPE_RE.sub("", text)


def colorize(arg1: str, arg2: str) -> str:
    """Apply ANSI color if colors are enabled, otherwise return plain text.

    Supports both (text, color_code) and (color_code, text) parameter orderings.
    """
    if arg1.isdigit():
        color_code, text = arg1, arg2
    else:
        text, color_code = arg1, arg2

    if not should_use_color():
        return text
    return f"\033[{color_code}m{text}\033[0m"


def format_status(status: str, message: str) -> str:
    """Format status with both semantic prefix and color (AC7.04).

    Never relies on color alone:
    - OK    -> [OK] (green if enabled)
    - WARN  -> [WARN] (yellow if enabled)
    - ERROR -> [ERROR] (red if enabled)
    - INFO  -> [INFO] (blue if enabled)
    """
    status_upper = status.upper()
    color_map = {
        "OK": "92",     # Green
        "WARN": "93",   # Yellow
        "ERROR": "91",  # Red
        "INFO": "94",   # Blue
    }

    raw_tag = f"[{status_upper}]"
    if should_use_color() and status_upper in color_map:
        tag = colorize(raw_tag, color_map[status_upper])
    else:
        tag = raw_tag

    return f"{tag} {message}"


# Alias for compatibility
format_msg = format_status


def wrap_text(text: str, width: int = 78, indent: str = "") -> str:
    """Wrap text to fit within standard 80-column terminal margins."""
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=indent)


def format_header(title: str, width: int = 74) -> str:
    """Format a clean header banner."""
    sep = "=" * width
    padding = max(0, (width - len(title) - 2) // 2)
    centered = f"{' ' * padding}{title}"
    return f"{sep}\n{centered}\n{sep}"


def format_box(text: str, title: Optional[str] = None, width: int = 74) -> str:
    """Format text inside a clean terminal border box."""
    lines = []
    top_border = f"+-- {title} {'-' * max(0, width - len(title or '') - 6)}+" if title else f"+{'-' * (width - 2)}+"
    bottom_border = f"+{'-' * (width - 2)}+"
    lines.append(top_border)
    for raw_line in text.splitlines():
        wrapped = textwrap.wrap(raw_line, width=width - 4) or [""]
        for w in wrapped:
            lines.append(f"| {w:<{width - 4}} |")
    lines.append(bottom_border)
    return "\n".join(lines)
