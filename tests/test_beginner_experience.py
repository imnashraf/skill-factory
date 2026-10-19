"""Unit and simulated journey tests for Beginner Onboarding Experience (Phase 16, Workstreams 16A & 16E)."""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from skillfactory.guide import get_os_friendly_name, get_os_path_guidance, run_beginner_guide


class TestBeginnerExperience(unittest.TestCase):
    """Validates the beginner first-run journey and cross-platform path guidance."""

    def test_os_path_guidance(self):
        os_name = get_os_friendly_name()
        self.assertIn(os_name, ("macOS", "Linux", "Windows"))

        # Verify path hints for various platforms
        antigravity_path = get_os_path_guidance("antigravity")
        self.assertTrue(".agents" in antigravity_path)

        claude_path = get_os_path_guidance("claude-code")
        self.assertTrue("claude" in claude_path.lower())

        cursor_path = get_os_path_guidance("cursor")
        self.assertTrue(".cursor" in cursor_path)

    def test_simulated_beginner_journey_non_interactive(self):
        """Simulate an automated first-time user journey from start to finish."""
        output_buffer = io.StringIO()

        def fake_print(*args: object, **kwargs: object) -> None:
            output_buffer.write(" ".join(str(a) for a in args) + "\n")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exit_code = run_beginner_guide(
                non_interactive=True,
                skill_name="beginner-test-skill",
                platform="standalone",
                output_dir=tmp_path,
                print_func=fake_print,
            )

            self.assertEqual(exit_code, 0, "Guided onboarding must exit cleanly with code 0")

            rendered = output_buffer.getvalue()
            # 1. Must show system health check
            self.assertIn("Checking System Prerequisites", rendered)
            # 2. Must show target selection
            self.assertIn("Target platform: standalone", rendered)
            # 3. Must show scaffolding generation
            self.assertIn("Skill created at:", rendered)
            # 4. Must show validation and test execution
            self.assertIn("Specification and directory integrity verified!", rendered)
            # 5. Must show complete lifecycle guidance
            self.assertIn("Full Lifecycle Commands:", rendered)
            self.assertIn("skillfactory test", rendered)
            self.assertIn("skillfactory eval", rendered)
            self.assertIn("skillfactory scan", rendered)
            self.assertIn("skillfactory uninstall", rendered)

            # Check created skill files
            created_skill = tmp_path / "beginner-test-skill"
            self.assertTrue((created_skill / "SKILL.md").is_file())
            self.assertTrue((created_skill / "scripts" / "main.py").is_file())
            self.assertTrue((created_skill / "tests" / "test_placeholder.py").is_file() or (created_skill / "tests" / "test_main.py").is_file())
            self.assertTrue((created_skill / ".skillfactory" / "manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
