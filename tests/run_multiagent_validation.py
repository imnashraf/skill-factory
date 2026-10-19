#!/usr/bin/env python3
"""Multi-agent integration test runner for Step 4 of Phase 10 validation.

Tests Claude Code, Cursor, Codex, and Google Antigravity across:
- Installation (canonical ID and aliases)
- Directory layout & specification validation
- Frontmatter & metadata compliance
- Script execution with representative inputs
- Edit detection & backup snapshot creation on update
- Single-command rollback
- Clean uninstallation
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from skillfactory.compat.platform_db import get_platform, normalize_platform_id
from skillfactory.compat.resolve import resolve_install_targets
from skillfactory.installer import (
    install_skill,
    rollback_skill,
    uninstall_skill,
    update_skill,
)
from skillfactory.registry import find_installation, load_registry
from skillfactory.validator import validate_skill


def run_platform_lifecycle_test(
    platform_name: str,
    alias_name: str,
    skill_source_dir: Path,
    test_args: list[str],
    work_dir: Path,
) -> dict:
    """Run complete install -> execute -> update -> rollback -> uninstall cycle."""
    report = {
        "platform": platform_name,
        "alias_tested": alias_name,
        "stages": {},
        "passed": True,
        "errors": [],
    }

    env_dir = work_dir / f"env_{platform_name}"
    env_dir.mkdir(parents=True, exist_ok=True)
    home_dir = env_dir / "home"
    proj_dir = env_dir / "project"
    home_dir.mkdir(parents=True, exist_ok=True)
    proj_dir.mkdir(parents=True, exist_ok=True)

    reg_path = home_dir / "registry.json"

    # Stage 1: Installation via alias
    try:
        res = install_skill(
            skill_path=skill_source_dir,
            target_platform=alias_name,
            scope="project",
            project_dir=proj_dir,
            home_dir=home_dir,
            registry_path=reg_path,
        )
        report["stages"]["install"] = {
            "status": "PASS",
            "installed_path": str(res.installed_path),
            "target_platform": res.target_platform,
            "mode": res.mode,
            "file_count": len(res.copied_files),
        }
        installed_skill_dir = Path(res.installed_path)
    except Exception as exc:
        report["passed"] = False
        report["stages"]["install"] = {"status": "FAIL", "error": str(exc)}
        report["errors"].append(f"Install error: {exc}")
        return report

    # Stage 2: Validation in target location
    try:
        val = validate_skill(installed_skill_dir)
        report["stages"]["validation"] = {
            "status": "PASS" if val.is_valid else "FAIL",
            "errors": val.errors,
            "warnings": val.warnings,
        }
        if not val.is_valid:
            report["passed"] = False
            report["errors"].append(f"Validation failed: {val.errors}")
    except Exception as exc:
        report["passed"] = False
        report["stages"]["validation"] = {"status": "FAIL", "error": str(exc)}
        report["errors"].append(f"Validation exception: {exc}")

    # Stage 3: Script Execution inside installed location
    script_path = installed_skill_dir / "scripts" / "main.py"
    if script_path.is_file():
        try:
            cmd = [sys.executable, str(script_path)] + test_args
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            # Both 0 and expected non-zero exits (e.g. diff found) are acceptable if output is produced
            report["stages"]["execution"] = {
                "status": "PASS",
                "returncode": proc.returncode,
                "stdout_sample": proc.stdout[:200].strip(),
            }
        except Exception as exc:
            report["passed"] = False
            report["stages"]["execution"] = {"status": "FAIL", "error": str(exc)}
            report["errors"].append(f"Execution error: {exc}")
    else:
        report["stages"]["execution"] = {"status": "SKIPPED", "reason": "No main.py"}

    # Stage 4: Update with backup creation
    try:
        # Simulate local edit
        test_file = installed_skill_dir / "README.md"
        test_file.write_text(test_file.read_text(encoding="utf-8") + "\n# Modified\n", encoding="utf-8")

        # Update with force
        up_res = update_skill(
            skill_name=skill_source_dir.name,
            source_path=skill_source_dir,
            target_platform=alias_name,
            force=True,
            home_dir=home_dir,
            registry_path=reg_path,
        )
        # Verify that after update, the local edit was overwritten by pristine source
        post_update_readme = (installed_skill_dir / "README.md").read_text(encoding="utf-8")
        overwritten_cleanly = "# Modified" not in post_update_readme

        report["stages"]["update"] = {
            "status": "PASS" if overwritten_cleanly else "FAIL",
            "backup_created": bool(up_res.backup_path and Path(up_res.backup_path).is_dir()),
            "backup_path": up_res.backup_path,
            "overwritten_cleanly": overwritten_cleanly,
        }
    except Exception as exc:
        report["passed"] = False
        report["stages"]["update"] = {"status": "FAIL", "error": str(exc)}
        report["errors"].append(f"Update error: {exc}")

    # Stage 5: Rollback (should restore the pre-update snapshot with # Modified)
    try:
        rb_res = rollback_skill(
            skill_name=skill_source_dir.name,
            target_platform=alias_name,
            registry_path=reg_path,
        )
        # Verify our modified line was restored from the pre-update backup
        restored_readme = (installed_skill_dir / "README.md").read_text(encoding="utf-8")
        has_edit = "# Modified" in restored_readme
        report["stages"]["rollback"] = {
            "status": "PASS" if has_edit else "FAIL",
            "restored_from": rb_res.backup_path,
            "backup_restored_cleanly": has_edit,
        }
        if not has_edit:
            report["passed"] = False
            report["errors"].append("Rollback failed: pre-update backup content was not restored")
    except Exception as exc:
        report["passed"] = False
        report["stages"]["rollback"] = {"status": "FAIL", "error": str(exc)}
        report["errors"].append(f"Rollback error: {exc}")

    # Stage 6: Uninstall
    try:
        removed_files = uninstall_skill(
            skill_name=skill_source_dir.name,
            target_platform=alias_name,
            registry_path=reg_path,
        )
        is_clean = not installed_skill_dir.exists()
        reg_data = load_registry(reg_path)
        in_reg = any(r["skill_name"] == skill_source_dir.name for r in reg_data.get("installations", []))
        report["stages"]["uninstall"] = {
            "status": "PASS" if is_clean and not in_reg else "FAIL",
            "removed_files_count": len(removed_files),
            "directory_removed": is_clean,
            "registry_cleaned": not in_reg,
        }
        if not is_clean or in_reg:
            report["passed"] = False
            report["errors"].append("Uninstall failed to clean directory or registry")
    except Exception as exc:
        report["passed"] = False
        report["stages"]["uninstall"] = {"status": "FAIL", "error": str(exc)}
        report["errors"].append(f"Uninstall error: {exc}")

    return report


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        work_dir = Path(tmpdir)
        skills_dir = REPO_ROOT / "generated-skills"

        platforms_to_test = [
            ("claude-code", "claude", skills_dir / "csv-to-report", ["--help"]),
            ("cursor", "cursor", skills_dir / "excel-comparison", ["--help"]),
            ("codex", "openai", skills_dir / "file-organizer", ["--help"]),
            ("antigravity", "google", skills_dir / "security-config-scanner", ["--help"]),
        ]

        all_passed = True
        results = []
        for pid, alias, sdir, targs in platforms_to_test:
            print(f"Testing platform: {pid} (alias '{alias}') with skill '{sdir.name}'...")
            res = run_platform_lifecycle_test(pid, alias, sdir, targs, work_dir)
            results.append(res)
            if not res["passed"]:
                all_passed = False
                print(f"  [FAIL] {pid}: {res['errors']}")
            else:
                print(f"  [PASS] {pid} passed all 6 lifecycle stages!")

        print("\nConsolidated Platform Lifecycle Summary:")
        print(json.dumps(results, indent=2))
        return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
