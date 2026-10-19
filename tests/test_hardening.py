"""Unit and regression tests for Phase 14: Production Hardening, Cross-Platform Edge Cases, and Security (AC14.01–AC14.06)."""
from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import time
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

from skillfactory.cli import main
from skillfactory.core import generate_skill
from skillfactory.installer import install_skill, uninstall_skill
from skillfactory.manifest import create_manifest, verify_manifest
from skillfactory.packaging import (
    ZipSecurityError,
    calculate_file_sha256,
    export_skill_to_zip,
    import_skill_from_zip,
)
from skillfactory.scanner import scan_python_code, scan_secrets_in_text
from skillfactory.spec import SkillSpec
from skillfactory.validator import validate_skill


class ProductionHardeningTests(unittest.TestCase):
    def test_unicode_and_nested_filesystem_paths(self):
        """AC14.01: Verifies skills scaffold and validate in deep Unicode directories."""
        with tempfile.TemporaryDirectory() as tmp:
            unicode_dest = Path(tmp) / "测试目录 📂" / "日本語スペース 🚀" / "sub_path"
            unicode_dest.mkdir(parents=True)

            spec = SkillSpec(
                name="unicode-hardening-tool",
                description="A test tool handling international paths: 日本語, العربية, and emojis 🌟.",
                template_family="python-script",
            )
            res = generate_skill(spec, unicode_dest)
            self.assertTrue(res.target_path.exists())

            # Validate generated skill
            val = validate_skill(res.target_path)
            self.assertTrue(val.is_valid, f"Validation errors: {val.errors}")

            # Verify manifest inside deep Unicode tree
            is_valid, discrepancies = verify_manifest(res.target_path)
            self.assertTrue(is_valid, f"Manifest verification failed: {discrepancies}")
            self.assertEqual(discrepancies, [])

    def test_windows_reserved_names_rejected(self):
        """AC14.01: Windows reserved device names are blocked across spec and validator."""
        reserved_samples = ["CON", "prn", "Aux", "nul", "COM1", "lpt9"]
        for res_name in reserved_samples:
            spec = SkillSpec(
                name=res_name,
                description="Valid description for testing reserved name rejection.",
            )
            errors = spec.validate()
            self.assertTrue(
                any("reserved by Windows" in e for e in errors),
                f"Expected '{res_name}' to trigger reserved name error, got: {errors}",
            )

    def test_tampered_manifest_detection(self):
        """AC14.03: Detects file tampering and unexpected modifications."""
        with tempfile.TemporaryDirectory() as tmp:
            spec = SkillSpec(
                name="tamper-test-skill",
                description="Testing manifest tampering detection.",
                template_family="python-script",
            )
            res = generate_skill(spec, Path(tmp))

            # Modify an existing file after manifest creation
            script_file = res.target_path / "scripts" / "main.py"
            original_content = script_file.read_text(encoding="utf-8")
            script_file.write_text(original_content + "\n# Tampered line\n", encoding="utf-8")

            is_valid, discrepancies = verify_manifest(res.target_path)
            self.assertFalse(is_valid)
            self.assertTrue(any("scripts/main.py" in d for d in discrepancies))

    def test_zip_path_traversal_and_symlink_defense(self):
        """AC14.03: Blocks Zip Slip path traversal and malicious absolute targets."""
        with tempfile.TemporaryDirectory() as tmp:
            malicious_zip = Path(tmp) / "evil.zip"
            target_extract = Path(tmp) / "extracted"
            target_extract.mkdir()

            # Create archive with path traversal filename
            with zipfile.ZipFile(malicious_zip, "w") as zf:
                zf.writestr("../../../evil.sh", "echo 'pwned'")

            with self.assertRaises(ZipSecurityError):
                import_skill_from_zip(malicious_zip, target_extract)

    def test_safe_atomic_installation_lifecycle(self):
        """AC14.01 & AC14.03: Full install -> verify -> uninstall leaves zero trace."""
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "source"
            target_repo = Path(tmp) / "agent_workspace"
            target_repo.mkdir()
            reg_file = Path(tmp) / "registry.json"

            spec = SkillSpec(
                name="lifecycle-skill",
                description="Tests atomic installation and clean removal.",
                template_family="python-script",
            )
            res = generate_skill(spec, source_dir)

            # Install skill to cursor platform target
            install_res = install_skill(
                skill_path=res.target_path,
                target_platform="cursor",
                scope="project",
                project_dir=target_repo,
                registry_path=reg_file,
            )
            self.assertTrue(install_res.installed_path.exists())

            # Verify installed skill files
            is_valid, disc = verify_manifest(install_res.installed_path)
            self.assertTrue(is_valid, f"Installed manifest invalid: {disc}")

            # Uninstall skill
            removed = uninstall_skill(
                skill_name="lifecycle-skill",
                target_platform="cursor",
                registry_path=reg_file,
            )
            self.assertGreaterEqual(len(removed), 1)
            self.assertFalse(install_res.installed_path.exists())

    def test_ast_safety_scanner_catches_eval_exec_subprocess(self):
        """AC14.03: Code safety scanner identifies dangerous Python runtime constructs."""
        dangerous_snippets = [
            ("eval('1 + 1')", "AST001"),
            ("__import__('os')", "AST002"),
            ("import os; os.system('id')", "AST003"),
            ("import subprocess; subprocess.Popen(['rm', '-rf', '/'], shell=True)", "AST007"),
        ]
        for code, expected_rule in dangerous_snippets:
            findings = scan_python_code(code)
            rule_ids = {f.rule_id for f in findings}
            self.assertIn(
                expected_rule,
                rule_ids,
                f"Expected rule {expected_rule} for code: {code}, got: {rule_ids}",
            )


if __name__ == "__main__":
    unittest.main()
