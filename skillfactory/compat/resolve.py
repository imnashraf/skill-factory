"""Shared skill directory resolution and cross-platform collision detection."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from skillfactory.compat.platform_db import (
    detect_os_key,
    get_all_platforms,
    get_platform,
    get_project_skill_paths,
    get_user_skill_path,
    normalize_platform_id,
)


@dataclass
class ResolvedTarget:
    """A target installation directory mapped to the platforms it serves."""
    target_dir: str
    platforms: List[str]
    scope: str  # "project" or "user"
    primary_platform: str


@dataclass
class CollisionWarning:
    """Warning about duplicate skill names or colliding paths across platforms."""
    skill_name: str
    locations: List[str]
    impacted_platforms: List[str]
    message: str


def resolve_install_targets(
    platforms: List[str],
    scope: str = "project",
    project_dir: Optional[Path | str] = None,
    home_dir: Optional[Path | str] = None,
    os_name: Optional[str] = None,
    db: Optional[Dict[str, Any]] = None,
) -> List[ResolvedTarget]:
    """Resolve a list of requested platforms into a minimal set of target directories.
    
    Prevents duplicate installation where multiple platforms share the same directory
    (e.g., Cursor, Codex, and Antigravity sharing '.agents/skills/').
    """
    p_dir = Path(project_dir).resolve() if project_dir is not None else Path.cwd().resolve()
    h_dir = Path(home_dir).resolve() if home_dir is not None else Path.home().resolve()
    os_key = detect_os_key(os_name)

    dir_to_platforms: Dict[str, List[str]] = {}

    for pid in platforms:
        canonical_pid = normalize_platform_id(pid)
        pdef = get_platform(canonical_pid, db)
        if not pdef:
            continue

        if scope == "project":
            proj_paths = get_project_skill_paths(canonical_pid, db)
            if proj_paths:
                # Prefer primary (first) project path
                canonical_path = str((p_dir / proj_paths[0]).resolve())
                dir_to_platforms.setdefault(canonical_path, []).append(canonical_pid)
        elif scope == "user":
            user_path = get_user_skill_path(canonical_pid, os_name=os_key, home_override=h_dir, db=db)
            if user_path:
                canonical_path = str(Path(user_path).resolve())
                dir_to_platforms.setdefault(canonical_path, []).append(canonical_pid)

    resolved: List[ResolvedTarget] = []
    for target_dir, p_list in dir_to_platforms.items():
        resolved.append(
            ResolvedTarget(
                target_dir=target_dir,
                platforms=p_list,
                scope=scope,
                primary_platform=p_list[0],
            )
        )

    return resolved


def detect_skill_collisions(
    skill_name: str,
    project_dir: Optional[Path | str] = None,
    home_dir: Optional[Path | str] = None,
    os_name: Optional[str] = None,
    db: Optional[Dict[str, Any]] = None,
) -> List[CollisionWarning]:
    """Scan platform search directories to detect duplicate skill installations.
    
    For example, Cursor reads both .agents/skills and .claude/skills. If skill_name
    exists in both, Cursor encounters a collision.
    """
    p_dir = Path(project_dir).resolve() if project_dir is not None else Path.cwd().resolve()
    h_dir = Path(home_dir).resolve() if home_dir is not None else Path.home().resolve()
    os_key = detect_os_key(os_name)
    all_platforms = get_all_platforms(db)

    # Collect all skill directories and which platforms read them
    locations_with_skill: Dict[str, Set[str]] = {}

    for pid, pdef in all_platforms.items():
        # Check project paths
        for rel in pdef.get("project_skill_paths", []):
            cand = (p_dir / rel / skill_name).resolve()
            if cand.exists() and cand.is_dir():
                locations_with_skill.setdefault(str(cand), set()).add(pid)

        # Check foreign paths read by platform (e.g. Cursor reading .claude/skills)
        for foreign in pdef.get("reads_foreign_paths", []):
            if foreign.startswith("~"):
                cand = (Path(h_dir) / foreign[2:].replace("/", os.sep) / skill_name).resolve()
            else:
                cand = (p_dir / foreign / skill_name).resolve()
            if cand.exists() and cand.is_dir():
                locations_with_skill.setdefault(str(cand), set()).add(pid)

        # Check user paths
        u_path = get_user_skill_path(pid, os_name=os_key, home_override=h_dir, db=db)
        if u_path:
            cand = (Path(u_path) / skill_name).resolve()
            if cand.exists() and cand.is_dir():
                locations_with_skill.setdefault(str(cand), set()).add(pid)

    warnings: List[CollisionWarning] = []

    # If the skill exists in more than one distinct physical directory
    if len(locations_with_skill) > 1:
        distinct_paths = list(locations_with_skill.keys())
        all_impacted: Set[str] = set()
        for pset in locations_with_skill.values():
            all_impacted.update(pset)

        warnings.append(
            CollisionWarning(
                skill_name=skill_name,
                locations=distinct_paths,
                impacted_platforms=sorted(list(all_impacted)),
                message=(
                    f"Duplicate skill '{skill_name}' found in multiple locations: "
                    + ", ".join(distinct_paths)
                    + f". Tools like Cursor that scan multiple folders will see collisions."
                ),
            )
        )

    return warnings
