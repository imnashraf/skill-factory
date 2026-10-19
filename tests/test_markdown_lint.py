"""Automated regression tests for Markdown quality and formatting compliance (MD022, MD031, MD032, MD058, MD060)."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from skillfactory.ai.requirements import parse_natural_language_requirement
from skillfactory.core import generate_skill
from skillfactory.publish import prepare_publish_repository
from skillfactory.spec import VALID_TEMPLATE_FAMILIES, SkillSpec

_REPO_ROOT = Path(__file__).resolve().parent.parent


def check_markdown_lint_rules(filepath: Path | str, content: str) -> list[str]:
    """Inspect Markdown text for MD022, MD031, MD032, MD058, MD060 violations."""
    lines = content.splitlines()
    violations = []
    in_frontmatter = False
    in_fence = False

    for idx, line in enumerate(lines):
        line_num = idx + 1
        stripped = line.strip()

        # Handle YAML frontmatter
        if idx == 0 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue

        # Handle Code Fences (MD031)
        if stripped.startswith("```"):
            if not in_fence:
                # Opening fence: previous line must be blank if not at start
                if idx > 0 and lines[idx - 1].strip() != "" and not lines[idx - 1].strip() == "---":
                    violations.append(
                        f"{filepath}:{line_num}: MD031 Fenced code block opening must be preceded by a blank line"
                    )
                in_fence = True
            else:
                # Closing fence: next line must be blank if not at end
                if idx + 1 < len(lines) and lines[idx + 1].strip() != "":
                    violations.append(
                        f"{filepath}:{line_num}: MD031 Fenced code block closing must be followed by a blank line"
                    )
                in_fence = False
            continue

        if in_fence:
            continue

        # Handle Headings (MD022)
        if stripped.startswith("#") and re.match(r"^#{1,6}\s+", stripped):
            # Preceding line must be blank unless at start or after frontmatter
            if idx > 0 and lines[idx - 1].strip() != "" and lines[idx - 1].strip() != "---":
                violations.append(
                    f"{filepath}:{line_num}: MD022 Heading must be preceded by a blank line"
                )
            # Following line must be blank unless at end
            if idx + 1 < len(lines) and lines[idx + 1].strip() != "":
                violations.append(
                    f"{filepath}:{line_num}: MD022 Heading must be followed by a blank line"
                )
            continue

        # Handle Lists (MD032)
        is_list = bool(re.match(r"^\s*([*\-+]|\d+\.)\s+", line))
        prev_is_list = bool(idx > 0 and re.match(r"^\s*([*\-+]|\d+\.)\s+", lines[idx - 1]))
        next_is_list = bool(idx + 1 < len(lines) and re.match(r"^\s*([*\-+]|\d+\.)\s+", lines[idx + 1]))

        if is_list and not prev_is_list:
            if idx > 0 and lines[idx - 1].strip() != "":
                violations.append(
                    f"{filepath}:{line_num}: MD032 List start must be preceded by a blank line"
                )
        if is_list and not next_is_list:
            if idx + 1 < len(lines) and lines[idx + 1].strip() != "":
                violations.append(
                    f"{filepath}:{line_num}: MD032 List end must be followed by a blank line"
                )

        # Handle Table delimiter pipe style (MD060) and table boundaries (MD058)
        if stripped.startswith("|") and "---" in stripped:
            if re.search(r"\|---", stripped) or re.search(r"---\|", stripped):
                violations.append(
                    f"{filepath}:{line_num}: MD060 Table column style missing space padding around pipes"
                )

    return violations


class MarkdownQualityRegressionTests(unittest.TestCase):
    """Verify that all repository documentation, skills, and templates comply with markdown lint rules."""

    def test_all_five_template_families_generate_lint_clean_markdown(self):
        """Verify generated skills from all 5 template families have zero lint violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            for family in sorted(VALID_TEMPLATE_FAMILIES):
                spec = SkillSpec(
                    name=f"lint-check-{family}",
                    description=f"Automated quality test skill for {family} family.",
                    template_family=family,
                    author="Skill Factory CI",
                    license="MIT",
                )
                res = generate_skill(spec, tmp_root)
                md_files = list(res.target_path.rglob("*.md"))
                self.assertGreaterEqual(len(md_files), 4)

                for md_file in md_files:
                    content = md_file.read_text(encoding="utf-8")
                    violations = check_markdown_lint_rules(md_file.name, content)
                    self.assertEqual(
                        violations,
                        [],
                        f"Template family '{family}' file '{md_file.name}' has Markdown violations: {violations}",
                    )

    def test_all_examples_have_zero_lint_violations(self):
        """Verify all skills in examples/ have zero Markdown lint violations."""
        examples_dir = _REPO_ROOT / "examples"
        for md_file in sorted(examples_dir.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            violations = check_markdown_lint_rules(str(md_file.relative_to(_REPO_ROOT)), content)
            self.assertEqual(
                violations,
                [],
                f"File '{md_file.relative_to(_REPO_ROOT)}' has Markdown violations: {violations}",
            )

    def test_all_generated_skills_have_zero_lint_violations(self):
        """Verify all reference skills in generated-skills/ have zero Markdown lint violations."""
        gen_dir = _REPO_ROOT / "generated-skills"
        if not gen_dir.exists():
            self.skipTest("generated-skills directory not present")

        for md_file in sorted(gen_dir.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            violations = check_markdown_lint_rules(str(md_file.relative_to(_REPO_ROOT)), content)
            self.assertEqual(
                violations,
                [],
                f"File '{md_file.relative_to(_REPO_ROOT)}' has Markdown violations: {violations}",
            )

    def test_root_skill_md_has_zero_lint_violations(self):
        """Verify root SKILL.md has zero Markdown lint violations."""
        skill_md = _REPO_ROOT / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "Root SKILL.md must exist")
        content = skill_md.read_text(encoding="utf-8")
        violations = check_markdown_lint_rules("SKILL.md", content)
        self.assertEqual(violations, [], f"SKILL.md has violations: {violations}")

    def test_publish_generated_readme_has_zero_lint_violations(self):
        """Verify standalone publish scaffold generates lint-clean README.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            source_skill = _REPO_ROOT / "examples" / "sql-migration-linter"
            target_repo = tmp_root / "published-repo"

            prepare_publish_repository(source_skill, target_repo)
            readme = target_repo / "README.md"
            self.assertTrue(readme.is_file(), "Generated README.md must exist")
            content = readme.read_text(encoding="utf-8")
            violations = check_markdown_lint_rules("published/README.md", content)
            self.assertEqual(violations, [], f"Published README.md has violations: {violations}")

    def test_ai_requirements_to_markdown_has_zero_lint_violations(self):
        """Verify structured requirements to_markdown() complies with all Markdown lint rules."""
        req = parse_natural_language_requirement(
            "Create an attendance CSV validator that detects missing punch-outs and overtime anomalies."
        )
        md = req.to_markdown()
        violations = check_markdown_lint_rules("spec.md", md)
        self.assertEqual(violations, [], f"Requirement spec.to_markdown() has violations: {violations}")

    def test_markdownlint_cli_execution_if_available(self):
        """If npx is available, verify full repository passes markdownlint-cli with zero errors."""
        npx_path = shutil.which("npx")
        if not npx_path:
            self.skipTest("npx not available in environment")

        config_path = _REPO_ROOT / ".markdownlint.json"
        self.assertTrue(config_path.is_file(), ".markdownlint.json must exist")

        all_md_files = [
            str(p)
            for p in _REPO_ROOT.rglob("*.md")
            if "node_modules" not in p.parts and ".git" not in p.parts
        ]

        res = subprocess.run(
            ["npx", "--yes", "markdownlint-cli", "-c", str(config_path)] + all_md_files,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"markdownlint-cli reported violations:\n{res.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
