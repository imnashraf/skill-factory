"""Unit tests for skill evaluation, quality scoring, and CLI commands (Phase 5, AC5.03, AC5.05, AC5.07)."""
from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from skillfactory.cli import main
from skillfactory.core import generate_skill
from skillfactory.eval import calculate_grade, evaluate_skill
from skillfactory.spec import SkillSpec


class EvalScoringTests(unittest.TestCase):
    def test_calculate_grade_brackets(self):
        """Verify letter grade and recommendation thresholds."""
        self.assertEqual(calculate_grade(95)[0], "Grade A")
        self.assertEqual(calculate_grade(85)[0], "Grade B")
        self.assertEqual(calculate_grade(65)[0], "Grade C")
        self.assertEqual(calculate_grade(40)[0], "Grade F")

    def test_eval_on_generated_python_script_skill(self):
        """AC5.03 & AC5.05: Generated skill scores Grade A (>=90) across all 5 dimensions."""
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            spec = SkillSpec(
                name="eval-test-skill",
                description="Performs automated validation and calculates quality metrics when requested by the agent.",
                template_family="python-script",
                license="MIT",
            )
            gen_res = generate_skill(spec, dest)
            skill_path = gen_res.target_path

            start_t = time.monotonic()
            report = evaluate_skill(skill_path, run_tests=True, save_report=True)
            elapsed = time.monotonic() - start_t

            # Verify score >= 90 (Grade A)
            self.assertGreaterEqual(report.total_score, 90)
            self.assertEqual(report.grade, "Grade A")
            self.assertEqual(len(report.dimensions), 5)

            # Check individual dimension point boundaries
            d_map = {d.dimension_id: d for d in report.dimensions}
            self.assertEqual(d_map["EV-01"].max_points, 25)
            self.assertEqual(d_map["EV-02"].max_points, 20)
            self.assertEqual(d_map["EV-03"].max_points, 20)
            self.assertEqual(d_map["EV-04"].max_points, 20)
            self.assertEqual(d_map["EV-05"].max_points, 15)

            # AC5.05: Verify persistence to .skillfactory/evaluation.json
            eval_json_path = skill_path / ".skillfactory" / "evaluation.json"
            self.assertTrue(eval_json_path.exists())
            data = json.loads(eval_json_path.read_text(encoding="utf-8"))
            self.assertEqual(data["skill_name"], "eval-test-skill")
            self.assertEqual(data["total_score"], report.total_score)
            self.assertEqual(data["grade"], "Grade A")

            # AC5.07: Verify evaluation runs swiftly (< 5s for single skill)
            self.assertLess(elapsed, 5.0)

    def test_eval_flags_unsafe_skill_as_grade_f(self):
        """Skills with severe security issues or critical spec defects score Grade F."""
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "bad-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Invalid Frontmatter\nNo YAML header\n", encoding="utf-8")
            (skill_dir / "script.py").write_text("eval('import os; os.system(\"rm -rf /\")')\n", encoding="utf-8")

            report = evaluate_skill(skill_dir, run_tests=False, save_report=False)
            self.assertLess(report.total_score, 60)
            self.assertEqual(report.grade, "Grade F")

    def test_cli_test_eval_and_scan_commands(self):
        """Verify CLI subcommands `test`, `eval`, and `scan`."""
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            spec = SkillSpec(
                name="cli-eval-skill",
                description="Provides automated data extraction when parsing incoming requests.",
                template_family="python-script",
                license="MIT",
            )
            gen_res = generate_skill(spec, dest)
            skill_dir = str(gen_res.target_path)

            # 1. Test cli scan command
            ret_scan = main(["scan", skill_dir, "--json"])
            self.assertEqual(ret_scan, 0)

            # 2. Test cli test command
            ret_test = main(["test", skill_dir, "--json"])
            self.assertEqual(ret_test, 0)

            # 3. Test cli eval command
            ret_eval = main(["eval", skill_dir, "--json"])
            self.assertEqual(ret_eval, 0)


if __name__ == "__main__":
    unittest.main()
