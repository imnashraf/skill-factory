"""Tests for test-inventory-analyzer."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

script_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_path))
from main import analyze_test_directory, format_markdown_report


class TestInventoryAnalyzer(unittest.TestCase):
    def test_analyze_sample_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sample_test = tmp_path / "test_example.py"
            sample_test.write_text(
                """import unittest
class SampleTest(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(1, 1)
        self.assertTrue(True)
    def test_beta(self):
        assert 2 == 2
    @unittest.skip("skip reason")
    def test_gamma(self):
        pass
""",
                encoding="utf-8",
            )
            data = analyze_test_directory(tmp_path)
            self.assertEqual(data["test_files_count"], 1)
            self.assertEqual(data["total_test_functions"], 3)
            self.assertEqual(data["total_assertions"], 3) # assertEqual + assertTrue + assert
            self.assertEqual(data["total_skipped_tests"], 1)

            md = format_markdown_report(data)
            self.assertIn("# Test Inventory & Suite Audit Report", md)
            self.assertIn("test_example.py", md)


if __name__ == "__main__":
    unittest.main()
