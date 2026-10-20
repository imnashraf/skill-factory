"""Automated test suite for markdown-doc-validator."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
import sys

scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from main import main, validate_file, validate_repository


class MarkdownValidatorTests(unittest.TestCase):
    def test_clean_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "clean.md"
            doc.write_text(
                "# Main Title\n\n"
                "## Section 1\n\n"
                "Here is [a link](https://example.com) and an [anchor](#section-1).\n\n"
                "```python\n"
                "print('hello')\n"
                "```\n\n"
                "| Header 1 | Header 2 |\n"
                "| --- | --- |\n"
                "| Val 1 | Val 2 |\n",
                encoding="utf-8"
            )
            issues = validate_file(doc, Path(tmp))
            self.assertEqual(len(issues), 0)

    def test_detects_broken_relative_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "test.md"
            doc.write_text(
                "# Title\n\n"
                "Check out [the missing manual](docs/nonexistent.md).\n",
                encoding="utf-8"
            )
            issues = validate_file(doc, Path(tmp))
            rule_ids = {i.rule_id for i in issues}
            self.assertIn("MD-BROKEN-LINK", rule_ids)

    def test_detects_unlabeled_code_fences(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "test.md"
            doc.write_text(
                "# Title\n\n"
                "```\n"
                "plain code without lang\n"
                "```\n",
                encoding="utf-8"
            )
            issues = validate_file(doc, Path(tmp))
            rule_ids = {i.rule_id for i in issues}
            self.assertIn("MD-NO-LANG", rule_ids)

    def test_detects_unspaced_table_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "test.md"
            doc.write_text(
                "# Title\n\n"
                "| A | B |\n"
                "|---|---|\n"
                "| 1 | 2 |\n",
                encoding="utf-8"
            )
            issues = validate_file(doc, Path(tmp))
            rule_ids = {i.rule_id for i in issues}
            self.assertIn("MD-TABLE-SEP", rule_ids)

    def test_detects_empty_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "test.md"
            doc.write_text(
                "# Title\n\n"
                "## \n",
                encoding="utf-8"
            )
            issues = validate_file(doc, Path(tmp))
            rule_ids = {i.rule_id for i in issues}
            self.assertIn("MD-EMPTY-HEAD", rule_ids)

    def test_cli_json_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "broken.md"
            doc.write_text("# Title\n[bad](nowhere.md)\n", encoding="utf-8")

            from unittest.mock import patch
            with patch("sys.stdout", new_callable=io.StringIO) as fake_out:
                rc = main([str(doc), "--json", "--fail-on-errors"])
                self.assertEqual(rc, 1)
                data = json.loads(fake_out.getvalue())
                self.assertEqual(data["status"], "success")
                self.assertGreater(data["errors"], 0)

    def test_nonexistent_path_error(self):
        rc = main(["/nonexistent/fake/file.md"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
