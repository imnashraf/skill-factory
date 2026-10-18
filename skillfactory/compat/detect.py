"""Detection of installed AI agent platforms and path readiness."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.compat.platform_db import (
    detect_os_key,
    get_all_platforms,
    get_project_skill_paths,
    get_user_skill_path,
    resolve_path_string,
)


@dataclass
class PlatformDetectionResult:
    """Detection status and path readiness for a single platform."""
    platform_id: str
    display_name: str
    detected: bool
    reasons: List[str] = field(default_factory=list)
    project_skill_paths: List[str] = field(default_factory=list)
    project_path_statuses: Dict[str, str] = field(default_factory=dict)
    user_skill_path: Optional[str] = None
    user_path_status: str = "unknown"
    status_summary: str = "Not detected"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _check_path_status(target_path: Path) -> str:
    """Check if target path exists and is writable, or if its parent is writable."""
    try:
        if target_path.exists():
            if target_path.is_dir():
                return "exists_writable" if os.access(target_path, os.W_OK) else "exists_readonly"
            return "conflict_file_exists"

        # Path does not exist; check nearest existing ancestor
        curr = target_path.parent
        while curr != curr.parent:
            if curr.exists():
                return "ready_to_create" if os.access(curr, os.W_OK) else "parent_readonly"
            curr = curr.parent
        return "ready_to_create"
    except Exception:
        return "inaccessible"


def detect_platform(
    platform_id: str,
    platform_def: Dict[str, Any],
    project_dir: Optional[Path | str] = None,
    home_dir: Optional[Path | str] = None,
    os_name: Optional[str] = None,
) -> PlatformDetectionResult:
    """Detect whether a specific platform is installed and assess skill path readiness."""
    p_dir = Path(project_dir).resolve() if project_dir is not None else Path.cwd().resolve()
    h_dir = Path(home_dir).resolve() if home_dir is not None else Path.home().resolve()
    os_key = detect_os_key(os_name)

    display_name = platform_def.get("display_name", platform_id)
    rules = platform_def.get("detection_rules", {})
    reasons: List[str] = []

    # 1. Project-level directory detection
    for rel_proj in rules.get("project_dirs", []):
        cand = p_dir / rel_proj
        if cand.exists():
            reasons.append(f"Found project folder: {cand.name}/")

    # 2. User-level directory detection
    for raw_user in rules.get("user_dirs", []):
        resolved_user = Path(resolve_path_string(raw_user, home_override=h_dir))
        if resolved_user.exists():
            reasons.append(f"Found user directory: {resolved_user.name}/")

    # 3. Binary detection
    for binary in rules.get("binaries", []):
        if shutil.which(binary) is not None:
            reasons.append(f"Found binary command: '{binary}'")

    detected = len(reasons) > 0

    # Evaluate project skill paths
    project_paths: List[str] = []
    project_statuses: Dict[str, str] = {}
    for rel_skill in platform_def.get("project_skill_paths", []):
        full_proj_skill = p_dir / rel_skill
        project_paths.append(str(full_proj_skill))
        project_statuses[rel_skill] = _check_path_status(full_proj_skill)

    # Evaluate user skill path
    user_skill_path = get_user_skill_path(platform_id, os_name=os_key, home_override=h_dir)
    user_status = "unknown"
    if user_skill_path:
        user_status = _check_path_status(Path(user_skill_path))

    if detected:
        status_summary = f"Detected ({', '.join(reasons)})"
    else:
        status_summary = "Not detected on host"

    return PlatformDetectionResult(
        platform_id=platform_id,
        display_name=display_name,
        detected=detected,
        reasons=reasons,
        project_skill_paths=project_paths,
        project_path_statuses=project_statuses,
        user_skill_path=user_skill_path,
        user_path_status=user_status,
        status_summary=status_summary,
    )


def detect_all_platforms(
    project_dir: Optional[Path | str] = None,
    home_dir: Optional[Path | str] = None,
    os_name: Optional[str] = None,
    db: Optional[Dict[str, Any]] = None,
) -> Dict[str, PlatformDetectionResult]:
    """Scan the environment for all registered platforms."""
    platforms = get_all_platforms(db)
    results: Dict[str, PlatformDetectionResult] = {}
    for pid, pdef in platforms.items():
        results[pid] = detect_platform(
            platform_id=pid,
            platform_def=pdef,
            project_dir=project_dir,
            home_dir=home_dir,
            os_name=os_name,
        )
    return results
