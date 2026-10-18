"""Core Skill Generator Engine (Phase 1, Task T1.04).

Implements atomic skill generation with sibling staging (.tmp-*), rollback on error,
UTF-8 with LF line endings, and manifest creation.
"""
from __future__ import annotations

import os
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from skillfactory.manifest import create_manifest, write_manifest
from skillfactory.spec import SkillSpec, SpecValidationError
from skillfactory.templates.loader import render_template_family
from skillfactory.validator import validate_skill


@dataclass
class GenerationResult:
    skill_name: str
    target_path: Path
    written_files: List[str] = field(default_factory=list)
    dry_run: bool = False
    manifest: Optional[Dict] = None


def generate_skill(
    spec: SkillSpec,
    output_dir: Path,
    dry_run: bool = False,
) -> GenerationResult:
    """Atomically generate an Agent Skill directory from a SkillSpec.

    Args:
        spec: The SkillSpec defining the skill.
        output_dir: Parent directory where the skill folder will reside.
        dry_run: If True, simulate actions without creating files on disk.

    Returns:
        GenerationResult describing the outcome.

    Raises:
        SpecValidationError: If the spec is invalid.
        FileExistsError: If target skill folder already exists.
        OSError: If filesystem operations fail.
    """
    # 1. Validate spec
    errors = spec.validate()
    if errors:
        raise SpecValidationError(errors)

    out_root = Path(output_dir).resolve()
    target_dir = out_root / spec.name

    if target_dir.exists():
        raise FileExistsError(
            f"Target directory '{target_dir}' already exists. "
            "Skill Factory refuses to overwrite existing directories (FR-CORE-06)."
        )

    # 2. Render templates
    files = render_template_family(spec)

    # Add .skillfactory/skill-spec.json
    spec_json = spec.to_json(indent=2)
    files[".skillfactory/skill-spec.json"] = spec_json

    if dry_run:
        return GenerationResult(
            skill_name=spec.name,
            target_path=target_dir,
            written_files=sorted(list(files.keys())),
            dry_run=True,
        )

    # 3. Atomic sibling staging
    out_root.mkdir(parents=True, exist_ok=True)
    staging_dir = out_root / f".tmp-{spec.name}-{uuid.uuid4().hex[:8]}"

    completed = False
    try:
        staging_dir.mkdir(parents=True, exist_ok=False)

        # Write all rendered files
        for rel_path, content in files.items():
            file_dest = staging_dir / rel_path
            file_dest.parent.mkdir(parents=True, exist_ok=True)
            # Ensure LF line endings and UTF-8 encoding
            normalized_content = content.replace("\r\n", "\n")
            file_dest.write_text(normalized_content, encoding="utf-8")

        # Generate and write manifest.json
        manifest = create_manifest(staging_dir, spec, template_id=spec.template_family)
        write_manifest(staging_dir, manifest)

        # Validate staged skill directory
        val_result = validate_skill(
            staging_dir,
            expected_name=spec.name,
            verify_hashes=True,
            check_dirname=False,
        )
        if not val_result.is_valid:
            raise ValueError(
                f"Generated skill failed validation: {'; '.join(val_result.errors)}"
            )

        # Atomically rename staging to target
        os.replace(str(staging_dir), str(target_dir))
        completed = True

        all_written = [
            p.relative_to(target_dir).as_posix()
            for p in sorted(target_dir.rglob("*"))
            if p.is_file()
        ]

        return GenerationResult(
            skill_name=spec.name,
            target_path=target_dir,
            written_files=all_written,
            dry_run=False,
            manifest=manifest,
        )

    finally:
        if not completed and staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def create_scaffold(name: str, description: str, destination: Path) -> Path:
    """Compatibility function matching scripts/create_skill.py behavior."""
    spec = SkillSpec(
        name=name,
        description=description,
        template_family="python-script",
    )
    result = generate_skill(spec, destination, dry_run=False)
    return result.target_path
