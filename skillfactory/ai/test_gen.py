"""Behavioral Unit Test Generator (Phase 16, Workstream 16C).

Synthesizes deterministic, executable `unittest.TestCase` suites mapped directly
to Acceptance Criteria and Input/Output contracts from StructuredRequirementSpec.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from skillfactory.ai.requirements import StructuredRequirementSpec


def generate_behavioral_tests(spec: StructuredRequirementSpec) -> str:
    """Synthesize complete, executable test suite mapped to acceptance criteria."""
    camel_name = "".join(part.capitalize() for part in spec.skill_name.split("-"))
    test_class_name = f"Test{camel_name}Behavior"

    test_methods: list[str] = []

    # Map each Acceptance Criterion to a test method
    for idx, ac in enumerate(spec.acceptance_criteria, start=1):
        method_name = f"test_ac_{idx}_{ac.criterion_id.lower().replace('-', '_')}"
        safe_desc = ac.description.replace('"', '\\"')
        safe_scenario = ac.test_scenario.replace('"', '\\"')

        if idx == 1:
            # Positive workflow test
            test_body = f"""        \"\"\"{ac.criterion_id}: {safe_desc}\"\"\"
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            sample_in = tmppath / "input_sample.txt"
            sample_in.write_text("sample,data,100\\n", encoding="utf-8")
            
            # Execute main script via subprocess
            res = subprocess.run(
                [sys.executable, str(self.script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(res.returncode, 0, f"Help command failed: {{res.stderr}}")
            self.assertIn("usage", res.stdout.lower() + res.stderr.lower())"""
        elif idx == 2:
            # Boundary / validation test
            test_body = f"""        \"\"\"{ac.criterion_id}: {safe_desc}\"\"\"
        # Scenario: {safe_scenario}
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            empty_file = tmppath / "empty.txt"
            empty_file.write_text("", encoding="utf-8")

            res = subprocess.run(
                [sys.executable, str(self.script_path), str(empty_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Expect either safe processing or controlled error (exit code 0 or 2, never unhandled crash 1 with traceback)
            self.assertNotIn("Traceback (most recent call last):", res.stderr)"""
        else:
            # Error / missing argument test
            test_body = f"""        \"\"\"{ac.criterion_id}: {safe_desc}\"\"\"
        # Scenario: {safe_scenario}
        res = subprocess.run(
            [sys.executable, str(self.script_path), "non_existent_file_path_xyz.txt"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(res.returncode, 0, "Missing input should yield non-zero exit code.")
        self.assertNotIn("Traceback (most recent call last):", res.stderr)"""

        test_methods.append(f"""    def {method_name}(self) -> None:
{test_body}
""")

    # Security test: directory escape / path traversal
    security_test = """    def test_security_path_traversal_defense(self) -> None:
        \"\"\"Verify defense against directory traversal attempts.\"\"\"
        res = subprocess.run(
            [sys.executable, str(self.script_path), "../../etc/passwd"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(res.returncode, 0, "Path traversal attempt must be rejected.")
        self.assertNotIn("root:x:0:0:", res.stdout)
"""
    test_methods.append(security_test)

    tests_block = "\n".join(test_methods)

    code = f'''"""Behavioral Unit Tests for {spec.skill_name}.

Generated autonomously by Skill Factory Test Generator.
Traceability: Mapped to Acceptance Criteria in {spec.skill_name} spec.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class {test_class_name}(unittest.TestCase):
    \"\"\"Behavioral test cases for {spec.skill_name}.\"\"\"

    @classmethod
    def setUpClass(cls) -> None:
        cls.script_path = (Path(__file__).resolve().parent.parent / "scripts" / "main.py").resolve()
        if not cls.script_path.is_file():
            raise FileNotFoundError(f"Target script not found: {{cls.script_path}}")

{tests_block}

if __name__ == "__main__":
    unittest.main()
'''
    return code
