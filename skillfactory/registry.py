"""Local installation registry manager (Phase 4, Task T4.01).

Manages ~/.skillfactory/registry.json (or SKILLFACTORY_HOME) tracking installed skills,
platforms, scopes, versions, and backup snapshots.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.compat.platform_db import normalize_platform_id


@dataclass
class BackupEntry:
    backup_path: str
    created_at: str
    reason: str = "pre-update"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InstallationRecord:
    skill_name: str
    platform: str
    scope: str  # "project" or "user"
    installed_path: str
    source_path: str
    version: str
    installed_at: str
    mode: str = "copy"  # "copy" or "symlink"
    installed_files: List[str] = field(default_factory=list)
    backup_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_data_dir(home_override: Optional[Path | str] = None) -> Path:
    """Return the base user data directory for Skill Factory."""
    if home_override is not None:
        return Path(home_override).resolve()
    env_home = os.environ.get("SKILLFACTORY_HOME")
    if env_home:
        return Path(env_home).resolve()
    return (Path.home() / ".skillfactory").resolve()


def get_registry_path(home_override: Optional[Path | str] = None) -> Path:
    """Return the path to registry.json."""
    return get_data_dir(home_override) / "registry.json"


def load_registry(registry_path: Optional[Path | str] = None) -> Dict[str, Any]:
    """Load registry.json from disk or return empty registry structure."""
    reg_file = Path(registry_path) if registry_path is not None else get_registry_path()
    if not reg_file.is_file():
        return {"schema_version": "1.0", "installations": []}

    try:
        with open(reg_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "installations" not in data:
                data["installations"] = []
            return data
    except Exception:
        return {"schema_version": "1.0", "installations": []}


def save_registry(data: Dict[str, Any], registry_path: Optional[Path | str] = None) -> None:
    """Atomically write registry.json with UTF-8 and formatting."""
    reg_file = Path(registry_path) if registry_path is not None else get_registry_path()
    reg_file.parent.mkdir(parents=True, exist_ok=True)

    tmp_file = reg_file.parent / f".tmp-registry-{os.getpid()}.json"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(str(tmp_file), str(reg_file))


def find_installation(
    skill_name: str,
    platform: Optional[str] = None,
    installed_path: Optional[str] = None,
    registry_path: Optional[Path | str] = None,
) -> Optional[Dict[str, Any]]:
    """Find a specific installation record."""
    data = load_registry(registry_path)
    for record in data.get("installations", []):
        if record.get("skill_name") == skill_name:
            if platform is not None and normalize_platform_id(record.get("platform", "")) != normalize_platform_id(platform):
                continue
            if installed_path is not None:
                # Compare resolved absolute paths
                try:
                    if Path(record.get("installed_path")).resolve() != Path(installed_path).resolve():
                        continue
                except Exception:
                    continue
            return record
    return None


def register_installation(
    record: InstallationRecord,
    registry_path: Optional[Path | str] = None,
) -> None:
    """Add or update an installation record in registry.json."""
    data = load_registry(registry_path)
    installations = data.get("installations", [])

    # Replace existing record for the same skill and installed_path if present
    norm_dest = str(Path(record.installed_path).resolve())
    updated = False
    for i, existing in enumerate(installations):
        existing_dest = str(Path(existing.get("installed_path", "")).resolve())
        if existing.get("skill_name") == record.skill_name and existing_dest == norm_dest:
            installations[i] = record.to_dict()
            updated = True
            break

    if not updated:
        installations.append(record.to_dict())

    data["installations"] = installations
    save_registry(data, registry_path)


def unregister_installation(
    skill_name: str,
    platform: Optional[str] = None,
    installed_path: Optional[str] = None,
    registry_path: Optional[Path | str] = None,
) -> bool:
    """Remove an installation record from registry.json."""
    data = load_registry(registry_path)
    installations = data.get("installations", [])
    initial_len = len(installations)

    filtered = []
    for rec in installations:
        if rec.get("skill_name") == skill_name:
            if platform is not None and normalize_platform_id(rec.get("platform", "")) != normalize_platform_id(platform):
                filtered.append(rec)
                continue
            if installed_path is not None:
                try:
                    if Path(rec.get("installed_path")).resolve() != Path(installed_path).resolve():
                        filtered.append(rec)
                        continue
                except Exception:
                    pass
            # Match to remove
            continue
        filtered.append(rec)

    data["installations"] = filtered
    save_registry(data, registry_path)
    return len(filtered) < initial_len
