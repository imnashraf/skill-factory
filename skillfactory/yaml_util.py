"""Lightweight, safe YAML frontmatter serializer and parser using standard library only.

Fixes DEF-01 by ensuring all YAML frontmatter strings (names, descriptions, hints)
are safely escaped/quoted to prevent YAML syntax errors on colons, hash signs, quotes,
and special characters.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Tuple


class YamlError(ValueError):
    """Raised when YAML frontmatter is missing or malformed."""
    pass


def dump_yaml_scalar(val: Any) -> str:
    """Safely format a scalar value for YAML frontmatter."""
    if val is None:
        return '""'
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        # Plain unquoted identifier: only if simple alphanumeric + hyphens/underscores,
        # not a reserved word like true/false/null/yes/no, and not containing colons or #
        if re.fullmatch(r"[A-Za-z0-9_-]+", val) and val.lower() not in {
            "true", "false", "yes", "no", "null", "on", "off", "y", "n"
        }:
            return val
        # Any string with spaces, colons, quotes, #, or special characters is safely double-quoted
        return json.dumps(val, ensure_ascii=False)
    raise YamlError(f"Unsupported YAML scalar type: {type(val)}")


def dump_frontmatter(data: Dict[str, Any]) -> str:
    """Serialize a dictionary into standard YAML frontmatter enclosed in '---'."""
    lines = ["---"]
    for key, val in data.items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+", str(key)):
            raise YamlError(f"Invalid YAML key: {key}")
        if isinstance(val, dict):
            lines.append(f"{key}:")
            for sub_k, sub_v in val.items():
                if not re.fullmatch(r"[A-Za-z0-9_-]+", str(sub_k)):
                    raise YamlError(f"Invalid YAML sub-key: {sub_k}")
                lines.append(f"  {sub_k}: {dump_yaml_scalar(sub_v)}")
        elif isinstance(val, list):
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {dump_yaml_scalar(item)}")
        else:
            lines.append(f"{key}: {dump_yaml_scalar(val)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


# Alias for compatibility
safe_dump_frontmatter = dump_frontmatter


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter and markdown body from markdown text.

    Returns:
        (frontmatter_dict, markdown_body)

    Raises:
        YamlError: If frontmatter is missing, unclosed, or invalid.
    """
    if not text.startswith("---"):
        raise YamlError("Document does not start with YAML frontmatter delimiter '---'")

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise YamlError("Document does not start with '---' on the first line")

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        raise YamlError("YAML frontmatter is not closed with '---'")

    yaml_lines = lines[1:end_idx]
    markdown_body = "".join(lines[end_idx + 1:])

    result: Dict[str, Any] = {}
    current_key: str | None = None
    current_subdict: Dict[str, Any] | None = None
    current_list: list[Any] | None = None
    multiline_key: str | None = None
    multiline_lines: list[str] = []

    def _flush_multiline():
        nonlocal multiline_key, multiline_lines
        if multiline_key is not None:
            # Join folded multiline text
            joined = " ".join(line.strip() for line in multiline_lines).strip()
            if current_subdict is not None:
                current_subdict[multiline_key] = joined
            else:
                result[multiline_key] = joined
            multiline_key = None
            multiline_lines = []

    def _parse_scalar(raw: str) -> Any:
        raw = raw.strip()
        if not raw:
            return ""
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            if raw.startswith('"'):
                try:
                    return json.loads(raw)
                except Exception:
                    return raw[1:-1]
            else:
                # Single-quoted string: replace '' with '
                return raw[1:-1].replace("''", "'")
        if raw.lower() in ("true", "yes", "on"):
            return True
        if raw.lower() in ("false", "no", "off"):
            return False
        if raw.lower() in ("null", "~"):
            return None
        # Try integer
        if re.fullmatch(r"[-+]?\d+", raw):
            try:
                return int(raw)
            except ValueError:
                pass
        # Try float
        if re.fullmatch(r"[-+]?\d+\.\d+", raw):
            try:
                return float(raw)
            except ValueError:
                pass
        return raw

    for line_idx, raw_line in enumerate(yaml_lines):
        line = raw_line.rstrip("\r\n")
        stripped = line.strip()

        # Skip empty lines and comment lines
        if not stripped or stripped.startswith("#"):
            continue

        # Check for multiline continuation
        if multiline_key is not None:
            if line.startswith("  ") or line.startswith("\t"):
                multiline_lines.append(line.strip())
                continue
            else:
                _flush_multiline()

        # Check for nested dict entry: "  subkey: value"
        if line.startswith("  ") and not line.startswith("  - "):
            if current_subdict is None or current_key is None:
                raise YamlError(f"Unexpected indentation at frontmatter line {line_idx + 2}: {line}")
            sub_line = line.strip()
            if ":" not in sub_line:
                raise YamlError(f"Invalid key-value pair in frontmatter: {line}")
            sub_k, sub_v = sub_line.split(":", 1)
            sub_k = sub_k.strip()
            sub_v = sub_v.strip()
            if sub_v in (">", ">-", "|", "|-"):
                multiline_key = sub_k
                multiline_lines = []
            else:
                current_subdict[sub_k] = _parse_scalar(sub_v)
            continue

        # Check for list entry: "  - value"
        if line.startswith("  - ") or line.startswith("- "):
            if current_list is None:
                raise YamlError(f"Unexpected list item in frontmatter at line {line_idx + 2}: {line}")
            val = line.split("-", 1)[1].strip()
            current_list.append(_parse_scalar(val))
            continue

        # Top level line
        _flush_multiline()
        current_subdict = None
        current_list = None

        if ":" not in line:
            raise YamlError(f"Malformed YAML line (missing ':'): {line}")

        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()

        if not v:
            # Could be start of a nested dictionary or list
            # We look ahead or determine on next line; initialize subdict by default
            current_key = k
            current_subdict = {}
            result[k] = current_subdict
        elif v in (">", ">-", "|", "|-"):
            current_key = k
            multiline_key = k
            multiline_lines = []
        else:
            current_key = k
            result[k] = _parse_scalar(v)

    _flush_multiline()
    return result, markdown_body
