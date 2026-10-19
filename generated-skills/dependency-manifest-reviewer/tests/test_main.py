"""Tests for dependency-manifest-reviewer."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import format_markdown_report, review_requirements_lines


class TestDependencyManifestReviewer(unittest.TestCase):
    def test_review_vulnerabilities(self):
        lines = [
            "requests==2.31.0",                                   # Clean
            "urllib3>=1.26.0",                                     # Unbounded
            "unpinned-pkg",                                        # Completely unpinned
            "git+https://github.com/example/repo.git",             # Mutable VCS without commit
            "insecure-pkg @ http://insecure.example.com/pkg.whl",  # Insecure HTTP
            "requests==2.31.0",                                   # Duplicate
        ]
        res = review_requirements_lines(lines)
        self.assertEqual(res["total_dependencies"], 5)
        self.assertEqual(res["findings_count"], 5)
        self.assertFalse(res["is_secure"])

        md = format_markdown_report(res, "requirements.txt")
        self.assertIn("# Dependency Manifest Review", md)
        self.assertIn("DEP-01", md)
        self.assertIn("DEP-02", md)


if __name__ == "__main__":
    unittest.main()
