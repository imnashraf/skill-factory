"""Tests for skillfactory/yaml_util.py (verifying DEF-01 fix)."""
from __future__ import annotations

import unittest
from skillfactory.yaml_util import dump_frontmatter, parse_frontmatter, dump_yaml_scalar, YamlError


class YamlUtilTests(unittest.TestCase):
    def test_safe_scalar_escaping(self):
        # Colon followed by space
        val = "Compare files: report diffs"
        self.assertEqual(dump_yaml_scalar(val), '"Compare files: report diffs"')

        # Hash character
        val2 = "#1 tool for PDFs"
        self.assertEqual(dump_yaml_scalar(val2), '"#1 tool for PDFs"')

        # Single and double quotes
        val3 = "It's 'quoted' and \"double-quoted\""
        self.assertEqual(dump_yaml_scalar(val3), '"It\'s \'quoted\' and \\"double-quoted\\""')

    def test_roundtrip_complex_frontmatter(self):
        data = {
            "name": "excel-diff",
            "description": "Compare two Excel files: report differences, #1 tool for data auditing.",
            "compatibility": "Works with Claude Code, Cursor, Codex, and Antigravity.",
            "metadata": {
                "author": "Test Author",
                "version": "1.0.0",
            },
        }
        yaml_text = dump_frontmatter(data)
        parsed, body = parse_frontmatter(yaml_text + "\n# Skill Title\n\nSome body text.\n")
        self.assertEqual(parsed, data)
        self.assertEqual(body.strip(), "# Skill Title\n\nSome body text.")

    def test_parse_folded_description(self):
        content = """---
name: folded-skill
description: >
  This is a folded description that spans
  multiple lines in the frontmatter.
---

Body content
"""
        parsed, body = parse_frontmatter(content)
        self.assertEqual(parsed["name"], "folded-skill")
        self.assertEqual(
            parsed["description"],
            "This is a folded description that spans multiple lines in the frontmatter.",
        )
        self.assertEqual(body.strip(), "Body content")

    def test_invalid_frontmatter(self):
        # Missing start delimiter
        with self.assertRaises(YamlError):
            parse_frontmatter("# No frontmatter\nBody\n")

        # Missing end delimiter
        with self.assertRaises(YamlError):
            parse_frontmatter("---\nname: bad-skill\n")

    def test_def01_yaml_break_characters(self):
        """DEF-01: Ensure descriptions with colons, quotes, and hashes parse back identically."""
        break_cases = [
            "Compare files: report diffs",
            "#1 tool for PDFs",
            "'Single quoted' and \"double quoted\"",
            "Key: Value pairs in description: e.g. foo: bar",
            "Special chars: [brackets], {braces}, @mention, *pointer, &anchor",
            "Multi: colon: in: one: sentence: with # hash at end",
        ]
        for desc in break_cases:
            data = {"name": "sample-skill", "description": desc}
            frontmatter = dump_frontmatter(data)
            parsed, _ = parse_frontmatter(frontmatter)
            self.assertEqual(parsed["description"], desc, f"Failed on case: {desc}")


if __name__ == "__main__":
    unittest.main()
