"""Unit and integration test suite for excel-comparison skill."""
from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

# Add scripts directory to path
import sys
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from main import compare_spreadsheets, format_report_text, main


def create_minimal_xlsx(file_path: Path, sheet_name: str, headers: list[str], rows: list[list[str]]) -> None:
    """Helper to generate a minimal valid .xlsx file using pure standard library zipfile."""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n'
        '  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>\n'
        '  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
        '  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>\n'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>\n'
        '</Relationships>'
    )
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>\n'
        '  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>\n'
        '</Relationships>'
    )
    wb = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        '  <sheets>\n'
        f'    <sheet name="{sheet_name}" sheetId="1" r:id="rId1"/>\n'
        '  </sheets>\n'
        '</workbook>'
    )

    # Collect shared strings
    shared: list[str] = []
    str_map: dict[str, int] = {}

    def get_str_idx(val: str) -> int:
        if val not in str_map:
            str_map[val] = len(shared)
            shared.append(val)
        return str_map[val]

    all_data = [headers] + rows
    sheet_rows_xml = []
    for r_idx, r in enumerate(all_data):
        cells_xml = []
        for c_idx, cell in enumerate(r):
            s_idx = get_str_idx(cell)
            cells_xml.append(f'<c t="s"><v>{s_idx}</v></c>')
        sheet_rows_xml.append(f'<row r="{r_idx+1}">{"".join(cells_xml)}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
        f'  <sheetData>{"".join(sheet_rows_xml)}</sheetData>\n'
        '</worksheet>'
    )

    si_items = "".join(f"<si><t>{s}</t></si>" for s in shared)
    shared_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared)}" uniqueCount="{len(shared)}">\n'
        f'  {si_items}\n'
        '</sst>'
    )

    with zipfile.ZipFile(file_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        zf.writestr("xl/workbook.xml", wb)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        zf.writestr("xl/sharedStrings.xml", shared_xml)


class ExcelComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_identical_csv_comparison(self):
        """Comparing identical CSV spreadsheets returns is_identical=True and exit code 0."""
        file1 = self.tmp / "base.csv"
        file2 = self.tmp / "copy.csv"
        csv_data = "id,name,role,salary\n101,Alice,Engineer,120000\n102,Bob,Designer,105000\n"
        file1.write_text(csv_data, encoding="utf-8")
        file2.write_text(csv_data, encoding="utf-8")

        rep = compare_spreadsheets(file1, file2, key_column="id")
        self.assertTrue(rep.is_identical)
        self.assertEqual(rep.added_count, 0)
        self.assertEqual(rep.removed_count, 0)
        self.assertEqual(rep.modified_count, 0)
        self.assertEqual(rep.identical_count, 2)

        # CLI exit code check
        exit_code = main([str(file1), str(file2), "--key", "id"])
        self.assertEqual(exit_code, 0)

    def test_csv_modifications_detected(self):
        """Modified cells are accurately detected with old and new values."""
        file1 = self.tmp / "base.csv"
        file2 = self.tmp / "updated.csv"
        file1.write_text("id,name,role,salary\n101,Alice,Engineer,120000\n102,Bob,Designer,105000\n", encoding="utf-8")
        file2.write_text("id,name,role,salary\n101,Alice,Senior Engineer,140000\n102,Bob,Designer,105000\n", encoding="utf-8")

        rep = compare_spreadsheets(file1, file2, key_column="id")
        self.assertFalse(rep.is_identical)
        self.assertEqual(rep.modified_count, 1)
        self.assertEqual(rep.identical_count, 1)

        diff = rep.diffs[0]
        self.assertEqual(diff.key_value, "101")
        self.assertEqual(diff.diff_type, "modified")
        changed_cols = {c.column: (c.old_value, c.new_value) for c in diff.cell_diffs}
        self.assertEqual(changed_cols["role"], ("Engineer", "Senior Engineer"))
        self.assertEqual(changed_cols["salary"], ("120000", "140000"))

        exit_code = main([str(file1), str(file2), "--key", "id"])
        self.assertEqual(exit_code, 1)

    def test_csv_added_and_removed_rows(self):
        """Added and removed rows are detected accurately based on primary key."""
        file1 = self.tmp / "base.csv"
        file2 = self.tmp / "updated.csv"
        file1.write_text("id,name\n1,Alpha\n2,Beta\n", encoding="utf-8")
        file2.write_text("id,name\n2,Beta\n3,Gamma\n", encoding="utf-8")

        rep = compare_spreadsheets(file1, file2, key_column="id")
        self.assertFalse(rep.is_identical)
        self.assertEqual(rep.removed_count, 1)
        self.assertEqual(rep.added_count, 1)
        self.assertEqual(rep.identical_count, 1)

        diff_types = {d.key_value: d.diff_type for d in rep.diffs}
        self.assertEqual(diff_types["1"], "removed")
        self.assertEqual(diff_types["3"], "added")

    def test_xlsx_spreadsheets_comparison(self):
        """Verify native .xlsx spreadsheet comparison works without third-party dependencies."""
        file1 = self.tmp / "sales_v1.xlsx"
        file2 = self.tmp / "sales_v2.xlsx"

        headers = ["SKU", "Product", "Qty", "Price"]
        rows1 = [
            ["SKU-01", "Keyboard", "10", "49.99"],
            ["SKU-02", "Mouse", "25", "29.99"],
        ]
        rows2 = [
            ["SKU-01", "Keyboard", "15", "49.99"],
            ["SKU-02", "Mouse", "25", "29.99"],
            ["SKU-03", "Monitor", "5", "199.99"],
        ]

        create_minimal_xlsx(file1, "Sheet1", headers, rows1)
        create_minimal_xlsx(file2, "Sheet1", headers, rows2)

        rep = compare_spreadsheets(file1, file2, key_column="SKU")
        self.assertFalse(rep.is_identical)
        self.assertEqual(rep.added_count, 1)
        self.assertEqual(rep.modified_count, 1)
        self.assertEqual(rep.identical_count, 1)

    def test_cli_json_and_output_file(self):
        """CLI flags --json and --output generate valid structured output file."""
        file1 = self.tmp / "f1.csv"
        file2 = self.tmp / "f2.csv"
        out_json = self.tmp / "diff_report.json"

        file1.write_text("code,val\nA,10\n", encoding="utf-8")
        file2.write_text("code,val\nA,20\n", encoding="utf-8")

        exit_code = main([str(file1), str(file2), "--key", "code", "--json", "--output", str(out_json)])
        self.assertEqual(exit_code, 1)
        self.assertTrue(out_json.exists())

        loaded = json.loads(out_json.read_text(encoding="utf-8"))
        self.assertFalse(loaded["is_identical"])
        self.assertEqual(loaded["modified_count"], 1)

    def test_file_not_found_handling(self):
        """Missing input file exits cleanly with return code 2 without stack trace."""
        exit_code = main(["/nonexistent/f1.csv", "/nonexistent/f2.csv"])
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
