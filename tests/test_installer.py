"""Comprehensive test suite for Phase 4 Easy Installation and Updates (T4.01–T4.09, AC4.01–AC4.09)."""

from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from skillfactory.cli import main
from skillfactory.core import generate_skill
from skillfactory.installer import (
    install_self,
    install_skill,
    rollback_skill,
    uninstall_skill,
    update_skill,
)
from skillfactory.manifest import compute_sha256
from skillfactory.registry import (
    find_installation,
    load_registry,
    register_installation,
    save_registry,
)
from skillfactory.spec import SkillSpec


class InstallerLifecycleTests(unittest.TestCase):
    """Test full install, update, rollback, and uninstall lifecycle."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        self.src_dir = self.root / "source"
        self.proj_dir = self.root / "project"
        self.home_dir = self.root / "home"
        self.reg_path = self.home_dir / "registry.json"

        self.src_dir.mkdir(parents=True)
        self.proj_dir.mkdir(parents=True)
        self.home_dir.mkdir(parents=True)

        # Generate a test skill in source directory
        self.spec = SkillSpec(
            name="lifecycle-skill",
            description="Testing the complete installation lifecycle.",
            template_family="python-script",
            version="1.0.0",
        )
        self.gen_res = generate_skill(self.spec, self.src_dir)
        self.skill_source = self.gen_res.target_path

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_install_and_registry_tracking(self):
        """AC4.01 & AC4.02: Install copies allow-listed files and tracks in registry."""
        # Add extraneous files in source that should NOT be copied (e.g. .venv, *.pyc)
        (self.skill_source / ".venv").mkdir()
        (self.skill_source / ".venv" / "junk.txt").write_text("ignore me")
        (self.skill_source / "junk.pyc").write_text("binary pyc")

        res = install_skill(
            skill_path=self.skill_source,
            target_platform="cursor",
            scope="project",
            project_dir=self.proj_dir,
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )

        # Target should be project/.agents/skills/lifecycle-skill
        expected_dest = (self.proj_dir / ".agents" / "skills" / "lifecycle-skill").resolve()
        self.assertEqual(res.installed_path.resolve(), expected_dest)
        self.assertTrue(expected_dest.is_dir())
        self.assertTrue((expected_dest / "SKILL.md").is_file())
        self.assertTrue((expected_dest / "README.md").is_file())
        self.assertTrue((expected_dest / "scripts" / "main.py").is_file())

        # Allow-list check: junk should not be copied
        self.assertFalse((expected_dest / ".venv").exists())
        self.assertFalse((expected_dest / "junk.pyc").exists())

        # Check registry.json record (AC4.01)
        reg_record = find_installation("lifecycle-skill", registry_path=self.reg_path)
        self.assertIsNotNone(reg_record)
        self.assertEqual(reg_record["skill_name"], "lifecycle-skill")
        self.assertEqual(reg_record["platform"], "cursor")
        self.assertEqual(reg_record["scope"], "project")
        self.assertEqual(reg_record["version"], "1.0.0")
        self.assertEqual(reg_record["mode"], "copy")
        self.assertIn("SKILL.md", reg_record["installed_files"])

    def test_refuse_unmanaged_folder_overwrite(self):
        """AC4.02: Refuses to overwrite an existing unmanaged folder."""
        # Pre-create the target directory without registering it
        unmanaged = self.proj_dir / ".agents" / "skills" / "lifecycle-skill"
        unmanaged.mkdir(parents=True)
        (unmanaged / "important_user_work.txt").write_text("Do not delete!")

        with self.assertRaises(FileExistsError) as ctx:
            install_skill(
                skill_path=self.skill_source,
                target_platform="cursor",
                scope="project",
                project_dir=self.proj_dir,
                home_dir=self.home_dir,
                registry_path=self.reg_path,
            )
        self.assertIn("not managed by Skill Factory", str(ctx.exception))
        # Ensure user work was preserved
        self.assertTrue((unmanaged / "important_user_work.txt").is_file())

    def test_update_with_edit_detection_and_backup(self):
        """AC4.03: Update detects local edits, requires force, and takes backup snapshot."""
        # 1. Install
        install_res = install_skill(
            skill_path=self.skill_source,
            target_platform="cursor",
            scope="project",
            project_dir=self.proj_dir,
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )

        # 2. Tamper with installed file
        script_path = install_res.installed_path / "scripts" / "main.py"
        script_path.write_text("# Locally modified code!\n", encoding="utf-8")

        # 3. Update without force must fail
        with self.assertRaises(ValueError) as ctx:
            update_skill(
                skill_name="lifecycle-skill",
                target_platform="cursor",
                force=False,
                home_dir=self.home_dir,
                registry_path=self.reg_path,
            )
        self.assertIn("has local modifications", str(ctx.exception))

        # 4. Update with force succeeds and creates backup snapshot
        update_res = update_skill(
            skill_name="lifecycle-skill",
            target_platform="cursor",
            force=True,
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )
        self.assertIsNotNone(update_res.backup_path)
        backup_dir = Path(update_res.backup_path)
        self.assertTrue(backup_dir.is_dir())
        # Backup should contain the modified script
        backup_script = backup_dir / "scripts" / "main.py"
        self.assertIn("Locally modified code!", backup_script.read_text(encoding="utf-8"))

        # Installed path has been updated with fresh code
        self.assertNotIn("Locally modified code!", script_path.read_text(encoding="utf-8"))

    def test_rollback(self):
        """AC4.04: Rollback restores previous version byte-for-byte."""
        # Install and then update to create a backup
        install_skill(
            skill_path=self.skill_source,
            target_platform="cursor",
            scope="project",
            project_dir=self.proj_dir,
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )

        installed_script = self.proj_dir / ".agents" / "skills" / "lifecycle-skill" / "scripts" / "main.py"
        installed_script.write_text("# Version 1 customized\n", encoding="utf-8")
        orig_sha = compute_sha256(installed_script)

        # Force update to create backup
        update_skill(
            skill_name="lifecycle-skill",
            target_platform="cursor",
            force=True,
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )
        # Verify script was overwritten by update
        self.assertNotEqual(compute_sha256(installed_script), orig_sha)

        # Rollback
        rollback_res = rollback_skill(
            skill_name="lifecycle-skill",
            target_platform="cursor",
            registry_path=self.reg_path,
        )
        self.assertEqual(compute_sha256(installed_script), orig_sha)

    def test_safe_uninstall_preserves_user_files(self):
        """AC4.05: Safe uninstall deletes only tracked files, preserving user files."""
        install_res = install_skill(
            skill_path=self.skill_source,
            target_platform="cursor",
            scope="project",
            project_dir=self.proj_dir,
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )

        dest = install_res.installed_path
        # User creates extra file in skill directory
        user_file = dest / "my_custom_data.csv"
        user_file.write_text("col1,col2\n1,2\n", encoding="utf-8")

        removed = uninstall_skill(
            skill_name="lifecycle-skill",
            target_platform="cursor",
            registry_path=self.reg_path,
        )

        # Tracked files should be removed
        self.assertFalse((dest / "SKILL.md").exists())
        self.assertFalse((dest / "README.md").exists())
        # User file must be preserved
        self.assertTrue(user_file.is_file())
        self.assertTrue(dest.is_dir())

        # Registry entry should be removed
        self.assertIsNone(find_installation("lifecycle-skill", registry_path=self.reg_path))

    def test_symlink_mode(self):
        """AC4.06: Symlink mode creates valid symlink or falls back cleanly."""
        res = install_skill(
            skill_path=self.skill_source,
            target_platform="claude-code",
            scope="project",
            link=True,
            project_dir=self.proj_dir,
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )
        self.assertTrue(res.installed_path.exists())
        # On Unix/macOS, symlink should succeed
        if hasattr(os, "symlink"):
            self.assertTrue(res.installed_path.is_symlink() or res.mode == "copy")

    def test_install_self(self):
        """AC4.08: Self-install command installs Skill Factory into platform folder."""
        results = install_self(
            target_platform="cursor",
            scope="user",
            home_dir=self.home_dir,
            registry_path=self.reg_path,
        )
        self.assertTrue(len(results) >= 1)
        res = results[0]
        self.assertTrue(res.installed_path.is_dir())
        self.assertTrue((res.installed_path / "SKILL.md").is_file())


class CliInstallCommandTests(unittest.TestCase):
    """Test CLI commands: install, update, rollback, uninstall, list."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env_patch = {"SKILLFACTORY_HOME": str(self.root / "home")}
        import os
        self.old_env = os.environ.get("SKILLFACTORY_HOME")
        os.environ["SKILLFACTORY_HOME"] = str(self.root / "home")

        spec = SkillSpec(name="cli-installed-skill", description="CLI install test.", template_family="instructions-only")
        res = generate_skill(spec, self.root / "skills")
        self.skill_path = str(res.target_path)

    def tearDown(self):
        import os
        if self.old_env:
            os.environ["SKILLFACTORY_HOME"] = self.old_env
        else:
            os.environ.pop("SKILLFACTORY_HOME", None)
        self.tmp.cleanup()

    def test_cli_install_and_list(self):
        """AC4.07: Verify CLI install and list output."""
        project_dir = str(self.root / "sandbox_project")
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret_install = main(["install", self.skill_path, "--target", "cursor", "--scope", "project", "--project", project_dir])
        self.assertEqual(ret_install, 0)
        self.assertIn("Installed 'cli-installed-skill'", buf.getvalue())

        # List command (AC4.07)
        buf_list = io.StringIO()
        with redirect_stdout(buf_list):
            ret_list = main(["list"])
        self.assertEqual(ret_list, 0)
        list_out = buf_list.getvalue()
        self.assertIn("cli-installed-skill", list_out)
        self.assertIn("cursor", list_out)
        self.assertIn("Total installations: 1", list_out)

        # List in JSON mode
        buf_json = io.StringIO()
        with redirect_stdout(buf_json):
            ret_json = main(["list", "--json"])
        self.assertEqual(ret_json, 0)
        data = json.loads(buf_json.getvalue())
        self.assertEqual(len(data["installations"]), 1)
        self.assertEqual(data["installations"][0]["skill_name"], "cli-installed-skill")


if __name__ == "__main__":
    unittest.main()
