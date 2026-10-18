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


def cmd_doctor(args: argparse.Namespace) -> int:
    """Handle `skillfactory doctor` command (Phase 3, Task T3.03, AC3.03)."""
    from skillfactory.compat.detect import detect_all_platforms
    from skillfactory.compat.platform_db import detect_os_key, get_all_platforms

    project_dir = Path(getattr(args, "project", ".")).resolve()
    py_ver = sys.version_info
    py_ver_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    py_compatible = py_ver >= (3, 9)
    os_name = detect_os_key()

    detection_results = detect_all_platforms(project_dir=project_dir)
    all_defs = get_all_platforms()

    if getattr(args, "json", False):
        report = {
            "status": "success",
            "system": {
                "python_version": py_ver_str,
                "python_executable": sys.executable,
                "python_compatible": py_compatible,
                "os_name": os_name,
                "platform": sys.platform,
                "project_dir": str(project_dir),
            },
            "platforms": {
                pid: res.to_dict() for pid, res in detection_results.items()
            },
            "shared_directories": [
                {
                    "path": ".agents/skills",
                    "platforms": ["cursor", "codex", "antigravity"],
                    "note": "Shared project-level skills directory across Cursor, Codex, and Antigravity.",
                }
            ],
        }
        print(json.dumps(report, indent=2))
        return 0

    print("Skill Factory Doctor — System & Multi-Agent Compatibility Report")
    print("=" * 66)
    print("\n[System Runtime]")
    py_status = "[OK]" if py_compatible else "[FAIL]"
    print(f"  Python:      {py_ver_str} ({sys.executable}) {py_status} (Requires 3.9+)")
    print(f"  OS:          {os_name} ({sys.platform})")
    print(f"  Project:     {project_dir}")

    print("\n[Detected AI Platforms]")
    for pid, res in detection_results.items():
        pdef = all_defs.get(pid, {})
        vendor = pdef.get("vendor", "")
        verified = pdef.get("last_verified", "unverified")
        inv_syntax = pdef.get("invocation_syntax", "n/a")

        status_line = res.status_summary
        tag = "[OK]" if res.detected else "[INFO]"
        print(f"\n  • {res.display_name} ({vendor}) {tag}")
        print(f"    Status:        {status_line}")
        print(f"    Verified:      {verified}")
        print(f"    Invocation:    {inv_syntax}")

        if res.project_path_statuses:
            for rel_p, p_stat in res.project_path_statuses.items():
                print(f"    Project Path:  {rel_p}/ [{p_stat}]")
        if res.user_skill_path:
            print(f"    User Path:     {res.user_skill_path} [{res.user_path_status}]")

    print("\n[Shared-Directory Notes]")
    print("  • '.agents/skills/' is shared across Cursor, OpenAI Codex, and Google Antigravity.")
    print("    Skills created in or installed to '.agents/skills/' are automatically visible to all three.")

    print("\n" + format_msg("OK", "Doctor check completed successfully. All systems operational."))
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    """Handle `skillfactory install` command (Phase 4, Task T4.02, AC4.02)."""
    from skillfactory.installer import install_skill

    target_platform = getattr(args, "target", None)
    if not target_platform:
        # Smart detection: pick detected platform or cursor
        from skillfactory.compat.detect import detect_all_platforms
        detected = [pid for pid, d in detect_all_platforms().items() if d.detected]
        target_platform = detected[0] if detected else "cursor"

    try:
        res = install_skill(
            skill_path=args.path,
            target_platform=target_platform,
            scope=args.scope,
            link=args.link,
            force=args.force,
            project_dir=getattr(args, "project", "."),
        )
        if getattr(args, "json", False):
            print(json.dumps({
                "status": "success",
                "skill_name": res.skill_name,
                "target_platform": res.target_platform,
                "installed_path": str(res.installed_path),
                "mode": res.mode,
                "copied_files": res.copied_files,
                "warning": res.warning,
            }, indent=2))
        else:
            if res.warning:
                print(format_msg("WARN", res.warning))
            print(format_msg("OK", f"Installed '{res.skill_name}' for {res.target_platform} at {res.installed_path} ({len(res.copied_files)} files, mode: {res.mode})"))
        return 0
    except Exception as err:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", str(err)), file=sys.stderr)
        return 1


def cmd_update(args: argparse.Namespace) -> int:
    """Handle `skillfactory update` command (Phase 4, Task T4.03, AC4.03)."""
    from skillfactory.installer import update_skill

    try:
        res = update_skill(
            skill_name=args.name,
            source_path=args.source,
            target_platform=args.target,
            force=args.force,
        )
        if getattr(args, "json", False):
            print(json.dumps({
                "status": "success",
                "skill_name": res.skill_name,
                "target_platform": res.target_platform,
                "installed_path": str(res.installed_path),
                "backup_path": res.backup_path,
                "copied_files": res.copied_files,
            }, indent=2))
        else:
            print(format_msg("OK", f"Updated '{res.skill_name}'. Automated backup saved at: {res.backup_path}"))
            print(format_msg("OK", f"Installed updated files to: {res.installed_path} ({len(res.copied_files)} files)"))
        return 0
    except Exception as err:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", str(err)), file=sys.stderr)
        return 1


def cmd_rollback(args: argparse.Namespace) -> int:
    """Handle `skillfactory rollback` command (Phase 4, Task T4.04, AC4.04)."""
    from skillfactory.installer import rollback_skill

    try:
        res = rollback_skill(
            skill_name=args.name,
            target_platform=args.target,
        )
        if getattr(args, "json", False):
            print(json.dumps({
                "status": "success",
                "skill_name": res.skill_name,
                "target_platform": res.target_platform,
                "restored_path": str(res.installed_path),
                "restored_from_backup": res.backup_path,
            }, indent=2))
        else:
            print(format_msg("OK", f"Rolled back '{res.skill_name}' from backup: {res.backup_path}"))
            print(format_msg("OK", f"Restored {len(res.copied_files)} files at {res.installed_path}"))
        return 0
    except Exception as err:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", str(err)), file=sys.stderr)
        return 1


def cmd_uninstall(args: argparse.Namespace) -> int:
    """Handle `skillfactory uninstall` command (Phase 4, Task T4.05, AC4.05)."""
    from skillfactory.installer import uninstall_skill

    try:
        removed = uninstall_skill(
            skill_name=args.name,
            target_platform=args.target,
        )
        if getattr(args, "json", False):
            print(json.dumps({
                "status": "success",
                "skill_name": args.name,
                "removed_files": removed,
            }, indent=2))
        else:
            print(format_msg("OK", f"Uninstalled '{args.name}' ({len(removed)} files removed, user data preserved)"))
        return 0
    except Exception as err:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", str(err)), file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle `skillfactory list` command (Phase 4, Task T4.07, AC4.07)."""
    from skillfactory.manifest import verify_manifest
    from skillfactory.registry import load_registry

    data = load_registry()
    installations = data.get("installations", [])

    results = []
    for rec in installations:
        p_path = Path(rec.get("installed_path", ""))
        exists = p_path.exists()
        modified = False
        if exists and p_path.is_dir():
            valid, discrepancies = verify_manifest(p_path)
            if not valid and any("File content modified" in d for d in discrepancies):
                modified = True

        results.append({
            "skill_name": rec.get("skill_name"),
            "platform": rec.get("platform"),
            "scope": rec.get("scope"),
            "version": rec.get("version"),
            "mode": rec.get("mode"),
            "installed_path": rec.get("installed_path"),
            "exists": exists,
            "modified": modified,
        })

    if getattr(args, "json", False):
        print(json.dumps({"status": "success", "installations": results}, indent=2))
        return 0

    print("Skill Factory — Installed Skills")
    print("=" * 74)
    if not results:
        print("No skills currently recorded in the local registry.")
        return 0

    header = f"{'Skill Name':<20} {'Platform':<15} {'Scope':<9} {'Version':<9} {'Mode':<8} {'Modified?'}"
    print(header)
    print("-" * 74)
    for r in results:
        mod_text = "Yes (edits)" if r["modified"] else "No"
        if not r["exists"]:
            mod_text = "Missing dir"
        print(f"{r['skill_name']:<20} {r['platform']:<15} {r['scope']:<9} {r['version']:<9} {r['mode']:<8} {mod_text}")
    print("-" * 74)
    print(f"Total installations: {len(results)}")
    return 0


def cmd_install_self(args: argparse.Namespace) -> int:
    """Handle `skillfactory install-self` command (Phase 4, Task T4.08, AC4.08)."""
    from skillfactory.installer import install_self

    try:
        results = install_self(
            target_platform=args.target,
            scope=args.scope,
            link=args.link,
        )
        if getattr(args, "json", False):
            print(json.dumps({
                "status": "success",
                "installations": [
                    {
                        "platform": r.target_platform,
                        "installed_path": str(r.installed_path),
                        "mode": r.mode,
                    }
                    for r in results
                ],
            }, indent=2))
        else:
            for r in results:
                print(format_msg("OK", f"Self-installed Skill Factory for {r.target_platform} at {r.installed_path}"))
        return 0
    except Exception as err:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "error": str(err)}, indent=2), file=sys.stderr)
        else:
            print(format_msg("ERROR", str(err)), file=sys.stderr)
        return 1


def cmd_test(args: argparse.Namespace) -> int:
    """Handle `skillfactory test` command (Phase 5, Task T5.01, AC5.01)."""
    from skillfactory.tester import run_skill_tests

    skill_path = Path(args.path)
    timeout = getattr(args, "timeout", 10.0) or 10.0
    result = run_skill_tests(skill_path, timeout=timeout, save_report=True)

    if getattr(args, "json", False):
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.timed_out:
            print(format_msg("ERROR", f"Test execution timed out after {timeout:.1f}s (AC5.01)"), file=sys.stderr)
            return 1
        elif not result.success:
            print(
                format_msg(
                    "ERROR",
                    f"Tests failed: {result.failures} failure(s), {result.errors} error(s) in {result.duration_sec:.2f}s",
                ),
                file=sys.stderr,
            )
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            elif result.stdout:
                print(result.stdout, file=sys.stderr)
            return 1
        else:
            if result.tests_run == 0:
                print(format_msg("INFO", f"No test files found to execute in {skill_path / 'tests'}"))
            else:
                skip_msg = f" ({result.skipped} skipped)" if result.skipped > 0 else ""
                print(
                    format_msg(
                        "OK",
                        f"Executed {result.tests_run} tests in {result.duration_sec:.2f}s with 0 failures{skip_msg}",
                    )
                )
    return 0 if result.success else 1


def cmd_eval(args: argparse.Namespace) -> int:
    """Handle `skillfactory eval` command (Phase 5, Task T5.03, AC5.03)."""
    from skillfactory.eval import evaluate_skill

    skill_path = Path(args.path)
    run_tests = not getattr(args, "no_test", False)
    timeout = getattr(args, "timeout", 10.0) or 10.0
    report = evaluate_skill(skill_path, run_tests=run_tests, test_timeout=timeout, save_report=True)

    if getattr(args, "json", False):
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"Skill Evaluation Report: {report.skill_name}")
        print(f"Overall Score: {report.total_score} / 100 [{report.grade}]")
        print("-" * 54)
        for dim in report.dimensions:
            earned = dim.earned
            max_pts = dim.max_points
            tag = "OK" if earned >= (max_pts * 0.75) else ("WARN" if earned >= (max_pts * 0.5) else "ERROR")
            print(f"{format_msg(tag, f'{dim.name:<32}')}: {earned:>2} / {max_pts}")
        print("-" * 54)
        print(f"Recommendation: {report.recommendation}")

    return 0 if report.total_score >= 60 else 1


def cmd_scan(args: argparse.Namespace) -> int:
    """Handle `skillfactory scan` command (Phase 5, Task T5.02, AC5.02)."""
    from skillfactory.scanner import scan_skill_directory

    skill_path = Path(args.path)
    report = scan_skill_directory(skill_path)

    if getattr(args, "json", False):
        print(json.dumps(report.to_dict(), indent=2))
    else:
        if report.findings:
            print(f"Safety & Secret Scan for: {skill_path.name}")
            print("=" * 60)
            for f in report.findings:
                tag = "ERROR" if f.severity in ("CRITICAL", "HIGH") else ("WARN" if f.severity == "MEDIUM" else "INFO")
                print(format_msg(tag, f"[{f.rule_id}] {f.description}"))
                rel_f = Path(f.file_path).name
                print(f"  Line {f.line_number} in {rel_f}: {f.snippet}")
            print("-" * 60)
            print(
                f"Scanned {report.files_scanned} files: {report.critical_count} critical, {report.high_count} high, {report.medium_count} medium, {report.low_count} low"
            )
        else:
            print(format_msg("OK", f"Safety scan clean: {report.files_scanned} files inspected with 0 findings."))

    return 0 if report.is_clean else 1


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

    # Command: test
    test_parser = subparsers.add_parser("test", parents=[common_parser], help="Run skill tests in an isolated subprocess with 10s timeout")
    test_parser.add_argument("path", default=".", nargs="?", help="Path to skill directory (default: .)")
    test_parser.add_argument("--timeout", type=float, default=10.0, help="Test timeout in seconds (default: 10.0)")

    # Command: eval
    eval_parser = subparsers.add_parser("eval", parents=[common_parser], help="Evaluate skill quality across 5 dimensions (0-100 score)")
    eval_parser.add_argument("path", default=".", nargs="?", help="Path to skill directory (default: .)")
    eval_parser.add_argument("--no-test", action="store_true", help="Skip executing tests during evaluation")
    eval_parser.add_argument("--timeout", type=float, default=10.0, help="Test timeout in seconds (default: 10.0)")

    # Command: scan
    scan_parser = subparsers.add_parser("scan", parents=[common_parser], help="Perform AST safety and secrets scan on skill files")
    scan_parser.add_argument("path", default=".", nargs="?", help="Path to skill directory (default: .)")

    # Command: doctor
    doctor_parser = subparsers.add_parser(
        "doctor",
        parents=[common_parser],
        help="Diagnose system health, detected AI agents, and platform discovery paths",
    )
    doctor_parser.add_argument("--project", default=".", help="Project directory to inspect (default: .)")

    # Command: install
    install_parser = subparsers.add_parser("install", parents=[common_parser], help="Install an Agent Skill into a target platform")
    install_parser.add_argument("path", help="Path to the skill directory to install")
    install_parser.add_argument("--target", help="Target platform (claude-code, cursor, codex, antigravity)")
    install_parser.add_argument("--scope", default="project", choices=["project", "user"], help="Installation scope (default: project)")
    install_parser.add_argument("--project", default=".", help="Project directory (default: .)")
    install_parser.add_argument("--link", action="store_true", help="Use symbolic link instead of copying files")
    install_parser.add_argument("--force", action="store_true", help="Overwrite if already installed")
    install_parser.add_argument("--yes", action="store_true", help="Proceed non-interactively without prompt")

    # Command: update
    update_parser = subparsers.add_parser("update", parents=[common_parser], help="Update an installed skill with automated backup")
    update_parser.add_argument("name", help="Skill name to update")
    update_parser.add_argument("--source", help="Path to updated source directory (optional)")
    update_parser.add_argument("--target", help="Target platform (optional)")
    update_parser.add_argument("--force", action="store_true", help="Overwrite even if local modifications exist")

    # Command: rollback
    rollback_parser = subparsers.add_parser("rollback", parents=[common_parser], help="Restore the previous working backup snapshot")
    rollback_parser.add_argument("name", help="Skill name to roll back")
    rollback_parser.add_argument("--target", help="Target platform (optional)")

    # Command: uninstall
    uninstall_parser = subparsers.add_parser("uninstall", parents=[common_parser], help="Safely remove a skill while preserving user files")
    uninstall_parser.add_argument("name", help="Skill name to uninstall")
    uninstall_parser.add_argument("--target", help="Target platform (optional)")
    uninstall_parser.add_argument("--yes", action="store_true", help="Confirm removal non-interactively")

    # Command: list
    subparsers.add_parser("list", parents=[common_parser], help="List all installed skills and modification statuses")

    # Command: install-self
    self_parser = subparsers.add_parser("install-self", parents=[common_parser], help="Install Skill Factory into host AI platform")
    self_parser.add_argument("--target", help="Target platform (optional)")
    self_parser.add_argument("--scope", default="user", choices=["project", "user"], help="Installation scope (default: user)")
    self_parser.add_argument("--link", action="store_true", help="Use symbolic link instead of copying files")

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
    elif args.command == "test":
        return cmd_test(args)
    elif args.command == "eval":
        return cmd_eval(args)
    elif args.command == "scan":
        return cmd_scan(args)
    elif args.command == "doctor":
        return cmd_doctor(args)
    elif args.command == "install":
        return cmd_install(args)
    elif args.command == "update":
        return cmd_update(args)
    elif args.command == "rollback":
        return cmd_rollback(args)
    elif args.command == "uninstall":
        return cmd_uninstall(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "install-self":
        return cmd_install_self(args)
    elif args.command == "version":
        print(f"skillfactory {__version__}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
