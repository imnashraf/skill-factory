"""Agent Skills specification validator and quality linter (Phase 1, Task T1.07).

Fixes DEF-02 by strictly rejecting Windows reserved device names (CON, PRN, AUX, NUL,
COM1-9, LPT1-9) and platform reserved names (synced).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.manifest import verify_manifest
from skillfactory.spec import (
    NAME_PATTERN,
    PLATFORM_RESERVED_NAMES,
    WINDOWS_RESERVED_NAMES,
)
from skillfactory.yaml_util import YamlError, parse_frontmatter

# Markdown link regex: [text](path)
MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    skill_dir: Optional[Path] = None
    skill_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "skill_name": self.skill_name,
            "skill_dir": str(self.skill_dir) if self.skill_dir else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


def validate_skill_name(name: str) -> List[str]:
    """Validate a skill name according to Agent Skills spec and platform rules."""
    errors: List[str] = []
    if not name or not isinstance(name, str):
        return ["Skill name must be a non-empty string"]

    name_clean = name.strip()
    if len(name_clean) < 1 or len(name_clean) > 64:
        errors.append(f"Skill name must be between 1 and 64 characters (got {len(name_clean)})")

    if not NAME_PATTERN.fullmatch(name_clean):
        errors.append(
            f"Skill name '{name}' must be lowercase alphanumeric with single hyphens (^[a-z0-9]+(?:-[a-z0-9]+)*$)"
        )

    if name_clean.lower() in WINDOWS_RESERVED_NAMES:
        errors.append(
            f"Skill name '{name}' is reserved by Windows (CON, PRN, AUX, NUL, COM1-9, LPT1-9)"
        )

    if name_clean.lower() in PLATFORM_RESERVED_NAMES:
        errors.append(
            f"Skill name '{name}' is reserved by target platforms (e.g. Claude Code 'synced')"
        )

    return errors


def validate_skill(
    skill_dir: Path,
    expected_name: Optional[str] = None,
    verify_hashes: bool = True,
    check_dirname: bool = True,
) -> ValidationResult:
    """Validate an Agent Skill folder against specification rules and best practices.

    Returns:
        ValidationResult containing pass/fail status, errors, and warnings.
    """
    errors: List[str] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}

    skill_path = Path(skill_dir).resolve()

    if not skill_path.exists():
        return ValidationResult(
            is_valid=False,
            errors=[f"Directory does not exist: {skill_path}"],
            skill_dir=skill_path,
        )

    if not skill_path.is_dir():
        return ValidationResult(
            is_valid=False,
            errors=[f"Target path is not a directory: {skill_path}"],
            skill_dir=skill_path,
        )

    folder_name = skill_path.name
    # 1. Folder name check
    if check_dirname:
        name_errors = validate_skill_name(folder_name)
        errors.extend(name_errors)

        if expected_name and folder_name != expected_name:
            errors.append(f"Directory name '{folder_name}' does not match expected name '{expected_name}'")
    elif expected_name:
        name_errors = validate_skill_name(expected_name)
        errors.extend(name_errors)

    # 2. SKILL.md existence
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"Missing required 'SKILL.md' at {skill_path}")
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            skill_dir=skill_path,
            skill_name=folder_name,
        )

    # 3. Read and parse SKILL.md frontmatter
    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as err:
        errors.append(f"Failed to read SKILL.md with UTF-8 encoding: {err}")
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            skill_dir=skill_path,
            skill_name=folder_name,
        )

    try:
        fm, body = parse_frontmatter(content)
        metadata["frontmatter"] = fm
    except YamlError as err:
        errors.append(f"Invalid YAML frontmatter in SKILL.md: {err}")
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            skill_dir=skill_path,
            skill_name=folder_name,
        )

    # 4. Frontmatter fields validation
    fm_name = fm.get("name")
    if not fm_name:
        errors.append("Frontmatter missing required 'name' field")
    else:
        if check_dirname and fm_name != folder_name:
            errors.append(
                f"Frontmatter name '{fm_name}' must match parent directory name '{folder_name}'"
            )
        elif not check_dirname and expected_name and fm_name != expected_name:
            errors.append(
                f"Frontmatter name '{fm_name}' must match expected name '{expected_name}'"
            )
        fm_name_errors = validate_skill_name(str(fm_name))
        for err in fm_name_errors:
            if err not in errors:
                errors.append(f"Frontmatter name: {err}")

    fm_desc = fm.get("description")
    if not fm_desc or not str(fm_desc).strip():
        errors.append("Frontmatter missing required non-empty 'description' field")
    else:
        desc_str = str(fm_desc).strip()
        if len(desc_str) > 1024:
            errors.append(f"Frontmatter description exceeds 1024 characters (got {len(desc_str)})")

    fm_compat = fm.get("compatibility")
    if fm_compat is not None:
        if not isinstance(fm_compat, str):
            errors.append("Frontmatter 'compatibility' must be a string")
        elif len(fm_compat) > 500:
            errors.append(f"Frontmatter compatibility exceeds 500 characters (got {len(fm_compat)})")

    fm_meta = fm.get("metadata")
    if fm_meta is not None:
        if not isinstance(fm_meta, dict):
            errors.append("Frontmatter 'metadata' must be a mapping of string to string")
        else:
            for k, v in fm_meta.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    errors.append(f"Frontmatter metadata entry '{k}' must be string: string")

    # 5. Best-practice size checks
    lines = content.splitlines()
    if len(lines) > 500:
        warnings.append(
            f"SKILL.md exceeds 500 lines ({len(lines)} lines). Consider moving reference material into references/"
        )

    # Token estimate (~1.33 words per token)
    words = len(body.split())
    est_tokens = int(words * 1.33)
    if est_tokens > 5000:
        warnings.append(
            f"SKILL.md body length exceeds ~5,000 estimated tokens (~{est_tokens} tokens). "
            "Consider keeping prompt concise."
        )

    # 6. File reference links check
    for match in MD_LINK_PATTERN.finditer(body):
        link_target = match.group(2).strip()
        # Skip external links and anchors
        if link_target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # Check absolute path
        if link_target.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", link_target):
            errors.append(f"Hardcoded absolute path found in link: '{link_target}'")
            continue
        # Check path traversal
        if ".." in Path(link_target).parts:
            errors.append(f"Path traversal detected in link: '{link_target}'")
            continue
        # Check depth
        parts = Path(link_target).parts
        if len(parts) > 2:
            warnings.append(
                f"Reference path '{link_target}' is nested more than one level deep. Agent discovery works best with shallow references."
            )
        # Check file exists
        resolved = skill_path / link_target
        if not resolved.exists():
            errors.append(f"Referenced file does not exist: '{link_target}'")

    # 7. Manifest verification
    if verify_hashes:
        manifest_path = skill_path / ".skillfactory" / "manifest.json"
        if manifest_path.exists():
            valid_hashes, discrepancies = verify_manifest(skill_path)
            if not valid_hashes:
                for disc in discrepancies:
                    errors.append(f"Manifest discrepancy: {disc}")

    # 8. Windows MAX_PATH warning (EC-10)
    for p in skill_path.rglob("*"):
        if len(str(p)) > 250:
            warnings.append(
                f"Path length ({len(str(p))} chars) approaches Windows MAX_PATH limit (260): {p.relative_to(skill_path)}"
            )

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        skill_dir=skill_path,
        skill_name=folder_name,
        metadata=metadata,
    )
