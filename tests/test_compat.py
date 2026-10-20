"""Unit tests for Phase 3 Multi-Agent Compatibility (T3.01–T3.06, AC3.01–AC3.06)."""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from skillfactory.cli import main
from skillfactory.compat.detect import detect_all_platforms, detect_platform
from skillfactory.compat.platform_db import (
    get_all_platforms,
    get_platform,
    get_project_skill_paths,
    get_reserved_names,
    get_user_skill_path,
    load_platforms_db,
)
from skillfactory.compat.resolve import detect_skill_collisions, resolve_install_targets
from skillfactory.core import generate_skill
from skillfactory.spec import SkillSpec
from skillfactory.validator import validate_skill
from skillfactory.yaml_util import parse_frontmatter


class PlatformDatabaseTests(unittest.TestCase):
    """AC3.01: Platform database platforms.json encodes paths and features for all 4 tools."""

    def setUp(self):
        self.db = load_platforms_db()

    def test_database_schema_and_metadata(self):
        self.assertIn("schema_version", self.db)
        self.assertIn("last_updated", self.db)
        self.assertIn("platforms", self.db)

        platforms = self.db["platforms"]
        expected_platforms = {
            "claude-code",
            "cursor",
            "codex",
            "antigravity",
            "windsurf",
            "continue",
            "cline",
            "copilot",
        }
        self.assertEqual(set(platforms.keys()), expected_platforms)

    def test_required_platform_fields(self):
        required_keys = [
            "id",
            "display_name",
            "vendor",
            "last_verified",
            "source_url",
            "status",
            "invocation_syntax",
            "project_skill_paths",
            "user_skill_paths",
            "detection_rules",
            "supported_frontmatter_fields",
        ]
        for pid, pdef in self.db["platforms"].items():
            for key in required_keys:
                self.assertIn(key, pdef, f"Platform '{pid}' missing required key '{key}'")
            self.assertEqual(pdef["status"], "verified")
            self.assertTrue(len(pdef["last_verified"]) >= 10, f"Platform '{pid}' must have ISO date")
            self.assertTrue(pdef["source_url"].startswith("http") or "skill" in pdef["source_url"])

    def test_reserved_names(self):
        claude_reserved = get_reserved_names("claude-code")
        self.assertIn("synced", claude_reserved)

        all_reserved = get_reserved_names()
        self.assertIn("synced", all_reserved)

    def test_os_path_resolution(self):
        user_path_mac = get_user_skill_path("claude-code", os_name="macos", home_override="/tmp/mockhome")
        self.assertIsNotNone(user_path_mac)
        self.assertEqual(user_path_mac, str(Path("/tmp/mockhome/.claude/skills").resolve()))

        user_path_win = get_user_skill_path("claude-code", os_name="windows", home_override="/tmp/mockhome")
        self.assertIsNotNone(user_path_win)
        assert user_path_win is not None
        self.assertTrue(user_path_win.endswith(".claude/skills") or user_path_win.endswith(".claude\\skills"))


class PlatformDetectionTests(unittest.TestCase):
    """AC3.02: Platform detection identifies installed agents on host system."""

    def test_mock_filesystem_detection(self):
        with tempfile.TemporaryDirectory() as tmp_proj, tempfile.TemporaryDirectory() as tmp_home:
            p_dir = Path(tmp_proj)
            h_dir = Path(tmp_home)

            # Initially nothing detected
            results = detect_all_platforms(project_dir=p_dir, home_dir=h_dir)
            # Since system binary might exist, we check specific mock directories
            claude_def = get_platform("claude-code")
            self.assertIsNotNone(claude_def)
            assert claude_def is not None
            # Overwrite binary check to avoid host contamination in unit test
            isolated_claude = dict(claude_def)
            isolated_claude["detection_rules"] = {"project_dirs": [".claude"], "user_dirs": ["~/.claude"], "binaries": []}
            
            res_before = detect_platform("claude-code", isolated_claude, project_dir=p_dir, home_dir=h_dir)
            self.assertFalse(res_before.detected)

            # Create mock user directory for Claude
            (h_dir / ".claude").mkdir()
            res_after = detect_platform("claude-code", isolated_claude, project_dir=p_dir, home_dir=h_dir)
            self.assertTrue(res_after.detected)
            self.assertTrue(any(".claude" in r for r in res_after.reasons))

            # Create mock project directory for Antigravity (.agents)
            agy_def = get_platform("antigravity")
            self.assertIsNotNone(agy_def)
            assert agy_def is not None
            isolated_agy = dict(agy_def)
            isolated_agy["detection_rules"] = {"project_dirs": [".agents"], "user_dirs": [], "binaries": []}
            (p_dir / ".agents").mkdir()
            res_agy = detect_platform("antigravity", isolated_agy, project_dir=p_dir, home_dir=h_dir)
            self.assertTrue(res_agy.detected)

    def test_path_readiness_statuses(self):
        with tempfile.TemporaryDirectory() as tmp_proj, tempfile.TemporaryDirectory() as tmp_home:
            p_dir = Path(tmp_proj)
            h_dir = Path(tmp_home)

            results = detect_all_platforms(project_dir=p_dir, home_dir=h_dir)
            for res in results.values():
                for p_status in res.project_path_statuses.values():
                    self.assertIn(p_status, ["ready_to_create", "exists_writable", "exists_readonly"])
                self.assertIn(res.user_path_status, ["ready_to_create", "exists_writable", "exists_readonly"])


class DoctorCommandTests(unittest.TestCase):
    """AC3.03: skillfactory doctor prints clear diagnostic summary and path readiness."""

    def test_doctor_terminal_output(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["doctor"])
        self.assertEqual(ret, 0)
        output = buf.getvalue()
        self.assertIn("Skill Factory Doctor", output)
        self.assertIn("System Runtime", output)
        self.assertIn("Detected AI Platforms", output)
        self.assertIn("Shared-Directory Notes", output)
        self.assertIn("Claude Code", output)
        self.assertIn("Cursor", output)
        self.assertIn("OpenAI Codex", output)
        self.assertIn("Google Antigravity", output)

    def test_doctor_json_output(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["doctor", "--json"])
        self.assertEqual(ret, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["status"], "success")
        self.assertIn("system", data)
        self.assertIn("platforms", data)
        self.assertIn("shared_directories", data)
        self.assertTrue(data["system"]["python_compatible"])
        self.assertIn("claude-code", data["platforms"])


class SharedFolderResolverTests(unittest.TestCase):
    """AC3.04: Shared directory resolver avoids double-installing to .agents/skills/."""

    def test_resolve_shared_targets_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp_proj:
            # When targeting cursor, codex, and antigravity together
            platforms = ["cursor", "codex", "antigravity"]
            resolved = resolve_install_targets(platforms, scope="project", project_dir=tmp_proj)
            
            # Must resolve to 1 single folder: .agents/skills
            self.assertEqual(len(resolved), 1)
            self.assertTrue(resolved[0].target_dir.endswith(".agents/skills") or resolved[0].target_dir.endswith(".agents\\skills"))
            self.assertEqual(set(resolved[0].platforms), {"cursor", "codex", "antigravity"})

    def test_resolve_claude_and_agents_targets(self):
        with tempfile.TemporaryDirectory() as tmp_proj:
            platforms = ["claude-code", "cursor", "codex", "antigravity"]
            resolved = resolve_install_targets(platforms, scope="project", project_dir=tmp_proj)
            
            # Exactly two directories: .claude/skills and .agents/skills
            self.assertEqual(len(resolved), 2)
            dirs = {r.target_dir for r in resolved}
            self.assertTrue(any(d.endswith(".claude/skills") or d.endswith(".claude\\skills") for d in dirs))
            self.assertTrue(any(d.endswith(".agents/skills") or d.endswith(".agents\\skills") for d in dirs))

    def test_collision_detection(self):
        with tempfile.TemporaryDirectory() as tmp_proj, tempfile.TemporaryDirectory() as tmp_home:
            p_dir = Path(tmp_proj)
            h_dir = Path(tmp_home)

            # Scenario 1: Clean - no duplicate
            (p_dir / ".agents" / "skills" / "clean-skill").mkdir(parents=True)
            warnings = detect_skill_collisions("clean-skill", project_dir=p_dir, home_dir=h_dir)
            self.assertEqual(len(warnings), 0)

            # Scenario 2: Collision - same skill in both .claude/skills and .agents/skills
            (p_dir / ".claude" / "skills" / "colliding-skill").mkdir(parents=True)
            (p_dir / ".agents" / "skills" / "colliding-skill").mkdir(parents=True)
            warnings_coll = detect_skill_collisions("colliding-skill", project_dir=p_dir, home_dir=h_dir)
            self.assertEqual(len(warnings_coll), 1)
            self.assertIn("cursor", warnings_coll[0].impacted_platforms)
            self.assertIn("Duplicate skill 'colliding-skill'", warnings_coll[0].message)


class CompatibilitySectionGenerationTests(unittest.TestCase):
    """AC3.05: Compatibility table auto-generated in README.md and frontmatter."""

    def test_compatibility_artifacts_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = SkillSpec(
                name="compat-demo",
                description="Demonstrating multi-platform compatibility generation.",
                template_family="python-script",
            )
            res = generate_skill(spec, Path(tmp))
            
            # 1. Frontmatter compatibility
            skill_md = (res.target_path / "SKILL.md").read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(skill_md)
            self.assertIn("compatibility", fm)
            self.assertIn("Claude Code", fm["compatibility"])
            self.assertIn("Cursor", fm["compatibility"])
            self.assertIn("Google Antigravity", fm["compatibility"])

            # 2. README.md Compatibility table
            readme_md = (res.target_path / "README.md").read_text(encoding="utf-8")
            self.assertIn("## Compatibility", readme_md)
            self.assertIn("| Claude Code |", readme_md)
            self.assertIn("| Cursor |", readme_md)
            self.assertIn("| OpenAI Codex |", readme_md)
            self.assertIn("| Google Antigravity |", readme_md)


class PlatformDiscoverySimulationTests(unittest.TestCase):
    """AC3.06: Generated skills load cleanly without errors in simulated platform folders."""

    def test_simulated_platform_discovery_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = SkillSpec(
                name="cross-platform-skill",
                description="Testing discovery across simulated platform folders.",
                template_family="instructions-only",
            )
            res = generate_skill(spec, root / "staging")

            simulated_paths = [
                root / ".claude" / "skills" / "cross-platform-skill",
                root / ".agents" / "skills" / "cross-platform-skill",
                root / ".cursor" / "skills" / "cross-platform-skill",
                root / ".gemini" / "config" / "skills" / "cross-platform-skill",
            ]

            for sim_path in simulated_paths:
                sim_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(res.target_path, sim_path)

                # Validate directly in the simulated folder
                val_result = validate_skill(sim_path, expected_name="cross-platform-skill", verify_hashes=True)
                self.assertTrue(
                    val_result.is_valid,
                    f"Skill failed validation in {sim_path}: {val_result.errors}",
                )


class PlatformAliasNormalizationTests(unittest.TestCase):
    """DEF-04: Test platform alias normalization across all platform commands."""

    def test_normalize_platform_id_aliases(self):
        from skillfactory.compat.platform_db import normalize_platform_id

        self.assertEqual(normalize_platform_id("claude"), "claude-code")
        self.assertEqual(normalize_platform_id("  Claude  "), "claude-code")
        self.assertEqual(normalize_platform_id("anthropic"), "claude-code")
        self.assertEqual(normalize_platform_id("cursor"), "cursor")
        self.assertEqual(normalize_platform_id("openai"), "codex")
        self.assertEqual(normalize_platform_id("codex"), "codex")
        self.assertEqual(normalize_platform_id("google"), "antigravity")
        self.assertEqual(normalize_platform_id("agy"), "antigravity")
        self.assertEqual(normalize_platform_id("antigravity"), "antigravity")
        self.assertEqual(normalize_platform_id("codeium"), "windsurf")
        self.assertEqual(normalize_platform_id("windsurf"), "windsurf")
        self.assertEqual(normalize_platform_id("continuedev"), "continue")
        self.assertEqual(normalize_platform_id("continue"), "continue")
        self.assertEqual(normalize_platform_id("cline"), "cline")
        self.assertEqual(normalize_platform_id("github-copilot"), "copilot")
        self.assertEqual(normalize_platform_id("copilot"), "copilot")

    def test_get_platform_with_aliases(self):
        claude_def = get_platform("claude")
        self.assertIsNotNone(claude_def)
        self.assertEqual(claude_def["id"], "claude-code")

        openai_def = get_platform("openai")
        self.assertIsNotNone(openai_def)
        self.assertEqual(openai_def["id"], "codex")

        google_def = get_platform("google")
        self.assertIsNotNone(google_def)
        self.assertEqual(google_def["id"], "antigravity")

    def test_resolve_install_targets_with_aliases(self):
        targets = resolve_install_targets(["claude", "google", "openai"])
        platform_ids = []
        for t in targets:
            platform_ids.extend(t.platforms)
        self.assertIn("claude-code", platform_ids)
        self.assertIn("antigravity", platform_ids)
        self.assertIn("codex", platform_ids)


if __name__ == "__main__":
    unittest.main()
