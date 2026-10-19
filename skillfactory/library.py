"""Local skill catalog indexer and offline search engine (Phases 6 & 17, Workstreams 17A, 17B).

Scans directories for Agent Skills, extracts metadata and quality scores, builds
searchable `index.json`, provides multi-attribute filtering (domain, category,
platform, grade, type), and lightning-fast offline search (< 10ms).
"""
from __future__ import annotations

import copy
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from skillfactory.yaml_util import parse_frontmatter

# 3-Tier Domain Taxonomy Definition (Phase 17, Workstream 17A)
DEFAULT_TAXONOMY: Dict[str, List[str]] = {
    "Personal": [
        "Productivity",
        "Learning",
        "File management",
        "Research",
        "Travel",
        "Personal administration",
    ],
    "Professional": [
        "Finance",
        "Accounting",
        "Human resources",
        "Payroll",
        "Procurement",
        "Supply chain",
        "Project management",
        "ERP",
        "Real estate",
        "Education",
        "Legal operations",
        "Healthcare administration",
        "Public administration",
    ],
    "Developer and AI": [
        "Software engineering",
        "Cybersecurity",
        "DevOps",
        "Testing",
        "Data engineering",
        "AI engineering",
        "Agent orchestration",
        "Documentation",
        "Release management",
    ],
}

_ACTIVE_TAXONOMY: Dict[str, List[str]] = copy.deepcopy(DEFAULT_TAXONOMY)


def register_custom_domain(domain_name: str, categories: List[str]) -> None:
    """Register or extend a domain category dynamically without breaking architecture."""
    clean_domain = domain_name.strip()
    clean_cats = [c.strip() for c in categories if c.strip()]
    if clean_domain in _ACTIVE_TAXONOMY:
        for c in clean_cats:
            if c not in _ACTIVE_TAXONOMY[clean_domain]:
                _ACTIVE_TAXONOMY[clean_domain].append(c)
    else:
        _ACTIVE_TAXONOMY[clean_domain] = clean_cats


def get_taxonomy() -> Dict[str, List[str]]:
    """Return the active 3-tier domain taxonomy."""
    return copy.deepcopy(_ACTIVE_TAXONOMY)


def reset_taxonomy() -> None:
    """Reset taxonomy to standard defaults."""
    global _ACTIVE_TAXONOMY
    _ACTIVE_TAXONOMY = copy.deepcopy(DEFAULT_TAXONOMY)


@dataclass
class CatalogEntry:
    name: str
    description: str
    path: str
    version: str = "0.1.0"
    template_family: str = "python-script"
    compatibility: str = ""
    domain: str = "Developer and AI"
    category: str = "General"
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
        skills = []
        for s in data.get("skills", []):
            if "domain" not in s or not s["domain"]:
                cat = s.get("category", "")
                if cat.lower() == "personal":
                    s["domain"] = "Personal"
                elif cat.lower() == "professional":
                    s["domain"] = "Professional"
                elif cat.lower() == "developer":
                    s["domain"] = "Developer and AI"
                else:
                    dom, _ = _classify_skill_domain(s.get("name", ""), s.get("description", ""))
                    s["domain"] = dom
            skills.append(CatalogEntry(**s))
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
            return CatalogIndex.load(catalog_path)
        except Exception:
            pass
    return CatalogIndex(skills=[], source_dir="", total_skills=0, updated_at="")


def _extract_tags(name: str, description: str, metadata: Dict[str, Any]) -> List[str]:
    """Derive search tags from skill name, description, and metadata."""
    tags: Set[str] = set()

    for token in name.split("-"):
        if len(token) > 2:
            tags.add(token.lower())

    meta_tags = metadata.get("tags") or metadata.get("keywords")
    if isinstance(meta_tags, list):
        for t in meta_tags:
            tags.add(str(t).lower())
    elif isinstance(meta_tags, str):
        for t in meta_tags.split(","):
            tags.add(t.strip().lower())

    keywords = [
        "python", "api", "git", "docker", "pdf", "test", "sql", "database",
        "json", "yaml", "markdown", "security", "audit", "lint", "benchmark",
        "data", "pipeline", "cli", "excel", "attendance", "invoice", "raid"
    ]
    desc_lower = description.lower()
    for kw in keywords:
        if kw in desc_lower:
            tags.add(kw)

    return sorted(tags)


def _classify_skill_domain(name: str, desc: str, explicit_domain: Optional[str] = None) -> Tuple[str, str]:
    """Classify a skill into the 3-tier taxonomy."""
    if explicit_domain:
        return explicit_domain, "General"

    lower = (name + " " + desc).lower()
    if any(k in lower for k in ("invoice", "finance", "financial", "attendance", "timesheet", "payroll")):
        return "Professional", "Finance & Workforce"
    elif any(k in lower for k in ("raid", "project", "milestone", "agile", "status")):
        return "Professional", "Project Management"
    elif any(k in lower for k in ("excel", "csv", "organizer", "file", "notes")):
        return "Personal", "Productivity"
    elif any(k in lower for k in ("security", "config", "scanner", "test", "inventory", "dependency", "manifest", "markdown")):
        return "Developer and AI", "Cybersecurity & DevOps"
    return "Developer and AI", "Software Engineering"


def index_directory(skills_root: Path, include_eval: bool = False) -> CatalogIndex:
    """Scan a directory for Agent Skills and build a searchable CatalogIndex."""
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
        explicit_domain = metadata.get("domain")

        domain, category = _classify_skill_domain(name, description, explicit_domain)

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
                domain=domain,
                category=category,
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
    query: str = "",
    tag_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    domain_filter: Optional[str] = None,
    platform_filter: Optional[str] = None,
    grade_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
) -> List[Tuple[CatalogEntry, int]]:
    """Search skills in a CatalogIndex offline with multi-attribute ranking (< 10ms, Workstream 17B).

    Returns:
        List of (CatalogEntry, relevance_score) sorted by highest relevance.
    """
    query_tokens = [t.lower() for t in query.strip().split() if t]
    tag_clean = tag_filter.lower().strip() if tag_filter else None
    cat_clean = category_filter.lower().strip() if category_filter else None
    dom_clean = domain_filter.lower().strip() if domain_filter else None
    plat_clean = platform_filter.lower().strip() if platform_filter else None
    grade_clean = grade_filter.upper().strip() if grade_filter else None
    type_clean = type_filter.lower().strip() if type_filter else None

    results: List[Tuple[CatalogEntry, int]] = []

    for entry in index.skills:
        # Multi-attribute filtering
        if tag_clean and tag_clean not in [t.lower() for t in entry.tags]:
            continue

        if cat_clean and cat_clean not in entry.category.lower():
            continue

        if dom_clean and dom_clean not in entry.domain.lower():
            continue

        if plat_clean and plat_clean not in entry.compatibility.lower() and entry.compatibility != "":
            continue

        if grade_clean:
            entry_grade = (entry.grade or "").upper().replace("GRADE", "").strip()
            clean_target = grade_clean.upper().replace("GRADE", "").strip()
            if clean_target and clean_target != entry_grade:
                continue

        if type_clean and type_clean not in entry.template_family.lower():
            continue

        # If no query keyword, accept with base score
        if not query_tokens:
            results.append((entry, 1))
            continue

        score = 0
        name_lower = entry.name.lower()
        desc_lower = entry.description.lower()
        tags_lower = [t.lower() for t in entry.tags]

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

    results.sort(key=lambda x: (-x[1], x[0].name))
    return results
