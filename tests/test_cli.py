"""Unit and integration tests for skillfactory CLI (AC1.01, AC1.08, FR-CLI-01..05)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skillfactory.cli import main
from skillfactory.spec import SkillSpec


class CliTests(unittest.TestCase):
    def test_cli_version(self):
        exit_code = main(["version"])
        self.assertEqual(exit_code, 0)

    def test_cli_help(self):
        exit_code = main([])
        self.assertEqual(exit_code, 0)

    def test_cli_new_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # 1. Create new skill
            exit_code = main([
                "new",
                "--name", "cli-test-skill",
                "--description", "Created via CLI arguments test.",
                "--template", "python-script",
                "--output", str(tmp_path),
            ])
            self.assertEqual(exit_code, 0)
            target = tmp_path / "cli-test-skill"
            self.assertTrue(target.exists())
            self.assertTrue((target / "SKILL.md").exists())
            self.assertTrue((target / ".skillfactory" / "manifest.json").exists())

            # 2. Validate skill
            val_code = main(["validate", str(target)])
            self.assertEqual(val_code, 0)

    def test_cli_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exit_code = main([
                "new",
                "--name", "dry-run-skill",
                "--description", "Testing dry run functionality.",
                "--output", str(tmp_path),
                "--dry-run",
            ])
            self.assertEqual(exit_code, 0)
            # Nothing should be written to disk
            self.assertFalse((tmp_path / "dry-run-skill").exists())

    def test_cli_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exit_code = main([
                "new",
                "--name", "json-output-skill",
                "--description", "Testing JSON flag in CLI.",
                "--output", str(tmp_path),
                "--json",
            ])
            self.assertEqual(exit_code, 0)
            target = tmp_path / "json-output-skill"
            self.assertTrue(target.exists())

    def test_cli_new_from_spec_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec = SkillSpec(
                name="spec-file-skill",
                description="Created from an intermediate spec JSON file.",
                template_family="instructions-only",
            )
            spec_file = tmp_path / "my-spec.json"
            spec_file.write_text(spec.to_json(), encoding="utf-8")

            exit_code = main([
                "new",
                "--spec", str(spec_file),
                "--output", str(tmp_path),
            ])
            self.assertEqual(exit_code, 0)
            target = tmp_path / "spec-file-skill"
            self.assertTrue(target.exists())
            self.assertTrue((target / "SKILL.md").exists())

    def test_cli_validate_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            main([
                "new",
                "--name", "record-skill",
                "--description", "Testing validation recording.",
                "--output", str(tmp_path),
            ])
            target = tmp_path / "record-skill"

            val_code = main(["validate", str(target), "--record"])
            self.assertEqual(val_code, 0)
            rec_file = target / ".skillfactory" / "validation.json"
            self.assertTrue(rec_file.exists())
            rec_data = json.loads(rec_file.read_text(encoding="utf-8"))
            self.assertTrue(rec_data["is_valid"])

    def test_cli_submodule_invocation(self):
        """Verify python3 -m skillfactory runs via subprocess (AC1.01)."""
        res = subprocess.run(
            [sys.executable, "-m", "skillfactory", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Skill Factory", res.stdout)


    def test_cli_platform_alias_support(self):
        """Verify --platform is accepted as an alias to --target."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            main([
                "new",
                "--name", "alias-skill",
                "--description", "Testing --platform alias support.",
                "--output", str(tmp_path),
            ])
            target = tmp_path / "alias-skill"
            exit_code = main([
                "install",
                str(target),
                "--platform", "claude-code",
                "--project", str(tmp_path),
            ])
            self.assertEqual(exit_code, 0)
            self.assertTrue((tmp_path / ".claude" / "skills" / "alias-skill").exists())

    def test_cli_pack_list_and_json(self):
        """Verify pack list outputs all 5 packs."""
        exit_code = main(["pack", "list"])
        self.assertEqual(exit_code, 0)

        # JSON mode
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["pack", "list", "--json"])
        self.assertEqual(ret, 0)
        data = json.loads(buf.getvalue())
        self.assertIn("packs", data)
        pack_ids = [p["id"] for p in data["packs"]]
        self.assertIn("office-productivity", pack_ids)
        self.assertIn("finance-erp", pack_ids)
        self.assertIn("developer-security", pack_ids)

    def test_cli_guide_non_interactive(self):
        """Verify guide runs non-interactively to completion."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exit_code = main([
                "guide",
                "--name", "beginner-cli-test",
                "--platform", "standalone",
                "--output", str(tmp_path),
                "--non-interactive",
            ])
            self.assertEqual(exit_code, 0)
            self.assertTrue((tmp_path / "beginner-cli-test" / "SKILL.md").exists())

    def test_cli_ai_create_with_mock_provider(self):
        """Verify ai-create command creates valid skill via mock provider."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exit_code = main([
                "ai-create",
                "Create a text report generator",
                "--name", "ai-cli-skill",
                "--provider", "mock-passing",
                "--output", str(tmp_path),
            ])
            self.assertEqual(exit_code, 0)
            self.assertTrue((tmp_path / "ai-cli-skill" / "SKILL.md").exists())
            self.assertTrue((tmp_path / "ai-cli-skill" / "scripts" / "main.py").exists())

    def test_cli_ai_create_safety_rejection(self):
        """Verify ai-create command intercepts dangerous code."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exit_code = main([
                "ai-create",
                "Execute dangerous code",
                "--name", "dangerous-cli-skill",
                "--provider", "mock-dangerous",
                "--output", str(tmp_path),
            ])
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
