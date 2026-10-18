"""Skill packaging, reproducible zip export, and Zip-Slip secure import (Phase 6, Tasks T6.03, T6.04).

Implements:
1. `export_skill`: packages skill into a portable .zip with SHA-256 checksum (AC6.03).
2. `import_skill`: safe extraction defending against Zip-Slip path traversal attacks,
   checksum verification, and pre-extraction security scanning (AC6.04).
"""
from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.scanner import scan_skill_directory
from skillfactory.validator import validate_skill

# Excluded paths when packaging skills
PACKAGE_EXCLUDE_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    ".DS_Store",
    "Thumbs.db",
}


class ZipSecurityError(Exception):
    """Raised when an archive fails safety or integrity checks."""


@dataclass
class ExportResult:
    zip_path: Path
    sha256_hash: str
    file_count: int
    size_bytes: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zip_path": str(self.zip_path),
            "sha256_hash": self.sha256_hash,
            "file_count": self.file_count,
            "size_bytes": self.size_bytes,
        }


@dataclass
class ImportResult:
    skill_name: str
    installed_path: Path
    file_count: int
    validation_valid: bool
    safety_clean: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "installed_path": str(self.installed_path),
            "file_count": self.file_count,
            "validation_valid": self.validation_valid,
            "safety_clean": self.safety_clean,
        }


def calculate_file_sha256(path: Path) -> str:
    """Calculate SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def export_skill(
    skill_dir: Path,
    output_zip: Optional[Path] = None,
    create_sidecar: bool = True,
) -> ExportResult:
    """Package an Agent Skill into a portable .zip archive with SHA-256 checksum (AC6.03).

    Args:
        skill_dir: Directory containing the skill to package.
        output_zip: Destination path for .zip file (default: <skill_name>.zip in current dir).
        create_sidecar: If True, writes <output_zip>.sha256 checksum sidecar.

    Returns:
        ExportResult containing archive details.
    """
    skill_path = Path(skill_dir).resolve()
    if not skill_path.exists() or not skill_path.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    skill_name = skill_path.name
    val = validate_skill(skill_path, check_dirname=False)
    if not val.is_valid:
        raise ValueError(f"Cannot export invalid skill: {'; '.join(val.errors)}")

    if output_zip is None:
        target_zip = Path.cwd() / f"{skill_name}.zip"
    else:
        target_zip = Path(output_zip).resolve()

    target_zip.parent.mkdir(parents=True, exist_ok=True)

    # Collect files
    files_to_pack: List[Path] = []
    for p in skill_path.rglob("*"):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(skill_path).parts
        if any(part in PACKAGE_EXCLUDE_NAMES for part in rel_parts):
            continue
        files_to_pack.append(p)

    # Temporary staging file for atomic zip creation
    tmp_zip = target_zip.parent / f".tmp-{uuid.uuid4().hex}.zip"
    try:
        with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(files_to_pack):
                arcname = str(Path(skill_name) / file_path.relative_to(skill_path))
                # Normalize zip info to eliminate host-dependent metadata
                zinfo = zipfile.ZipInfo(arcname)
                # Set fixed date-time for reproducible archives
                zinfo.date_time = (2026, 1, 1, 0, 0, 0)
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                zinfo.external_attr = 0o644 << 16  # standard read/write permissions
                zf.writestr(zinfo, file_path.read_bytes())

        # Atomic rename
        os.replace(tmp_zip, target_zip)
    finally:
        if tmp_zip.exists():
            tmp_zip.unlink(missing_ok=True)

    sha256_hash = calculate_file_sha256(target_zip)
    size_bytes = target_zip.stat().st_size

    if create_sidecar:
        sidecar = target_zip.with_suffix(target_zip.suffix + ".sha256")
        sidecar.write_text(f"{sha256_hash}  {target_zip.name}\n", encoding="utf-8")

    return ExportResult(
        zip_path=target_zip,
        sha256_hash=sha256_hash,
        file_count=len(files_to_pack),
        size_bytes=size_bytes,
    )


def import_skill(
    zip_path: Path,
    dest_dir: Path,
    verify_checksum: Optional[str] = None,
    force: bool = False,
) -> ImportResult:
    """Safely import an Agent Skill from a .zip archive (AC6.04).

    Defends against Zip-Slip path traversal attacks, verifies checksums,
    and runs safety scan before finalizing installation.

    Args:
        zip_path: Path to the .zip archive.
        dest_dir: Target directory where the skill folder should be placed.
        verify_checksum: Optional expected SHA-256 hex digest.
        force: If True, overwrites destination if it already exists.

    Returns:
        ImportResult detailing installation status.
    """
    archive_file = Path(zip_path).resolve()
    if not archive_file.exists() or not archive_file.is_file():
        raise FileNotFoundError(f"Archive file not found: {archive_file}")

    # 1. Verify Checksum if provided
    actual_hash = calculate_file_sha256(archive_file)
    if verify_checksum:
        clean_expected = verify_checksum.strip().lower()
        if actual_hash.lower() != clean_expected:
            raise ZipSecurityError(
                f"Checksum mismatch for '{archive_file.name}'. Expected: {clean_expected}, Actual: {actual_hash}"
            )

    dest_path = Path(dest_dir).resolve()
    dest_path.mkdir(parents=True, exist_ok=True)

    # 2. Inspect archive entries for Zip-Slip attacks (AC6.04)
    with zipfile.ZipFile(archive_file, "r") as zf:
        infolist = zf.infolist()
        if not infolist:
            raise ZipSecurityError("Archive is empty.")

        staging_dir = dest_path / f".tmp-import-{uuid.uuid4().hex}"
        staging_dir.mkdir(parents=True, exist_ok=True)

        try:
            for info in infolist:
                # Check for absolute paths
                name = info.filename
                if name.startswith("/") or name.startswith("\\"):
                    raise ZipSecurityError(
                        f"Zip-Slip vulnerability detected: absolute path in archive member '{name}'"
                    )
                if len(name) > 2 and name[1] == ":" and name[2] in ("/\\"):
                    raise ZipSecurityError(
                        f"Zip-Slip vulnerability detected: Windows drive path in archive member '{name}'"
                    )

                # Check for path traversal components '..'
                norm_parts = Path(name).parts
                if ".." in norm_parts:
                    raise ZipSecurityError(
                        f"Zip-Slip vulnerability detected: path traversal '..' in member '{name}'"
                    )

                # Check symlink attributes
                is_symlink = (info.external_attr >> 16) & 0o170000 == 0o120000
                if is_symlink:
                    raise ZipSecurityError(
                        f"Security policy violation: symlink entry detected in archive member '{name}'"
                    )

                # Verify resolved target is inside staging_dir
                target = (staging_dir / name).resolve()
                if not str(target).startswith(str(staging_dir.resolve())):
                    raise ZipSecurityError(
                        f"Zip-Slip vulnerability detected: member '{name}' escapes destination boundary"
                    )

            # 3. Extract safely into staging_dir
            zf.extractall(staging_dir)

            # 4. Determine extracted root directory
            extracted_items = [p for p in staging_dir.iterdir() if not p.name.startswith(".")]
            if len(extracted_items) == 1 and extracted_items[0].is_dir() and (extracted_items[0] / "SKILL.md").exists():
                skill_staging = extracted_items[0]
                skill_name = skill_staging.name
            elif (staging_dir / "SKILL.md").exists():
                skill_staging = staging_dir
                skill_name = archive_file.stem
            else:
                raise ZipSecurityError("No valid Agent Skill root found in archive (missing SKILL.md)")

            # 5. Pre-extraction safety scan & validation
            safety = scan_skill_directory(skill_staging)
            if not safety.is_clean:
                reasons = [f"[{f.rule_id}] {f.description}" for f in safety.findings if f.severity in ("CRITICAL", "HIGH")]
                raise ZipSecurityError(
                    f"Import rejected due to safety violations in archive: {'; '.join(reasons)}"
                )

            val = validate_skill(skill_staging, check_dirname=False)
            if not val.is_valid:
                raise ZipSecurityError(
                    f"Import rejected: skill failed specification validation: {'; '.join(val.errors)}"
                )

            # 6. Move to final destination
            final_target = dest_path / skill_name
            if final_target.exists():
                if not force:
                    raise FileExistsError(
                        f"Target folder '{final_target}' already exists. Use --force to overwrite."
                    )
                if final_target.is_dir():
                    shutil.rmtree(final_target)
                else:
                    final_target.unlink()

            if skill_staging != staging_dir:
                shutil.move(str(skill_staging), str(final_target))
            else:
                # Flat extraction
                final_target.mkdir(parents=True, exist_ok=True)
                for item in staging_dir.iterdir():
                    shutil.move(str(item), str(final_target / item.name))

            file_count = sum(1 for p in final_target.rglob("*") if p.is_file())

            return ImportResult(
                skill_name=skill_name,
                installed_path=final_target,
                file_count=file_count,
                validation_valid=val.is_valid,
                safety_clean=safety.is_clean,
            )

        finally:
            if staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)
