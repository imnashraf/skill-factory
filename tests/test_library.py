"""Unit tests for Phase 6: Skill Library, Catalog, Packaging, and Publishing (AC6.01–AC6.07)."""
from __future__ import annotations

import json
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

from skillfactory.cli import main
from skillfactory.core import generate_skill
from skillfactory.eval import evaluate_skill
from skillfactory.library import index_directory, search_catalog
from skillfactory.packaging import (
    ZipSecurityError,
    calculate_file_sha256,
    export_skill,
    import_skill,
)
from skillfactory.publish import prepare_publish_repository
from skillfactory.spec import SkillSpec


class LibraryAndPackagingTests(unittest.TestCase):
    def test_catalog_indexer_and_offline_search(self):
        """AC6.01 & AC6.02: Builds searchable index.json and searches offline in < 100ms."""
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            skills_dir.mkdir()

            spec_pdf = SkillSpec(
                name="pdf-parser-tool",
                description="Converts PDF documents into markdown text with tables.",
                template_family="python-script",
            )
            generate_skill(spec_pdf, skills_dir)

            spec_docker = SkillSpec(
                name="docker-guard",
                description="Audits Docker configurations for container security vulnerabilities.",
                template_family="python-script",
            )
            generate_skill(spec_docker, skills_dir)

            # AC6.01: Index directory
            index = index_directory(skills_dir, include_eval=False)
            self.assertEqual(index.total_skills, 2)
            index_file = skills_dir / "index.json"
            index.save(index_file)
            self.assertTrue(index_file.exists())

            # AC6.02: Search execution < 100ms (0.1s)
            start_t = time.monotonic()
            results_docker = search_catalog(index, "docker")
            elapsed = time.monotonic() - start_t
            self.assertLess(elapsed, 0.1)
            self.assertGreaterEqual(len(results_docker), 1)
            self.assertEqual(results_docker[0][0].name, "docker-guard")

            # Search by tag
            results_pdf = search_catalog(index, "pdf")
            self.assertGreaterEqual(len(results_pdf), 1)
            self.assertEqual(results_pdf[0][0].name, "pdf-parser-tool")

    def test_zip_export_and_checksum_verification(self):
        """AC6.03: export creates reproducible .zip package with SHA-256 checksum sidecar."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            dest_dir = Path(tmp) / "dist"
            src_dir.mkdir()
            dest_dir.mkdir()

            spec = SkillSpec(
                name="exportable-skill",
                description="Exports data to external CSV files when requested by user.",
                template_family="python-script",
            )
            gen_res = generate_skill(spec, src_dir)

            zip_target = dest_dir / "exportable-skill.zip"
            export_res = export_skill(gen_res.target_path, output_zip=zip_target, create_sidecar=True)

            self.assertTrue(zip_target.exists())
            self.assertGreater(export_res.size_bytes, 0)
            self.assertTrue(export_res.sha256_hash)

            # Check checksum sidecar
            sidecar = dest_dir / "exportable-skill.zip.sha256"
            self.assertTrue(sidecar.exists())
            sidecar_content = sidecar.read_text(encoding="utf-8")
            self.assertIn(export_res.sha256_hash, sidecar_content)

            # Verify zip content can be read cleanly
            with zipfile.ZipFile(zip_target, "r") as zf:
                namelist = zf.namelist()
                self.assertTrue(any("SKILL.md" in n for n in namelist))
                self.assertTrue(any("README.md" in n for n in namelist))

    def test_safe_import_success(self):
        """Safe zip import extracts, validates, and installs skill."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            dest_dir = Path(tmp) / "imported"
            src_dir.mkdir()
            dest_dir.mkdir()

            spec = SkillSpec(
                name="importable-skill",
                description="Performs safe data transformation when instructed by agent.",
                template_family="python-script",
            )
            gen_res = generate_skill(spec, src_dir)
            zip_target = src_dir / "importable-skill.zip"
            export_res = export_skill(gen_res.target_path, output_zip=zip_target)

            import_res = import_skill(
                zip_target,
                dest_dir=dest_dir,
                verify_checksum=export_res.sha256_hash,
            )
            self.assertEqual(import_res.skill_name, "importable-skill")
            self.assertTrue(import_res.installed_path.exists())
            self.assertTrue((import_res.installed_path / "SKILL.md").exists())
            self.assertTrue(import_res.validation_valid)
            self.assertTrue(import_res.safety_clean)

    def test_zip_slip_rejection(self):
        """AC6.04: Reject malicious archives containing Zip-Slip path traversal (../)."""
        with tempfile.TemporaryDirectory() as tmp:
            malicious_zip = Path(tmp) / "malicious.zip"
            dest_dir = Path(tmp) / "extract_target"
            dest_dir.mkdir()

            # Create a synthetic zip with Zip-Slip path traversal
            with zipfile.ZipFile(malicious_zip, "w") as zf:
                zf.writestr("evil-skill/SKILL.md", "---\nname: evil-skill\ndescription: test\n---\n")
                zf.writestr("../../etc/passwd", "malicious_content")

            with self.assertRaises(ZipSecurityError) as ctx:
                import_skill(malicious_zip, dest_dir=dest_dir)

            self.assertIn("Zip-Slip vulnerability detected", str(ctx.exception))
            # Verify no files escaped to parent
            self.assertFalse((Path(tmp) / "etc" / "passwd").exists())

    def test_publish_scaffolding_generation(self):
        """AC6.05: publish generates standalone Git repository structure with README, license, CI."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            publish_dir = Path(tmp) / "repo-output"
            src_dir.mkdir()

            spec = SkillSpec(
                name="publish-ready-skill",
                description="Validates incoming user files when asked by the agent.",
                template_family="python-script",
            )
            gen_res = generate_skill(spec, src_dir)

            res = prepare_publish_repository(
                skill_dir=gen_res.target_path,
                output_dir=publish_dir,
                github_repo="testuser/publish-ready-skill",
            )

            self.assertTrue(publish_dir.exists())
            self.assertTrue((publish_dir / ".gitignore").exists())
            self.assertTrue((publish_dir / ".github" / "workflows" / "ci.yml").exists())
            self.assertTrue((publish_dir / "README.md").exists())
            self.assertTrue((publish_dir / "LICENSE").exists())
            self.assertTrue((publish_dir / "SKILL.md").exists())
            self.assertIn("git init", res.instructions[1])
            self.assertIn("gh repo create", res.instructions[-1])

    def test_ac8_01_publish_blocked_on_secrets(self):
        """AC8.01: Pre-publish validation blocks export when secrets are present."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            publish_dir = Path(tmp) / "repo-output"
            src_dir.mkdir()

            spec = SkillSpec(
                name="secret-leak-skill",
                description="Attempts to publish with a credential.",
                template_family="python-script",
            )
            gen_res = generate_skill(spec, src_dir)

            # Plant an OpenAI secret in scripts/main.py and re-record manifest so validator passes
            script_file = gen_res.target_path / "scripts" / "main.py"
            script_file.write_text("API_KEY = 'sk-proj-abcdefghijklmnopqrstuv12345'\n", encoding="utf-8")
            from skillfactory.manifest import create_manifest, write_manifest
            manifest = create_manifest(gen_res.target_path, spec, spec.template_family)
            write_manifest(gen_res.target_path, manifest)

            with self.assertRaises(ValueError) as ctx:
                prepare_publish_repository(
                    skill_dir=gen_res.target_path,
                    output_dir=publish_dir,
                )
            self.assertIn("hardcoded credentials/secrets", str(ctx.exception))
            self.assertFalse(publish_dir.exists())

    def test_all_five_curated_examples_score_grade_a(self):
        """AC6.06: All 5 curated reference skills in examples/ score >= 90 (Grade A)."""
        examples_dir = Path("examples")
        self.assertTrue(examples_dir.is_dir(), "examples/ directory must exist")

        example_names = [
            "pdf-to-markdown",
            "docker-security-audit",
            "git-release-helper",
            "sql-migration-linter",
            "api-schema-validator",
        ]

        for name in example_names:
            skill_path = examples_dir / name
            self.assertTrue(skill_path.is_dir(), f"Example '{name}' must exist in examples/")

            rep = evaluate_skill(skill_path, run_tests=True, save_report=False)
            self.assertGreaterEqual(
                rep.total_score,
                90,
                f"Curated example '{name}' scored {rep.total_score}/100, but must score >= 90 (Grade A).",
            )
            self.assertEqual(rep.grade, "Grade A")


if __name__ == "__main__":
    unittest.main()
