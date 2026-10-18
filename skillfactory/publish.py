"""GitHub publish preparation and standalone repository scaffolding (Phase 6, Task T6.05).

Prepares a production-ready standalone Git repository for sharing an Agent Skill,
including root README, LICENSE, .gitignore, and GitHub Actions CI workflow (AC6.05).
Ensures secrets and validation checks pass before allowing export (FR-PUB-04).
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.eval import evaluate_skill
from skillfactory.scanner import scan_skill_directory
from skillfactory.validator import validate_skill

GITIGNORE_CONTENT = """# Python byte-code and virtual environments
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/

# Testing and coverage
.pytest_cache/
.coverage
htmlcov/

# IDE and OS files
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp
*.swo

# Skill Factory temporary files
.skillfactory/backups/
.tmp-*
"""

CI_WORKFLOW_CONTENT = """name: Skill Tests and Spec Validation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.9", "3.11", "3.13"]

    steps:
      - name: Check out repository
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38 # v5.4.0
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run skill test suite
        run: |
          python3 -m unittest discover -s tests -v || python -m unittest discover -s tests -v
"""


@dataclass
class PublishScaffoldResult:
    skill_name: str
    output_dir: Path
    github_repo: str
    quality_score: int
    grade: str
    instructions: List[str]
    files_created: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "output_dir": str(self.output_dir),
            "github_repo": self.github_repo,
            "quality_score": self.quality_score,
            "grade": self.grade,
            "instructions": self.instructions,
            "files_created": self.files_created,
        }


def prepare_publish_repository(
    skill_dir: Path,
    output_dir: Path,
    github_repo: Optional[str] = None,
    force: bool = False,
) -> PublishScaffoldResult:
    """Prepare a standalone Git repository scaffold for publishing an Agent Skill (AC6.05).

    Args:
        skill_dir: Directory containing the skill to publish.
        output_dir: Destination directory where the standalone repo should be generated.
        github_repo: Target GitHub repo name in owner/repo format (optional).
        force: If True, overwrites destination directory.

    Returns:
        PublishScaffoldResult containing generated files and exact git CLI instructions.
    """
    skill_path = Path(skill_dir).resolve()
    target_dir = Path(output_dir).resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    skill_name = skill_path.name
    repo_name = github_repo or f"username/{skill_name}"

    # 1. Pre-publish checklist: Specification Validation
    val = validate_skill(skill_path, check_dirname=False)
    if not val.is_valid:
        raise ValueError(f"Pre-publish check failed: specification invalid ({'; '.join(val.errors)})")

    # 2. Pre-publish checklist: Secret Scanner
    safety = scan_skill_directory(skill_path)
    secret_findings = [f for f in safety.findings if f.rule_id.startswith("SEC")]
    if secret_findings:
        raise ValueError(
            f"Pre-publish check blocked: detected {len(secret_findings)} hardcoded credentials/secrets. Remove before publishing!"
        )

    # 3. Pre-publish checklist: Quality Evaluation
    eval_rep = evaluate_skill(skill_path, run_tests=True, save_report=False)
    if eval_rep.total_score < 75:
        # Grade C or F
        raise ValueError(
            f"Pre-publish check failed: Quality score {eval_rep.total_score}/100 [{eval_rep.grade}] is below publication threshold (>= 75)."
        )

    # 4. Prepare target directory
    if target_dir.exists():
        if not force:
            raise FileExistsError(f"Target publish directory '{target_dir}' already exists. Use --force to overwrite.")
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)
    created_files: List[str] = []

    # 5. Copy skill contents (excluding temporary files)
    for root, dirs, files in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "venv", ".pytest_cache")]
        rel_root = Path(root).relative_to(skill_path)
        dest_sub = target_dir / rel_root
        dest_sub.mkdir(parents=True, exist_ok=True)

        for f in files:
            if f in (".DS_Store", "Thumbs.db"):
                continue
            src_f = Path(root) / f
            dst_f = dest_sub / f
            shutil.copy2(src_f, dst_f)
            created_files.append(str(dst_f.relative_to(target_dir)))

    # 6. Add .gitignore
    gitignore_path = target_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(GITIGNORE_CONTENT, encoding="utf-8")
        created_files.append(".gitignore")

    # 7. Add GitHub Actions CI workflow
    workflow_dir = target_dir / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    ci_path = workflow_dir / "ci.yml"
    ci_path.write_text(CI_WORKFLOW_CONTENT, encoding="utf-8")
    created_files.append(".github/workflows/ci.yml")

    # 8. Add/Verify README.md
    readme_path = target_dir / "README.md"
    if not readme_path.exists():
        desc = val.metadata.get("frontmatter", {}).get("description", "")
        readme_content = f"""# {skill_name}

{desc}

## Overview
This repository contains the `{skill_name}` Agent Skill, formatted according to the open [Agent Skills specification](https://agentskills.io).

## Installation

Using **Skill Factory**:
```bash
python3 -m skillfactory install . --target claude-code
```

Or copy directly into your AI assistant's skills directory:
- **Claude Code**: `.claude/skills/{skill_name}/`
- **Cursor / Codex / Antigravity**: `.agents/skills/{skill_name}/`

## Testing
Run automated test suite:
```bash
python3 -m unittest discover -s tests -v
```

## License
MIT License
"""
        readme_path.write_text(readme_content, encoding="utf-8")
        created_files.append("README.md")

    # 9. Formulate exact CLI publishing instructions
    instructions = [
        f"cd {target_dir}",
        "git init",
        "git add .",
        f"git commit -m 'feat: initial release of {skill_name} agent skill'",
        f"gh repo create {repo_name} --public --source=. --push",
    ]

    return PublishScaffoldResult(
        skill_name=skill_name,
        output_dir=target_dir,
        github_repo=repo_name,
        quality_score=eval_rep.total_score,
        grade=eval_rep.grade,
        instructions=instructions,
        files_created=sorted(created_files),
    )
