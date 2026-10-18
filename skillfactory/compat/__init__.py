"""Multi-agent platform compatibility and detection for Skill Factory."""

from skillfactory.compat.platform_db import (
    get_all_platforms,
    get_platform,
    get_project_skill_paths,
    get_reserved_names,
    get_user_skill_path,
    load_platforms_db,
)

__all__ = [
    "load_platforms_db",
    "get_platform",
    "get_all_platforms",
    "get_project_skill_paths",
    "get_user_skill_path",
    "get_reserved_names",
]
