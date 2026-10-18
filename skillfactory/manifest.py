"""Manifest generation and SHA-256 integrity verification (Phase 1, Task T1.06)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skillfactory import __version__
from skillfactory.spec import SCHEMA_VERSION, SkillSpec


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hex digest of a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def create_manifest(
    skill_dir: Path,
    spec: SkillSpec,
    template_id: str,
    template_version: str = "1.0.0",
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Scan a skill directory and build its manifest with file hashes and metadata."""
    now_utc = datetime.now(timezone.utc).isoformat()
    if created_at is None:
        created_at = now_utc

    files_map: Dict[str, Dict[str, Any]] = {}

    for path in sorted(skill_dir.rglob("*")):
        if path.is_file():
            rel_path = path.relative_to(skill_dir).as_posix()
            # Do not include the manifest itself or temp files
            if rel_path == ".skillfactory/manifest.json" or rel_path.startswith(".tmp"):
                continue
            sha = compute_sha256(path)
            size_bytes = path.stat().st_size
            files_map[rel_path] = {
                "sha256": sha,
                "bytes": size_bytes,
            }

    manifest = {
        "skill_name": spec.name,
        "skill_version": spec.version,
        "generator_name": "skillfactory",
        "generator_version": __version__,
        "template_id": template_id,
        "template_version": template_version,
        "spec_schema_version": SCHEMA_VERSION,
        "created_at": created_at,
        "updated_at": now_utc,
        "files": files_map,
    }
    return manifest


def write_manifest(skill_dir: Path, manifest: Dict[str, Any]) -> Path:
    """Write the manifest JSON file into `<skill_dir>/.skillfactory/manifest.json`."""
    meta_dir = skill_dir / ".skillfactory"
    meta_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = meta_dir / "manifest.json"
    content = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    manifest_path.write_text(content, encoding="utf-8")
    return manifest_path


def verify_manifest(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Verify that all files in the skill match the SHA-256 hashes recorded in the manifest.

    Returns:
        (is_valid, discrepancies)
    """
    manifest_path = skill_dir / ".skillfactory" / "manifest.json"
    if not manifest_path.exists():
        return False, ["Manifest file '.skillfactory/manifest.json' is missing"]

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as err:
        return False, [f"Manifest file is malformed JSON: {err}"]

    recorded_files = data.get("files", {})
    discrepancies: List[str] = []

    # Check that all recorded files exist and match their hash
    for rel_path, file_info in recorded_files.items():
        target_path = skill_dir / rel_path
        if not target_path.exists():
            discrepancies.append(f"Recorded file missing from disk: {rel_path}")
            continue
        expected_sha = file_info.get("sha256")
        actual_sha = compute_sha256(target_path)
        if actual_sha != expected_sha:
            discrepancies.append(
                f"File content modified: {rel_path} (expected SHA-256 {expected_sha[:8]}..., got {actual_sha[:8]}...)"
            )

    return len(discrepancies) == 0, discrepancies
