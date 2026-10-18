#!/usr/bin/env python3
"""Offline, standard-library-only Agent Skill scaffold generator (Legacy Compatibility Wrapper)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path so scripts/ can run standalone
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from skillfactory.core import create_scaffold
from skillfactory.spec import SkillSpec, SpecValidationError


def create(name: str, description: str, destination: Path) -> Path:
    """Create a new skill scaffold. Preserves identical signature and error types."""
    if '\n' in description:
        raise ValueError('Description must be one nonempty line of at most 1024 characters')

    try:
        return create_scaffold(name, description, destination)
    except SpecValidationError as err:
        raise ValueError(str(err)) from err


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Create a free offline Agent Skill scaffold")
    parser.add_argument("--name", required=True, help="Skill name (lowercase kebab-case)")
    parser.add_argument("--description", required=True, help="Skill description")
    parser.add_argument("--output", default="generated-skills", help="Output directory")
    args = parser.parse_args(argv)

    try:
        path = create(args.name, args.description, Path(args.output))
        print(f"Created scaffold: {path}")
    except (ValueError, FileExistsError) as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
