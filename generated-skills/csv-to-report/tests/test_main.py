"""Automated test suite for csv-to-report."""
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

from main import analyze_csv, main, render_markdown


class CsvToReportTests(unittest.TestCase):
    def test_numeric_and_categorical_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "sales.csv"
            f.write_text(
                "Region,Sales,Quantity\n"
                "North,100.50,5\n"
                "North,200.00,10\n"
                "South,150.25,8\n"
                "West,,12\n",  # null in sales
                encoding="utf-8"
            )
            rows, stats = analyze_csv(f)
            self.assertEqual(rows, 4)
            self.assertEqual(len(stats), 3)

            col_map = {s.name: s for s in stats}
            # Region (Categorical)
            self.assertEqual(col_map["Region"].dtype, "str")
            self.assertEqual(col_map["Region"].unique_count, 3)

            # Sales (Numeric float with 1 null)
            self.assertEqual(col_map["Sales"].dtype, "float")
            self.assertEqual(col_map["Sales"].null_count, 1)
            self.assertAlmostEqual(col_map["Sales"].min_val, 100.50)

            # Quantity (Numeric int)
            self.assertEqual(col_map["Quantity"].dtype, "int")
            self.assertEqual(col_map["Quantity"].null_count, 0)
            self.assertEqual(col_map["Quantity"].sum_val, 35)

    def test_tsv_delimiter_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "data.tsv"
            f.write_text("ID\tStatus\n1\tActive\n2\tPending\n", encoding="utf-8")
            rows, stats = analyze_csv(f)
            self.assertEqual(rows, 2)
            self.assertEqual(len(stats), 2)
            self.assertEqual(stats[0].name, "ID")

    def test_markdown_rendering(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "sample.csv"
            f.write_text("Item,Cost\nWidget,10\nGadget,20\n", encoding="utf-8")
            rows, stats = analyze_csv(f)
            md = render_markdown("Test Report", str(f), rows, stats)
            self.assertIn("# Test Report", md)
            self.assertIn("| **Cost** | `int` |", md)
            self.assertIn("| **Item** | `str` |", md)

    def test_cli_json_and_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            in_file = Path(tmp) / "input.csv"
            in_file.write_text("A,B\n1,2\n3,4\n", encoding="utf-8")
            out_file = Path(tmp) / "report.json"

            rc = main([str(in_file), "--format", "json", "--out", str(out_file)])
            self.assertEqual(rc, 0)
            self.assertTrue(out_file.exists())

            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["rows"], 2)

    def test_missing_file_error(self):
        rc = main(["/nonexistent/sample.csv"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
