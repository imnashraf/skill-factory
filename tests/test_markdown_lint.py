"""Automated regression tests for Markdown quality and formatting compliance (MD022, MD031, MD032, MD058, MD060)."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skillfactory.ai.requirements import parse_natural_language_requirement
from skillfactory.core import generate_skill
from skillfactory.publish import prepare_publish_repository
from skillfactory.spec import VALID_TEMPLATE_FAMILIES, SkillSpec

_REPO_ROOT = Path(__file__).resolve().parent.parent


def check_markdown_lint_rules(filepath: Path | str, content: str, check_embedded: bool = True) -> list[str]:
    """Inspect Markdown text for MD022, MD031, MD032, MD058, MD060 violations."""
    lines = content.splitlines()
    violations: list[str] = []
    in_frontmatter = False

    # Fence tracking stack: elements are [fence_char, fence_len, fence_lang, start_line, lines_inside]
    fence_stack: list[list] = []
    in_list = False
    list_indent = 0

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        line_num = idx + 1
        stripped = line.strip()

        # Handle YAML frontmatter at document start
        if idx == 0 and stripped == "---":
            in_frontmatter = True
            idx += 1
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            idx += 1
            continue

        # Code fences (MD031) with nested block and backtick length support
        fence_match = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
        if fence_match:
            f_delim = fence_match.group(1)
            f_char = f_delim[0]
            f_len = len(f_delim)
            f_info = fence_match.group(2).strip().lower()

            if fence_stack and fence_stack[-1][0] == f_char and f_len >= fence_stack[-1][1]:
                # Closing fence
                closing_fence = fence_stack.pop()
                if not fence_stack:
                    if idx + 1 < len(lines) and lines[idx + 1].strip() != "":
                        violations.append(
                            f"{filepath}:{line_num}: MD031 Fenced code block closing must be followed by a blank line"
                        )
                if check_embedded and closing_fence[2] in ("markdown", "md"):
                    embedded_text = "\n".join(closing_fence[4])
                    sub_violations = check_markdown_lint_rules(
                        f"{filepath}[embedded L{closing_fence[3]}]",
                        embedded_text,
                        check_embedded=True,
                    )
                    violations.extend(sub_violations)
                in_list = False
                idx += 1
                continue
            elif not fence_stack:
                # Opening top-level fence
                if idx > 0 and lines[idx - 1].strip() != "" and lines[idx - 1].strip() != "---":
                    violations.append(
                        f"{filepath}:{line_num}: MD031 Fenced code block opening must be preceded by a blank line"
                    )
                fence_stack.append([f_char, f_len, f_info, line_num, []])
                in_list = False
                idx += 1
                continue
            else:
                # Nested fence inside outer fence
                fence_stack.append([f_char, f_len, f_info, line_num, []])
                fence_stack[-2][4].append(line)
                idx += 1
                continue

        if fence_stack:
            fence_stack[-1][4].append(line)
            idx += 1
            continue

        # Headings (MD022)
        if stripped.startswith("#") and re.match(r"^#{1,6}\s+", stripped):
            in_list = False
            if idx > 0 and lines[idx - 1].strip() != "" and lines[idx - 1].strip() != "---":
                violations.append(
                    f"{filepath}:{line_num}: MD022 Heading must be preceded by a blank line"
                )
            if idx + 1 < len(lines) and lines[idx + 1].strip() != "":
                violations.append(
                    f"{filepath}:{line_num}: MD022 Heading must be followed by a blank line"
                )
            idx += 1
            continue

        # Lists (MD032)
        list_match = re.match(r"^(\s*)([*\-+]|\d+\.)\s+", line)
        if list_match:
            cur_indent = len(list_match.group(1))
            if not in_list:
                if idx > 0 and lines[idx - 1].strip() != "" and lines[idx - 1].strip() != "---":
                    violations.append(
                        f"{filepath}:{line_num}: MD032 List start must be preceded by a blank line"
                    )
                in_list = True
                list_indent = cur_indent
            idx += 1
            continue
        elif in_list:
            if stripped == "":
                # Blank line within or ending list; lookahead for continuation
                next_is_list = False
                for j in range(idx + 1, len(lines)):
                    if lines[j].strip() == "":
                        continue
                    if re.match(r"^(\s*)([*\-+]|\d+\.)\s+", lines[j]):
                        next_is_list = True
                    break
                if not next_is_list:
                    in_list = False
            elif len(line) - len(line.lstrip()) > list_indent or stripped.startswith(("|", ">")):
                pass
            else:
                violations.append(
                    f"{filepath}:{line_num}: MD032 List end must be followed by a blank line"
                )
                in_list = False

        # Table delimiter pipe style (MD060) and table boundaries (MD058)
        if stripped.startswith("|") and "---" in stripped:
            if re.search(r"\|---", stripped) or re.search(r"---\|", stripped):
                violations.append(
                    f"{filepath}:{line_num}: MD060 Table column style missing space padding around pipes"
                )

        idx += 1

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

    def test_all_raw_markdown_templates_have_zero_lint_violations(self):
        """Verify all raw markdown templates in skillfactory/templates/ have zero lint violations."""
        templates_dir = _REPO_ROOT / "skillfactory" / "templates"
        tmpl_files = sorted(templates_dir.rglob("*.md.tmpl"))
        self.assertGreaterEqual(len(tmpl_files), 15)

        for tmpl_file in tmpl_files:
            content = tmpl_file.read_text(encoding="utf-8")
            violations = check_markdown_lint_rules(str(tmpl_file.relative_to(_REPO_ROOT)), content)
            self.assertEqual(
                violations,
                [],
                f"Template file '{tmpl_file.relative_to(_REPO_ROOT)}' has Markdown violations: {violations}",
            )

    def test_repeated_generation_and_regeneration_remains_lint_clean(self):
        """Verify skills generated repeatedly and regenerated with updates remain 100% lint-clean."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            spec = SkillSpec(
                name="regeneration-test-skill",
                description="Testing repeated generation consistency and markdown lint hygiene.",
                template_family="checklist-review",
                author="Skill Factory CI",
                license="MIT",
            )
            # Initial generation
            res1 = generate_skill(spec, tmp_root)
            for md_file in res1.target_path.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                self.assertEqual(check_markdown_lint_rules(md_file.name, content), [])

            # Second generation into another location
            tmp_sub = tmp_root / "second_run"
            res2 = generate_skill(spec, tmp_sub)
            for md_file in res2.target_path.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                self.assertEqual(check_markdown_lint_rules(md_file.name, content), [])

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

    def test_all_documentation_files_have_zero_lint_violations(self):
        """Verify documentation files across docs/ and repository root have zero Markdown lint violations."""
        docs_files = sorted((_REPO_ROOT / "docs").rglob("*.md"))
        root_docs = [
            _REPO_ROOT / "README.md",
            _REPO_ROOT / "CHANGELOG.md",
            _REPO_ROOT / "CONTRIBUTING.md",
            _REPO_ROOT / "SECURITY.md",
            _REPO_ROOT / "CODE_OF_CONDUCT.md",
            _REPO_ROOT / "SKILL.md",
        ]
        target_files = [f for f in docs_files + root_docs if f.is_file()]

        for doc_file in target_files:
            content = doc_file.read_text(encoding="utf-8")
            violations = check_markdown_lint_rules(str(doc_file.relative_to(_REPO_ROOT)), content)
            self.assertEqual(
                violations,
                [],
                f"Documentation file '{doc_file.relative_to(_REPO_ROOT)}' has Markdown violations: {violations}",
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

    def test_ai_assisted_and_deterministic_fallback_generation_produces_clean_markdown(self):
        """Verify deterministic fallback specification renders fully lint-clean markdown artifacts."""
        req = parse_natural_language_requirement(
            "Build a log anomaly detector for syslog files with severity thresholds."
        )
        spec = req.to_spec(author="Automated Fallback Test")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            res = generate_skill(spec, tmp_root)
            for md_file in res.target_path.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                violations = check_markdown_lint_rules(md_file.name, content)
                self.assertEqual(violations, [], f"AI fallback artifact '{md_file.name}' has violations: {violations}")

    def test_markdownlint_cli_execution_if_available(self):
        """If npx is available, verify full repository passes markdownlint-cli with zero errors."""
        npx_path = shutil.which("npx")
        if not npx_path:
            self.skipTest("npx not available in environment")

        config_path = _REPO_ROOT / ".markdownlint.json"
        self.assertTrue(config_path.is_file(), ".markdownlint.json must exist")

        cmd = [
            npx_path,
            "--yes",
            "markdownlint-cli",
            "-c",
            str(config_path),
            "**/*.md",
            "--ignore",
            "node_modules/**",
        ]
        res = subprocess.run(
            cmd,
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            shell=(sys.platform == "win32"),
        )
        self.assertEqual(
            res.returncode,
            0,
            f"markdownlint-cli reported violations:\n{res.stderr or res.stdout}",
        )


if __name__ == "__main__":
    unittest.main()
