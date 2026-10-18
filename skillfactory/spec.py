"""Canonical SkillSpec data model and schema validation (Phase 1, Task T1.02)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = 1

VALID_TEMPLATE_FAMILIES = {
    "instructions-only",
    "python-script",
    "checklist-review",
    "file-transform",
    "workflow-runbook",
}

WINDOWS_RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
    "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
}

PLATFORM_RESERVED_NAMES = {
    "synced",
}

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SpecValidationError(ValueError):
    """Raised when a SkillSpec fails validation."""
    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass
class SkillSpec:
    name: str
    description: str
    template_family: str = "python-script"
    version: str = "0.1.0"
    author: str = ""
    license: str = "MIT"
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    edge_cases: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    scripts_needed: Optional[bool] = None
    script_language: str = "python"
    target_platforms: List[str] = field(default_factory=lambda: [
        "claude-code", "cursor", "codex", "antigravity"
    ])
    compatibility: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self):
        if self.scripts_needed is None:
            self.scripts_needed = self.template_family in ("python-script", "file-transform")

    def validate(self) -> List[str]:
        """Validate the spec against schema rules and naming constraints.

        Returns a list of error descriptions (empty if valid).
        """
        errors: List[str] = []

        # Name validation
        if not self.name or not isinstance(self.name, str):
            errors.append("Skill 'name' is required and must be a string")
        else:
            name_clean = self.name.strip()
            if len(name_clean) < 1 or len(name_clean) > 64:
                errors.append(f"Skill name must be between 1 and 64 characters (got {len(name_clean)})")
            if not NAME_PATTERN.fullmatch(name_clean):
                errors.append(f"Skill name '{self.name}' must be lowercase kebab-case (^[a-z0-9]+(?:-[a-z0-9]+)*$)")
            if name_clean.lower() in WINDOWS_RESERVED_NAMES:
                errors.append(f"Skill name '{self.name}' is reserved by Windows (CON, PRN, AUX, NUL, COM1-9, LPT1-9)")
            if name_clean.lower() in PLATFORM_RESERVED_NAMES:
                errors.append(f"Skill name '{self.name}' is reserved by target platforms (e.g. 'synced')")

        # Description validation
        if not self.description or not isinstance(self.description, str) or not self.description.strip():
            errors.append("Skill 'description' is required and cannot be empty")
        else:
            desc_len = len(self.description.strip())
            if desc_len > 1024:
                errors.append(f"Skill description must be at most 1024 characters (got {desc_len})")

        # Template family
        if self.template_family not in VALID_TEMPLATE_FAMILIES:
            errors.append(
                f"Unknown template family '{self.template_family}'. "
                f"Must be one of: {', '.join(sorted(VALID_TEMPLATE_FAMILIES))}"
            )

        # Compatibility
        if self.compatibility is not None:
            if not isinstance(self.compatibility, str):
                errors.append("'compatibility' must be a string")
            elif len(self.compatibility) > 500:
                errors.append(f"'compatibility' must be at most 500 characters (got {len(self.compatibility)})")

        # Metadata
        if not isinstance(self.metadata, dict):
            errors.append("'metadata' must be a dictionary")
        else:
            for k, v in self.metadata.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    errors.append(f"Metadata key-value pairs must both be strings (found {k}: {v})")

        # Schema version
        if self.schema_version != SCHEMA_VERSION:
            errors.append(f"Unsupported schema_version {self.schema_version}. Expected {SCHEMA_VERSION}")

        return errors

    def validate_or_raise(self) -> None:
        """Validate and raise SpecValidationError if any errors exist."""
        errors = self.validate()
        if errors:
            raise SpecValidationError(errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        d = asdict(self)
        # Ensure schema_version is present
        d["schema_version"] = self.schema_version
        return d

    def to_json(self, indent: int = 2) -> str:
        """Serialize to formatted JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False) + "\n"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillSpec:
        """Create a SkillSpec from a dictionary."""
        cleaned = dict(data)
        # Normalize fields
        if "name" in cleaned and isinstance(cleaned["name"], str):
            cleaned["name"] = cleaned["name"].strip()
        if "description" in cleaned and isinstance(cleaned["description"], str):
            cleaned["description"] = cleaned["description"].strip()
        # Drop unrecognized keys to prevent TypeError on future versions
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered = {k: v for k, v in cleaned.items() if k in valid_fields}
        spec = cls(**filtered)
        return spec

    @classmethod
    def from_json(cls, json_str: str) -> SkillSpec:
        """Deserialize from JSON string."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as err:
            raise SpecValidationError([f"Invalid JSON format: {err}"])
        if not isinstance(data, dict):
            raise SpecValidationError(["Spec root must be a JSON object"])
        return cls.from_dict(data)


def validate_spec_dict(data: Dict[str, Any]) -> List[str]:
    """Validate a dictionary against the Skill Spec schema v1."""
    if not isinstance(data, dict):
        return ["Root specification must be a JSON object"]
    try:
        spec = SkillSpec.from_dict(data)
        return spec.validate()
    except Exception as err:
        return [f"Spec validation error: {err}"]
