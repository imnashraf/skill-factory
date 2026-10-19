"""Skill installation, update, rollback, and uninstallation engine (Phase 4)."""

from __future__ import annotations

import datetime
import fnmatch
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from skillfactory.compat.detect import detect_all_platforms
from skillfactory.compat.platform_db import (
    detect_os_key,
    get_platform,
    get_project_skill_paths,
    get_user_skill_path,
    normalize_platform_id,
)
from skillfactory.compat.resolve import resolve_install_targets
from skillfactory.manifest import compute_sha256, verify_manifest
from skillfactory.registry import (
    InstallationRecord,
    find_installation,
    get_data_dir,
    get_registry_path,
    load_registry,
    register_installation,
    save_registry,
    unregister_installation,
)

ALLOW_LIST_NAMES = {
    "SKILL.md",
    "README.md",
    "LICENSE",
    "scripts",
    "references",
    "examples",
    "tests",
    ".skillfactory",
}

IGNORE_PATTERNS = {
    "__pycache__",
    "*.pyc",
    ".git",
    ".venv",
    "venv",
    ".DS_Store",
    ".tmp-*",
}


@dataclass
class InstallResult:
    skill_name: str
    target_platform: str
    installed_path: Path
    mode: str  # "copy" or "symlink"
    copied_files: List[str] = field(default_factory=list)
    backup_path: Optional[str] = None
    warning: Optional[str] = None


def is_ignored(name: str) -> bool:
    """Check if file or directory name matches ignored patterns."""
    for pat in IGNORE_PATTERNS:
        if fnmatch.fnmatch(name, pat):
            return True
    return False


def copy_allow_listed_files(
    src_dir: Path,
    dest_dir: Path,
) -> List[str]:
    """Copy only allow-listed files and subdirectories from src to dest.
    
    Normalizes line endings to LF and enforces UTF-8 encoding for text.
    Returns list of copied relative file paths.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied_files: List[str] = []

    for item in src_dir.iterdir():
        if item.name not in ALLOW_LIST_NAMES or is_ignored(item.name):
            continue

        if item.is_file():
            dest_file = dest_dir / item.name
            try:
                text = item.read_text(encoding="utf-8")
                dest_file.write_text(text.replace("\r\n", "\n"), encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                # Binary file fallback
                shutil.copy2(item, dest_file)
            copied_files.append(item.name)

        elif item.is_dir():
            for root, dirs, files in os.walk(str(item)):
                dirs[:] = [d for d in dirs if not is_ignored(d)]
                for file_name in files:
                    if is_ignored(file_name):
                        continue
                    full_src_file = Path(root) / file_name
                    rel_to_skill = full_src_file.relative_to(src_dir)
                    dest_file = dest_dir / rel_to_skill
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    try:
                        text = full_src_file.read_text(encoding="utf-8")
                        dest_file.write_text(text.replace("\r\n", "\n"), encoding="utf-8")
                    except (UnicodeDecodeError, ValueError):
                        shutil.copy2(full_src_file, dest_file)

                    copied_files.append(rel_to_skill.as_posix())

    return sorted(copied_files)


def install_skill(
    skill_path: Path | str,
    target_platform: str,
    scope: str = "project",
    link: bool = False,
    force: bool = False,
    project_dir: Optional[Path | str] = None,
    home_dir: Optional[Path | str] = None,
    os_name: Optional[str] = None,
    registry_path: Optional[Path | str] = None,
) -> InstallResult:
    """Install a skill into a target platform directory with allow-list copying."""
    src = Path(skill_path).resolve()
    if not src.is_dir() or not (src / "SKILL.md").is_file():
        raise ValueError(f"Source directory '{src}' is not a valid skill (missing SKILL.md)")

    skill_name = src.name

    canonical_platform = normalize_platform_id(target_platform)
    pdef = get_platform(canonical_platform)
    if not pdef:
        raise ValueError(
            f"Unknown platform '{target_platform}'. Supported platforms: claude-code, cursor, codex, antigravity (or aliases 'claude', 'openai', 'google')."
        )

    # Determine destination directory
    targets = resolve_install_targets(
        [canonical_platform],
        scope=scope,
        project_dir=project_dir,
        home_dir=home_dir,
        os_name=os_name,
    )
    if not targets:
        raise ValueError(f"Could not resolve install target for platform '{canonical_platform}' with scope '{scope}'")

    dest_container = Path(targets[0].target_dir)
    dest_path = dest_container / skill_name

    # Check for collision with existing unmanaged directory
    if dest_path.exists():
        existing_rec = find_installation(skill_name, installed_path=str(dest_path), registry_path=registry_path)
        if not existing_rec:
            raise FileExistsError(
                f"Destination '{dest_path}' already exists and is not managed by Skill Factory. "
                "Refusing to overwrite existing files (FR-INST-02)."
            )
        if not force:
            raise FileExistsError(
                f"Skill '{skill_name}' is already installed at '{dest_path}'. "
                "Use 'skillfactory update' or pass --force to overwrite."
            )

    # Perform install (symlink or copy)
    warning_msg: Optional[str] = None
    actual_mode = "copy"
    copied_files: List[str] = []

    if link:
        try:
            dest_container.mkdir(parents=True, exist_ok=True)
            if dest_path.exists():
                if dest_path.is_symlink() or dest_path.is_file():
                    dest_path.unlink()
                else:
                    shutil.rmtree(dest_path)
            os.symlink(str(src), str(dest_path))
            actual_mode = "symlink"
            copied_files = [p.name for p in src.iterdir() if p.name in ALLOW_LIST_NAMES]
        except (OSError, NotImplementedError) as err:
            warning_msg = f"Symlink creation failed ({err}); fell back to copy installation."
            actual_mode = "copy"
            copied_files = copy_allow_listed_files(src, dest_path)
    else:
        actual_mode = "copy"
        copied_files = copy_allow_listed_files(src, dest_path)

    # Read version if available
    spec_json = src / ".skillfactory" / "skill-spec.json"
    version = "0.1.0"
    if spec_json.is_file():
        try:
            import json
            data = json.loads(spec_json.read_text(encoding="utf-8"))
            version = data.get("version", "0.1.0")
        except Exception:
            pass

    record = InstallationRecord(
        skill_name=skill_name,
        platform=canonical_platform,
        scope=scope,
        installed_path=str(dest_path),
        source_path=str(src),
        version=version,
        installed_at=datetime.datetime.utcnow().isoformat() + "Z",
        mode=actual_mode,
        installed_files=copied_files,
    )
    register_installation(record, registry_path=registry_path)

    return InstallResult(
        skill_name=skill_name,
        target_platform=canonical_platform,
        installed_path=dest_path,
        mode=actual_mode,
        copied_files=copied_files,
        warning=warning_msg,
    )


def update_skill(
    skill_name: str,
    source_path: Optional[Path | str] = None,
    target_platform: Optional[str] = None,
    force: bool = False,
    home_dir: Optional[Path | str] = None,
    registry_path: Optional[Path | str] = None,
) -> InstallResult:
    """Update an installed skill with automated backup and edit detection."""
    canonical_platform = normalize_platform_id(target_platform) if target_platform else None
    reg_entry = find_installation(skill_name, platform=canonical_platform, registry_path=registry_path)
    if not reg_entry:
        raise ValueError(f"Skill '{skill_name}' is not recorded as installed in Skill Factory registry.")

    installed_path = Path(reg_entry["installed_path"])
    if not installed_path.exists():
        raise FileNotFoundError(f"Installed skill directory not found at '{installed_path}'")

    # Detect local modifications via manifest SHA-256 diff
    valid, discrepancies = verify_manifest(installed_path)
    if not valid and not force:
        disc_text = "; ".join(discrepancies)
        raise ValueError(
            f"Skill '{skill_name}' at '{installed_path}' has local modifications: {disc_text}. "
            "Use --force to overwrite local edits."
        )

    # Create backup snapshot before update (AC4.03)
    backup_base = get_data_dir(home_dir) / "backups" / skill_name
    timestamp_str = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_dir = backup_base / timestamp_str
    backup_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(installed_path, backup_dir)

    # Determine source
    src = Path(source_path).resolve() if source_path else Path(reg_entry.get("source_path", ""))
    if not src.is_dir() or not (src / "SKILL.md").is_file():
        raise ValueError(f"Update source path '{src}' is invalid or missing SKILL.md")

    # Refresh files
    copied_files = copy_allow_listed_files(src, installed_path)

    # Update version
    version = reg_entry.get("version", "0.1.0")
    spec_json = src / ".skillfactory" / "skill-spec.json"
    if spec_json.is_file():
        try:
            import json
            data = json.loads(spec_json.read_text(encoding="utf-8"))
            version = data.get("version", version)
        except Exception:
            pass

    history = reg_entry.get("backup_history", [])
    history.append({
        "backup_path": str(backup_dir),
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "reason": "pre-update",
    })

    updated_record = InstallationRecord(
        skill_name=skill_name,
        platform=reg_entry.get("platform", ""),
        scope=reg_entry.get("scope", "project"),
        installed_path=str(installed_path),
        source_path=str(src),
        version=version,
        installed_at=datetime.datetime.utcnow().isoformat() + "Z",
        mode="copy",
        installed_files=copied_files,
        backup_history=history,
    )
    register_installation(updated_record, registry_path=registry_path)

    return InstallResult(
        skill_name=skill_name,
        target_platform=reg_entry.get("platform", ""),
        installed_path=installed_path,
        mode="copy",
        copied_files=copied_files,
        backup_path=str(backup_dir),
    )


def rollback_skill(
    skill_name: str,
    target_platform: Optional[str] = None,
    registry_path: Optional[Path | str] = None,
) -> InstallResult:
    """Restore the previous working backup snapshot in a single command (AC4.04)."""
    canonical_platform = normalize_platform_id(target_platform) if target_platform else None
    reg_entry = find_installation(skill_name, platform=canonical_platform, registry_path=registry_path)
    if not reg_entry:
        raise ValueError(f"Skill '{skill_name}' not found in installation registry.")

    history = reg_entry.get("backup_history", [])
    if not history:
        raise ValueError(f"No backup snapshots found for skill '{skill_name}'.")

    latest_backup = history[-1]
    backup_path = Path(latest_backup["backup_path"])
    if not backup_path.is_dir():
        raise FileNotFoundError(f"Backup snapshot directory '{backup_path}' does not exist.")

    installed_path = Path(reg_entry["installed_path"])
    if installed_path.exists():
        shutil.rmtree(installed_path)

    shutil.copytree(backup_path, installed_path)

    # Pop latest backup from history
    new_history = history[:-1]
    reg_entry["backup_history"] = new_history
    data = load_registry(registry_path)
    for i, item in enumerate(data.get("installations", [])):
        if item.get("skill_name") == skill_name and item.get("installed_path") == str(installed_path):
            data["installations"][i] = reg_entry
            break
    save_registry(data, registry_path)

    restored_files = [
        p.relative_to(installed_path).as_posix()
        for p in installed_path.rglob("*")
        if p.is_file()
    ]

    return InstallResult(
        skill_name=skill_name,
        target_platform=reg_entry.get("platform", ""),
        installed_path=installed_path,
        mode="copy",
        copied_files=restored_files,
        backup_path=str(backup_path),
    )


def uninstall_skill(
    skill_name: str,
    target_platform: Optional[str] = None,
    registry_path: Optional[Path | str] = None,
) -> List[str]:
    """Remove only manifest/registry tracked files, preserving user data (AC4.05)."""
    canonical_platform = normalize_platform_id(target_platform) if target_platform else None
    reg_entry = find_installation(skill_name, platform=canonical_platform, registry_path=registry_path)
    if not reg_entry:
        raise ValueError(f"Skill '{skill_name}' not found in installation registry.")

    installed_path = Path(reg_entry["installed_path"])
    if not installed_path.exists():
        unregister_installation(skill_name, platform=canonical_platform, registry_path=registry_path)
        return []

    # If it's a symlink, just unlink
    if installed_path.is_symlink():
        installed_path.unlink()
        unregister_installation(skill_name, platform=canonical_platform, registry_path=registry_path)
        return [str(installed_path)]

    # Collect tracked files
    tracked_files = reg_entry.get("installed_files", [])
    manifest_file = installed_path / ".skillfactory" / "manifest.json"
    if manifest_file.is_file():
        try:
            import json
            m_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            for rel in m_data.get("files", {}).keys():
                if rel not in tracked_files:
                    tracked_files.append(rel)
        except Exception:
            pass

    removed: List[str] = []
    # Remove tracked files
    for rel in sorted(tracked_files, reverse=True):
        f_path = installed_path / rel
        if f_path.is_file() or f_path.is_symlink():
            try:
                f_path.unlink()
                removed.append(rel)
            except Exception:
                pass

    # Clean empty directories
    for root, dirs, files in os.walk(str(installed_path), topdown=False):
        for d in dirs:
            dir_to_check = Path(root) / d
            try:
                if not any(dir_to_check.iterdir()):
                    dir_to_check.rmdir()
            except Exception:
                pass

    # If installed_path is now empty, remove it too
    try:
        if not any(installed_path.iterdir()):
            installed_path.rmdir()
    except Exception:
        pass

    unregister_installation(skill_name, platform=canonical_platform, registry_path=registry_path)
    return removed


def install_self(
    target_platform: Optional[str] = None,
    scope: str = "user",
    link: bool = False,
    home_dir: Optional[Path | str] = None,
    registry_path: Optional[Path | str] = None,
) -> List[InstallResult]:
    """Install Skill Factory into host agent skills folder (AC4.08)."""
    root_dir = Path(__file__).parent.parent
    if not (root_dir / "SKILL.md").is_file():
        raise FileNotFoundError(f"Skill Factory root SKILL.md not found at {root_dir}")

    platforms_to_target: List[str] = []
    if target_platform:
        platforms_to_target.append(normalize_platform_id(target_platform))
    else:
        # Detect installed platforms
        detections = detect_all_platforms(home_dir=home_dir)
        for pid, d in detections.items():
            if d.detected:
                platforms_to_target.append(pid)
        if not platforms_to_target:
            # Fallback to cursor/codex/antigravity default
            platforms_to_target = ["antigravity"]

    results: List[InstallResult] = []
    for pid in platforms_to_target:
        res = install_skill(
            skill_path=root_dir,
            target_platform=pid,
            scope=scope,
            link=link,
            force=True,
            home_dir=home_dir,
            registry_path=registry_path,
        )
        results.append(res)

    return results
