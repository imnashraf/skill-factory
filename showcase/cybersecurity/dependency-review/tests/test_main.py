#!/usr/bin/env python3
"""Automated unit and regression tests for Dependency Manifest Reviewer (Demo 04)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
import unittest

_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from main import (
    audit_package_json,
    audit_requirements_txt,
    format_markdown_report,
)


class TestDependencyManifestReviewer(unittest.TestCase):
    def setUp(self) -> None:
        self.demo_dir = Path(__file__).resolve().parent.parent
        self.inputs_dir = self.demo_dir / "sample-inputs"
        self.expected_dir = self.demo_dir / "expected-outputs"

    def test_valid_pinned_requirements(self) -> None:
        """Verify cleanly pinned requirements have 0 findings and is_clean == True."""
        path = self.inputs_dir / "valid_requirements.txt"
        h_pre = hashlib.sha256(path.read_bytes()).hexdigest()

        lines = path.read_text(encoding="utf-8").splitlines()
        data = audit_requirements_txt(lines, path.name)

        self.assertTrue(data["is_clean"])
        self.assertEqual(data["total_findings"], 0)
        self.assertEqual(data["total_dependencies_declared"], 6)

        # File immutability check
        h_post = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(h_pre, h_post)

    def test_edge_case_findings_and_rules(self) -> None:
        """Verify detection of insecure HTTP, mutable VCS, conflicts, duplicates, unpinned, and wildcards."""
        path = self.inputs_dir / "edge_case_requirements.txt"
        lines = path.read_text(encoding="utf-8").splitlines()
        data = audit_requirements_txt(lines, path.name)

        self.assertFalse(data["is_clean"])
        rule_ids = [f["rule_id"] for f in data["findings"]]

        self.assertIn("DEP-01", rule_ids)  # Insecure HTTP
        self.assertIn("DEP-02", rule_ids)  # Mutable VCS
        self.assertIn("DEP-03", rule_ids)  # Conflicting requirements
        self.assertIn("DEP-04", rule_ids)  # Duplicate requirement
        self.assertIn("DEP-05", rule_ids)  # Unpinned dependency
        self.assertIn("DEP-06", rule_ids)  # Wildcard / unbounded

    def test_package_json_parsing_and_audit(self) -> None:
        """Verify package.json dependency auditing."""
        valid_json = json.dumps({
            "dependencies": {"express": "4.18.2"},
            "devDependencies": {"jest": "29.5.0"}
        })
        res = audit_package_json(valid_json, "package.json")
        self.assertTrue(res["is_clean"])

        bad_json = json.dumps({
            "dependencies": {"express": "http://insecure.local/pkg.tgz"},
            "devDependencies": {"express": "4.18.2"}
        })
        res_bad = audit_package_json(bad_json, "package.json")
        self.assertFalse(res_bad["is_clean"])
        rule_ids = [f["rule_id"] for f in res_bad["findings"]]
        self.assertIn("DEP-01", rule_ids)
        self.assertIn("DEP-03", rule_ids)

    def test_markdown_report_matches_expected(self) -> None:
        """Verify markdown report matches expected golden report."""
        path = self.inputs_dir / "valid_requirements.txt"
        expected_md = (self.expected_dir / "valid_review_report.md").read_text(encoding="utf-8")

        lines = path.read_text(encoding="utf-8").splitlines()
        data = audit_requirements_txt(lines, path.name)
        rendered_md = format_markdown_report(data)

        self.assertEqual(rendered_md.strip(), expected_md.strip())


if __name__ == "__main__":
    unittest.main()
