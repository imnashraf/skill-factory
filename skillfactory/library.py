"""Local skill catalog indexer and offline search engine (Phase 6, Tasks T6.01, T6.02).

Scans directories for Agent Skills, extracts metadata and quality scores, builds
searchable `index.json`, and provides lightning-fast offline search (< 100ms) (AC6.01, AC6.02).
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from skillfactory.yaml_util import parse_frontmatter


@dataclass
class CatalogEntry:
    name: str
    description: str
    path: str
    version: str = "0.1.0"
    template_family: str = "python-script"
    compatibility: str = ""
    tags: List[str] = field(default_factory=list)
    author: str = ""
    license: str = "MIT"
    eval_score: Optional[int] = None
    grade: Optional[str] = None
    has_scripts: bool = False
    has_tests: bool = False
    security_status: str = "Unverified"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CatalogIndex:
    skills: List[CatalogEntry]
    source_dir: str
    total_skills: int
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_dir": self.source_dir,
            "total_skills": self.total_skills,
            "updated_at": self.updated_at,
            "skills": [s.to_dict() for s in self.skills],
        }

    def save(self, output_path: Path) -> Path:
        out = Path(output_path)
        out.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        return out

    @classmethod
    def load(cls, index_path: Path) -> CatalogIndex:
        path = Path(index_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        skills = [CatalogEntry(**s) for s in data.get("skills", [])]
        return cls(
            skills=skills,
            source_dir=data.get("source_dir", ""),
            total_skills=data.get("total_skills", len(skills)),
            updated_at=data.get("updated_at", ""),
        )


def load_bundled_catalog() -> CatalogIndex:
    """Load the built-in reference skills catalog (Phase 13, AC13.01)."""
    catalog_path = Path(__file__).parent / "data" / "catalog.json"
    if catalog_path.is_file():
        try:
            data = json.loads(catalog_path.read_text(encoding="utf-8"))
            skills = [CatalogEntry(**s) for s in data.get("skills", [])]
            return CatalogIndex(
                skills=skills,
                source_dir=str(catalog_path),
                total_skills=len(skills),
                updated_at=data.get("updated_at", ""),
            )
        except Exception:
            pass
    return CatalogIndex(skills=[], source_dir="", total_skills=0, updated_at="")


def _extract_tags(name: str, description: str, metadata: Dict[str, Any]) -> List[str]:
    """Derive search tags from skill name, description, and metadata."""
    tags: Set[str] = set()

    # Name tokens
    for token in name.split("-"):
        if len(token) > 2:
            tags.add(token.lower())

    # Metadata tags
    meta_tags = metadata.get("tags") or metadata.get("keywords")
    if isinstance(meta_tags, list):
        for t in meta_tags:
            tags.add(str(t).lower())
    elif isinstance(meta_tags, str):
        for t in meta_tags.split(","):
            tags.add(t.strip().lower())

    # Common domain keyword extraction
    keywords = [
        "python",
        "api",
        "git",
        "docker",
        "pdf",
        "test",
        "sql",
        "database",
        "json",
        "yaml",
        "markdown",
        "security",
        "audit",
        "lint",
        "benchmark",
        "data",
        "pipeline",
        "cli",
    ]
    desc_lower = description.lower()
    for kw in keywords:
        if kw in desc_lower:
            tags.add(kw)

    return sorted(tags)


def index_directory(skills_root: Path, include_eval: bool = False) -> CatalogIndex:
    """Scan a directory for Agent Skills and build a searchable CatalogIndex.

    Args:
        skills_root: Directory containing skill subdirectories.
        include_eval: If True, calculates or reads evaluation scores.

    Returns:
        CatalogIndex with all discovered skills.
    """
    root = Path(skills_root).resolve()
    entries: List[CatalogEntry] = []

    if not root.exists() or not root.is_dir():
        return CatalogIndex(
            skills=[],
            source_dir=str(root),
            total_skills=0,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    for item in sorted(root.iterdir()):
        if not item.is_dir():
            continue

        skill_md = item / "SKILL.md"
        if not skill_md.exists():
            continue

        try:
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            fm, _ = parse_frontmatter(content)
        except Exception:
            continue

        name = fm.get("name") or item.name
        description = fm.get("description") or ""
        metadata = fm.get("metadata", {}) if isinstance(fm.get("metadata"), dict) else {}
        compatibility = fm.get("compatibility") or ""

        version = metadata.get("version", "0.1.0")
        author = metadata.get("author", "")
        template_family = metadata.get("template_family", "python-script")

        # Check existing evaluation or manifest
        eval_score: Optional[int] = None
        grade: Optional[str] = None
        eval_file = item / ".skillfactory" / "evaluation.json"
        if eval_file.exists():
            try:
                eval_data = json.loads(eval_file.read_text(encoding="utf-8"))
                eval_score = eval_data.get("total_score")
                grade = eval_data.get("grade")
            except Exception:
                pass
        elif include_eval:
            try:
                from skillfactory.eval import evaluate_skill
                rep = evaluate_skill(item, run_tests=False, save_report=False)
                eval_score = rep.total_score
                grade = rep.grade
            except Exception:
                pass

        has_scripts = (item / "scripts").is_dir() and any((item / "scripts").iterdir())
        has_tests = (item / "tests").is_dir() and any((item / "tests").iterdir())
        tags = _extract_tags(name, description, metadata)

        entries.append(
            CatalogEntry(
                name=name,
                description=description,
                path=str(item),
                version=version,
                template_family=template_family,
                compatibility=compatibility,
                tags=tags,
                author=author,
                license="MIT",
                eval_score=eval_score,
                grade=grade,
                has_scripts=has_scripts,
                has_tests=has_tests,
            )
        )

    return CatalogIndex(
        skills=entries,
        source_dir=str(root),
        total_skills=len(entries),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


def search_catalog(
    index: CatalogIndex,
    query: str,
    tag_filter: Optional[str] = None,
) -> List[Tuple[CatalogEntry, int]]:
    """Search skills in a CatalogIndex offline with ranking (< 100ms, AC6.02).

    Returns:
        List of (CatalogEntry, relevance_score) sorted by highest relevance.
    """
    start_time = time.monotonic()
    query_tokens = [t.lower() for t in query.strip().split() if t]
    tag_filter_clean = tag_filter.lower().strip() if tag_filter else None

    results: List[Tuple[CatalogEntry, int]] = []

    for entry in index.skills:
        if tag_filter_clean and tag_filter_clean not in [t.lower() for t in entry.tags]:
            continue

        if not query_tokens:
            results.append((entry, 1))
            continue

        score = 0
        name_lower = entry.name.lower()
        desc_lower = entry.description.lower()
        tags_lower = [t.lower() for t in entry.tags]

        # Exact name match gets highest score
        if " ".join(query_tokens) == name_lower:
            score += 100

        for token in query_tokens:
            if token == name_lower:
                score += 50
            elif token in name_lower:
                score += 30
            elif any(token == t for t in tags_lower):
                score += 20
            elif any(token in t for t in tags_lower):
                score += 10
            elif token in desc_lower:
                score += 5

        if score > 0:
            results.append((entry, score))

    # Sort descending by score, then alphabetically by name
    results.sort(key=lambda x: (-x[1], x[0].name))
    return results
