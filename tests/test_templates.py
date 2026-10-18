"""Unit and integration tests for all 5 template families (T2.05, T2.06, AC2.05, AC2.06)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skillfactory.core import generate_skill
from skillfactory.spec import VALID_TEMPLATE_FAMILIES, SkillSpec
from skillfactory.validator import validate_skill


class TemplateFamilyTests(unittest.TestCase):
    def test_all_five_template_families_generate_and_validate(self):
        """AC2.05: All 5 template families render valid Agent Skills packages."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            for family in sorted(VALID_TEMPLATE_FAMILIES):
                spec = SkillSpec(
                    name=f"test-{family}",
                    description=f"Automated test skill for {family} family.",
                    template_family=family,
                    author="Test Author",
                    license="MIT",
                )
                res = generate_skill(spec, tmp_path)
                self.assertTrue(res.target_path.exists())

                # Validate skill package
                val_res = validate_skill(res.target_path)
                self.assertTrue(
                    val_res.is_valid,
                    f"Template family '{family}' produced invalid skill: {val_res.errors}",
                )

                # Check core files exist
                self.assertTrue((res.target_path / "SKILL.md").exists())
                self.assertTrue((res.target_path / "README.md").exists())
                self.assertTrue((res.target_path / "references" / "guide.md").exists())
                self.assertTrue((res.target_path / "examples" / "example.md").exists())
                self.assertTrue((res.target_path / ".skillfactory" / "manifest.json").exists())
                self.assertTrue((res.target_path / ".skillfactory" / "skill-spec.json").exists())

    def test_script_templates_have_honest_stubs_and_passing_structural_tests(self):
        """AC2.06: Generated script-based skills include working structural tests and skipped stubs."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            script_families = ["python-script", "file-transform"]
            for family in script_families:
                spec = SkillSpec(
                    name=f"stub-test-{family}",
                    description=f"Testing honest stubs for {family}.",
                    template_family=family,
                )
                res = generate_skill(spec, tmp_path)
                skill_dir = res.target_path

                # Run unit tests inside the generated skill
                proc = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                    cwd=str(skill_dir),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                # Must exit 0 (passed)
                self.assertEqual(
                    proc.returncode,
                    0,
                    f"Tests in '{family}' failed:\n{proc.stdout}\n{proc.stderr}",
                )
                # Output must show test_skill_structure passed and stub skipped
                self.assertIn("test_skill_structure", proc.stderr + proc.stdout)
                self.assertIn("skipped", (proc.stderr + proc.stdout).lower())
                self.assertNotIn("FAILED", proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
