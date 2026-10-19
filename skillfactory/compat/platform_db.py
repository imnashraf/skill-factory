"""Data-driven platform configuration loader and query utilities."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_PLATFORMS_FILE = Path(__file__).parent.parent / "data" / "platforms.json"
_CACHED_DB: Optional[Dict[str, Any]] = None


def load_platforms_db(path: Optional[Path | str] = None) -> Dict[str, Any]:
    """Load the platforms database from disk.
    
    Caches the parsed result when using the default path.
    """
    global _CACHED_DB
    target_path = Path(path) if path is not None else _PLATFORMS_FILE
    
    if path is None and _CACHED_DB is not None:
        return _CACHED_DB

    if not target_path.is_file():
        raise FileNotFoundError(f"Platforms database not found at {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if path is None:
        _CACHED_DB = data
    return data


def get_all_platforms(db: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
    """Return dictionary of all registered platforms."""
    data = db or load_platforms_db()
    return data.get("platforms", {})


PLATFORM_ALIASES: Dict[str, str] = {
    "claude": "claude-code",
    "claudecode": "claude-code",
    "claude-code": "claude-code",
    "anthropic": "claude-code",
    "cursor": "cursor",
    "anysphere": "cursor",
    "codex": "codex",
    "openai": "codex",
    "openai-codex": "codex",
    "antigravity": "antigravity",
    "agy": "antigravity",
    "google": "antigravity",
    "google-antigravity": "antigravity",
    "gemini": "antigravity",
}


def normalize_platform_id(platform_id: str) -> str:
    """Normalize user input or alias to canonical platform ID.

    Examples:
        'claude' -> 'claude-code'
        'anthropic' -> 'claude-code'
        'openai' -> 'codex'
        'google' -> 'antigravity'
        'agy' -> 'antigravity'
    """
    if not platform_id:
        return platform_id
    key = platform_id.strip().lower()
    return PLATFORM_ALIASES.get(key, key)


def get_platform(platform_id: str, db: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Retrieve platform definition by ID (e.g. 'claude-code', 'cursor') or alias."""
    platforms = get_all_platforms(db)
    canonical = normalize_platform_id(platform_id)
    return platforms.get(canonical)


def detect_os_key(platform_os: Optional[str] = None) -> str:
    """Normalize system OS to platforms.json keys: 'macos', 'linux', or 'windows'."""
    if platform_os:
        val = platform_os.lower()
        if "darwin" in val or "mac" in val:
            return "macos"
        if "win" in val:
            return "windows"
        return "linux"

    if sys.platform == "darwin":
        return "macos"
    elif sys.platform.startswith("win"):
        return "windows"
    return "linux"


def resolve_path_string(path_str: str, home_override: Optional[Path | str] = None) -> str:
    """Expand '~' or '%USERPROFILE%' using system home or an override for testing."""
    if home_override is not None:
        home_path = str(Path(home_override).resolve())
        if path_str.startswith("~"):
            return os.path.join(home_path, path_str[2:].replace("/", os.sep))
        if "%USERPROFILE%" in path_str:
            return path_str.replace("%USERPROFILE%", home_path).replace("\\", os.sep)
        return path_str

    if "%USERPROFILE%" in path_str:
        userprofile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        return path_str.replace("%USERPROFILE%", userprofile)

    return os.path.expanduser(path_str)


def get_user_skill_path(
    platform_id: str,
    os_name: Optional[str] = None,
    home_override: Optional[Path | str] = None,
    db: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Return the resolved user-level skill directory path for a platform and OS."""
    p = get_platform(platform_id, db)
    if not p:
        return None
    user_paths = p.get("user_skill_paths", {})
    key = detect_os_key(os_name)
    raw = user_paths.get(key)
    if not raw:
        return None
    return resolve_path_string(raw, home_override)


def get_project_skill_paths(
    platform_id: str,
    db: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Return relative project-level skill directories (e.g. ['.claude/skills'])."""
    p = get_platform(platform_id, db)
    if not p:
        return []
    return list(p.get("project_skill_paths", []))


def get_reserved_names(
    platform_id: Optional[str] = None,
    db: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Return reserved names across all platforms or for a specified platform."""
    if platform_id:
        p = get_platform(platform_id, db)
        return list(p.get("reserved_names", [])) if p else []

    reserved: List[str] = []
    for p in get_all_platforms(db).values():
        for name in p.get("reserved_names", []):
            if name not in reserved:
                reserved.append(name)
    return reserved
