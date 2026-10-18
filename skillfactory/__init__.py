"""Skill Factory - Free, open-source Agent Skills generation and management."""
from __future__ import annotations

import sys

__version__ = "1.0.0"
__author__ = "Skill Factory Contributors"
MIN_PYTHON_VERSION = (3, 9)

if sys.version_info < MIN_PYTHON_VERSION:
    sys.stderr.write(
        f"Skill Factory requires Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or newer. "
        f"You are running Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.\n"
    )
    sys.exit(3)
