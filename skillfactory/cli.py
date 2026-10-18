"""Skill Factory CLI Dispatcher (Phase 1, Task T1.08).

Implements commands: new, validate, version.
Supports --dry-run, --json, and standardized exit codes (0, 1, 2, 3).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from skillfactory import __version__
from skillfactory.core import generate_skill
from skillfactory.spec import VALID_TEMPLATE_FAMILIES, SkillSpec, SpecValidationError
from skillfactory.validator import validate_skill


def use_color() -> bool:
    """Determine whether color output should be enabled."""
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def format_msg(status: str, msg: str) -> str:
    """Format messages with consistent [OK], [WARN], [ERROR] tags."""
    if use_color():
        colors = {
            "OK": "\033[92m[OK]\033[0m",
            "WARN": "\033[93m[WARN]\033[0m",
            "ERROR": "\033[91m[ERROR]\033[0m",
            "INFO": "\033[94m[INFO]\033[0m",
        }
        tag = colors.get(status, f"[{status}]")
    else:
        tag = f"[{status}]"
    return f"{tag} {msg}"


def cmd_new(args: argparse.Namespace) -> int:
    """Handle `skillfactory new` command."""
    try:
        if args.spec:
            spec_path = Path(args.spec)
            if not spec_path.exists():
                print(format_msg("ERROR", f"Spec file not found: {spec_path}"), file=sys.stderr)
                return 1
            spec = SkillSpec.from_json(spec_path.read_text(encoding="utf-8"))
        else:
            if not args.name or not args.description:
                print(
                    format_msg(
                        "ERROR",
                        "Both --name and --description are required when not using --spec."
                    ),
                    file=sys.stderr,
                )
                return 2
            spec = SkillSpec(
                name=args.name,
                description=args.description,
                template_family=args.template,
                license=args.license,
                author=args.author or "",
            )

        output_dir = Path(args.output)
        result = generate_skill(spec, output_dir, dry_run=args.dry_run)

        if args.json:
            print(
                json.dumps(
                    {
                        "status": "success",
                        "skill_name": result.skill_name,
                        "target_path": str(result.target_path),
                        "dry_run": result.dry_run,
                        "files": result.written_files,
                    },
                    indent=2,
                )
            )
        else:
            if result.dry_run:
                print(format_msg("INFO", f"Dry run: {len(result.written_files)} files would be generated at {result.target_path}"))
                for f in result.written_files:
                    print(f"  - {f}")
            else:
                print(format_msg("OK", f"Created skill '{result.skill_name}' at {result.target_path}"))
                print(f"Files created ({len(result.written_files)}):")
                for f in result.written_files:
                    print(f"  - {f}")
        return 0

    except SpecValidationError as err:
        if args.json:
            print(json.dumps({"status": "error", "errors": err.errors}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", "Specification validation failed:"), file=sys.stderr)
            for e in err.errors:
                print(f"  - {e}", file=sys.stderr)
        return 1

    except FileExistsError as err:
        if args.json:
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", str(err)), file=sys.stderr)
        return 1

    except PermissionError as err:
        if args.json:
            print(json.dumps({"status": "environment_error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", f"Permission denied: {err}"), file=sys.stderr)
        return 3

    except Exception as err:
        if args.json:
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", f"Unexpected error: {err}"), file=sys.stderr)
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Handle `skillfactory validate` command."""
    target_path = Path(args.path)
    val_result = validate_skill(target_path, verify_hashes=not args.no_hashes)

    if args.record and val_result.is_valid:
        meta_dir = target_path / ".skillfactory"
        meta_dir.mkdir(parents=True, exist_ok=True)
        rec_file = meta_dir / "validation.json"
        rec_file.write_text(
            json.dumps(val_result.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(val_result.to_dict(), indent=2))
        return 0 if val_result.is_valid else 1

    if val_result.is_valid:
        print(format_msg("OK", f"Skill '{val_result.skill_name}' is valid Agent Skills specification."))
        for w in val_result.warnings:
            print(format_msg("WARN", w))
        return 0
    else:
        print(format_msg("ERROR", f"Validation failed for '{target_path}':"), file=sys.stderr)
        for e in val_result.errors:
            print(f"  - {e}", file=sys.stderr)
        for w in val_result.warnings:
            print(format_msg("WARN", w))
        return 1


def cmd_interview(args: argparse.Namespace) -> int:
    """Handle `skillfactory interview` command (offline guided creation / batch answers)."""
    from skillfactory.interview import load_batch_answers, run_interactive_interview

    try:
        if args.answers:
            answers_path = Path(args.answers)
            spec = load_batch_answers(answers_path)
        else:
            spec = run_interactive_interview()

        output_dir = Path(args.output)

        if args.spec_only:
            spec_file = output_dir / f"{spec.name}-spec.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            spec_file.write_text(spec.to_json(), encoding="utf-8")
            if args.json:
                print(json.dumps({"status": "success", "spec_file": str(spec_file)}, indent=2))
            else:
                print(format_msg("OK", f"Specification written to {spec_file}"))
            return 0

        result = generate_skill(spec, output_dir, dry_run=args.dry_run)

        if args.json:
            print(
                json.dumps(
                    {
                        "status": "success",
                        "skill_name": result.skill_name,
                        "target_path": str(result.target_path),
                        "dry_run": result.dry_run,
                        "files": result.written_files,
                    },
                    indent=2,
                )
            )
        else:
            if result.dry_run:
                print(
                    format_msg(
                        "INFO",
                        f"Dry run: {len(result.written_files)} files would be created at {result.target_path}",
                    )
                )
                for f in result.written_files:
                    print(f"  - {f}")
            else:
                print(format_msg("OK", f"Successfully created '{result.skill_name}' at {result.target_path}"))
                print(f"Files created ({len(result.written_files)}):")
                for f in result.written_files:
                    print(f"  - {f}")
        return 0

    except Exception as err:
        if args.json:
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", str(err)), file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser."""
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    common_parser.add_argument("--dry-run", action="store_true", help="Simulate execution without modifying files")

    parser = argparse.ArgumentParser(
        prog="skillfactory",
        description="Skill Factory — Free, open-source Agent Skills generation and management.",
        parents=[common_parser],
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: new
    new_parser = subparsers.add_parser("new", parents=[common_parser], help="Create a new Agent Skill")
    new_parser.add_argument("--name", help="Skill name (lowercase kebab-case)")
    new_parser.add_argument("--description", help="What the skill does (1-1024 characters)")
    new_parser.add_argument(
        "--template",
        default="python-script",
        choices=sorted(VALID_TEMPLATE_FAMILIES),
        help="Template family (default: python-script)",
    )
    new_parser.add_argument("--output", default="generated-skills", help="Destination folder (default: generated-skills)")
    new_parser.add_argument("--spec", help="Path to input skill-spec.json file")
    new_parser.add_argument("--license", default="MIT", help="License (MIT, Apache-2.0, Unlicense, none)")
    new_parser.add_argument("--author", default="", help="Author name")

    # Command: interview
    interview_parser = subparsers.add_parser(
        "interview",
        parents=[common_parser],
        help="Guided interactive interview or batch creation without an AI model",
    )
    interview_parser.add_argument("--answers", help="Path to JSON file with batch answers")
    interview_parser.add_argument("--output", default="generated-skills", help="Destination folder (default: generated-skills)")
    interview_parser.add_argument("--spec-only", action="store_true", help="Only generate the spec JSON file")

    # Command: validate
    val_parser = subparsers.add_parser("validate", parents=[common_parser], help="Validate an Agent Skill directory")
    val_parser.add_argument("path", help="Path to the skill directory")
    val_parser.add_argument("--no-hashes", action="store_true", help="Skip manifest hash verification")
    val_parser.add_argument("--record", action="store_true", help="Record results to .skillfactory/validation.json")

    # Command: version
    subparsers.add_parser("version", help="Show Skill Factory version")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "new":
        return cmd_new(args)
    elif args.command == "interview":
        return cmd_interview(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "version":
        print(f"skillfactory {__version__}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
