"""Deterministic golden file tests (T2.07, AC2.07, NFR-07)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillfactory.core import generate_skill
from skillfactory.manifest import compute_sha256
from skillfactory.spec import SkillSpec


class GoldenDeterminismTests(unittest.TestCase):
    def test_byte_identical_reproducibility(self):
        """AC2.07: Identical spec produces 100% byte-identical files across independent runs."""
        spec = SkillSpec(
            name="deterministic-skill",
            description="Testing byte-identical reproducibility.",
            template_family="python-script",
            author="Deterministic Author",
            license="MIT",
            inputs=["file_a.txt", "file_b.txt"],
            outputs=["diff_report.json"],
            steps=["Step 1: Read files", "Step 2: Compare tokens", "Step 3: Output diff"],
            examples=[{"input": "sample", "output": "result", "description": "Quick check"}],
        )

        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            res1 = generate_skill(spec, Path(tmp1))
            res2 = generate_skill(spec, Path(tmp2))

            # Exclude manifest.json from comparison because it contains timestamps
            files1 = [
                p.relative_to(res1.target_path).as_posix()
                for p in sorted(res1.target_path.rglob("*"))
                if p.is_file() and p.name != "manifest.json"
            ]
            files2 = [
                p.relative_to(res2.target_path).as_posix()
                for p in sorted(res2.target_path.rglob("*"))
                if p.is_file() and p.name != "manifest.json"
            ]

            self.assertEqual(files1, files2, "File lists must match exactly")

            for rel_path in files1:
                path1 = res1.target_path / rel_path
                path2 = res2.target_path / rel_path

                sha1 = compute_sha256(path1)
                sha2 = compute_sha256(path2)
                self.assertEqual(
                    sha1,
                    sha2,
                    f"File '{rel_path}' is not byte-identical across runs ({sha1} != {sha2})",
                )


if __name__ == "__main__":
    unittest.main()
