"""Skill Pack Management Subsystem (Phase 15, Workstream D).

Provides discovery, batch installation, verification, and uninstallation of
curated skill packs across target AI platforms with atomic rollback on failure.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.errors import SkillFactoryError
from skillfactory.eval import evaluate_skill
from skillfactory.installer import InstallResult, install_skill, uninstall_skill
from skillfactory.scanner import scan_skill_directory
from skillfactory.tester import run_skill_tests
from skillfactory.validator import validate_skill

_PACKS_FILE = Path(__file__).parent / "data" / "packs.json"


@dataclass
class SkillPack:
    id: str
    name: str
    category: str
    description: str
    skills: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_packs() -> List[SkillPack]:
    """Load all skill packs from packs.json."""
    if not _PACKS_FILE.is_file():
        return []
    try:
        data = json.loads(_PACKS_FILE.read_text(encoding="utf-8"))
        return [SkillPack(**p) for p in data.get("packs", [])]
    except Exception:
        return []


def get_pack(pack_id: str) -> Optional[SkillPack]:
    """Find a skill pack by ID or lowercase name."""
    packs = load_packs()
    normalized = pack_id.strip().lower().replace(" ", "-")
    for p in packs:
        if p.id.lower() == normalized or p.name.lower() == pack_id.strip().lower():
            return p
    return None


def resolve_skill_path(skill_name: str, base_dir: Optional[Path | str] = None) -> Optional[Path]:
    """Resolve the directory of a reference skill."""
    candidates = []
    if base_dir:
        candidates.append(Path(base_dir) / skill_name)

    # Search generated-skills/
    candidates.append(Path.cwd() / "generated-skills" / skill_name)
    candidates.append(Path(__file__).parent.parent / "generated-skills" / skill_name)

    for c in candidates:
        if c.is_dir() and (c / "SKILL.md").is_file():
            return c.resolve()
    return None


def install_pack(
    pack_id: str,
    target_platform: str,
    scope: str = "project",
    project_dir: Optional[Path | str] = None,
    force: bool = False,
    yes: bool = False,
    base_dir: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Install all skills in a pack into a target platform."""
    pack = get_pack(pack_id)
    if not pack:
        raise SkillFactoryError(
            message=f"Skill pack '{pack_id}' not found.",
            why=f"No registered pack matches identifier '{pack_id}'.",
            suggestion="Run 'skillfactory pack list' to view all available packs.",
            exit_code=1,
        )

    results: List[Dict[str, Any]] = []
    installed_skills: List[str] = []

    try:
        for s_name in pack.skills:
            s_path = resolve_skill_path(s_name, base_dir=base_dir)
            if not s_path:
                raise SkillFactoryError(
                    message=f"Skill '{s_name}' in pack '{pack.name}' could not be located.",
                    why=f"Expected skill folder '{s_name}' was not found in generated-skills/.",
                    suggestion="Verify that the skill folder exists or re-create it using 'skillfactory new'.",
                    exit_code=1,
                )

            res = install_skill(
                skill_path=s_path,
                target_platform=target_platform,
                scope=scope,
                project_dir=project_dir,
                force=force,
            )
            installed_skills.append(s_name)
            results.append({
                "skill": s_name,
                "status": "installed",
                "installed_path": str(res.installed_path),
            })

    except Exception as exc:
        # Partial failure recovery: rollback already installed skills in this batch
        rollback_errors = []
        for installed_name in installed_skills:
            try:
                uninstall_skill(
                    skill_name=installed_name,
                    target_platform=target_platform,
                )
            except Exception as rb_err:
                rollback_errors.append(f"{installed_name}: {rb_err}")

        why_msg = f"Installation of pack '{pack.name}' failed during '{s_name}': {exc}"
        if rollback_errors:
            why_msg += f" (Rollback errors: {'; '.join(rollback_errors)})"

        raise SkillFactoryError(
            message=f"Failed to install pack '{pack.name}'.",
            why=why_msg,
            suggestion="Resolve the issue and re-try pack installation.",
            exit_code=1,
        )

    return {
        "status": "success",
        "pack_id": pack.id,
        "pack_name": pack.name,
        "target_platform": target_platform,
        "installed_count": len(results),
        "skills": results,
    }


def verify_pack(pack_id: str, base_dir: Optional[Path | str] = None) -> Dict[str, Any]:
    """Run validation, test execution, safety scan, and evaluation on all skills in a pack."""
    pack = get_pack(pack_id)
    if not pack:
        raise SkillFactoryError(
            message=f"Skill pack '{pack_id}' not found.",
            why=f"No registered pack matches identifier '{pack_id}'.",
            suggestion="Run 'skillfactory pack list' to view all available packs.",
            exit_code=1,
        )

    results: List[Dict[str, Any]] = []
    all_clean = True

    for s_name in pack.skills:
        s_path = resolve_skill_path(s_name, base_dir=base_dir)
        if not s_path:
            results.append({
                "skill": s_name,
                "valid": False,
                "tests_passed": False,
                "safety_clean": False,
                "grade": "Missing",
                "score": 0,
                "error": "Skill folder not found",
            })
            all_clean = False
            continue

        val = validate_skill(s_path)
        tests = run_skill_tests(s_path)
        safety = scan_skill_directory(s_path)
        ev = evaluate_skill(s_path, run_tests=False, save_report=False)

        skill_ok = val.is_valid and tests.success and safety.is_clean
        if not skill_ok:
            all_clean = False

        results.append({
            "skill": s_name,
            "valid": val.is_valid,
            "tests_passed": tests.success,
            "safety_clean": safety.is_clean,
            "grade": ev.grade,
            "score": ev.total_score,
        })

    return {
        "pack_id": pack.id,
        "pack_name": pack.name,
        "all_clean": all_clean,
        "total_skills": len(results),
        "results": results,
    }


def uninstall_pack(
    pack_id: str,
    target_platform: str,
    scope: str = "project",
    project_dir: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Cleanly uninstall all skills in a pack."""
    pack = get_pack(pack_id)
    if not pack:
        raise SkillFactoryError(
            message=f"Skill pack '{pack_id}' not found.",
            why=f"No registered pack matches identifier '{pack_id}'.",
            suggestion="Run 'skillfactory pack list' to view all available packs.",
            exit_code=1,
        )

    results: List[Dict[str, Any]] = []
    for s_name in pack.skills:
        try:
            removed = uninstall_skill(
                skill_name=s_name,
                target_platform=target_platform,
            )
            results.append({
                "skill": s_name,
                "status": "uninstalled",
                "removed_files_count": len(removed),
            })
        except Exception as e:
            results.append({
                "skill": s_name,
                "status": "error",
                "error": str(e),
            })

    return {
        "status": "success",
        "pack_id": pack.id,
        "pack_name": pack.name,
        "target_platform": target_platform,
        "uninstalled_count": len([r for r in results if r["status"] == "uninstalled"]),
        "results": results,
    }
