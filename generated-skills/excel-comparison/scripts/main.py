#!/usr/bin/env python3
"""Main script for excel-comparison: compares two Excel or CSV spreadsheets row-by-row and cell-by-cell."""
from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CellDiff:
    column: str
    old_value: str
    new_value: str


@dataclass
class RowDiff:
    key_value: str
    diff_type: str  # "added", "removed", "modified"
    details: Dict[str, Any] = field(default_factory=dict)
    cell_diffs: List[CellDiff] = field(default_factory=list)


@dataclass
class ComparisonReport:
    file1: str
    file2: str
    is_identical: bool
    total_rows_file1: int
    total_rows_file2: int
    added_count: int
    removed_count: int
    modified_count: int
    identical_count: int
    columns_file1: List[str]
    columns_file2: List[str]
    diffs: List[RowDiff] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


def _strip_ns(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def parse_xlsx(file_path: Path, sheet_name: Optional[str] = None) -> Tuple[List[str], List[Dict[str, str]]]:
    """Parse an .xlsx file using standard library zipfile and xml.etree."""
    with zipfile.ZipFile(file_path, "r") as zf:
        # Load shared strings if present
        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            with zf.open("xl/sharedStrings.xml") as s_file:
                root = ET.parse(s_file).getroot()
                for elem in root.iter():
                    if _strip_ns(elem.tag) == "si":
                        text_parts = [ch.text or "" for ch in elem.iter() if _strip_ns(ch.tag) == "t"]
                        shared_strings.append("".join(text_parts))

        # Find sheets in workbook.xml
        sheet_filename = "xl/worksheets/sheet1.xml"
        if "xl/workbook.xml" in zf.namelist():
            with zf.open("xl/workbook.xml") as wb_file:
                wb_root = ET.parse(wb_file).getroot()
                sheet_idx = 1
                for s in wb_root.iter():
                    if _strip_ns(s.tag) == "sheet":
                        if sheet_name and s.attrib.get("name") == sheet_name:
                            sheet_filename = f"xl/worksheets/sheet{sheet_idx}.xml"
                            break
                        sheet_idx += 1

        if sheet_filename not in zf.namelist():
            sheet_files = [n for n in zf.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
            if not sheet_files:
                raise ValueError(f"No worksheet found in Excel file {file_path}")
            sheet_filename = sheet_files[0]

        with zf.open(sheet_filename) as ws_file:
            ws_root = ET.parse(ws_file).getroot()
            all_raw_rows: List[List[str]] = []
            for elem in ws_root.iter():
                if _strip_ns(elem.tag) == "row":
                    row_vals: List[str] = []
                    for c in elem:
                        if _strip_ns(c.tag) == "c":
                            cell_type = c.attrib.get("t")
                            val_node = None
                            for ch in c:
                                if _strip_ns(ch.tag) == "v":
                                    val_node = ch
                                    break
                            raw_val = val_node.text.strip() if val_node is not None and val_node.text else ""
                            if cell_type == "s" and raw_val.isdigit():
                                idx = int(raw_val)
                                val_str = shared_strings[idx] if idx < len(shared_strings) else raw_val
                            else:
                                val_str = raw_val
                            row_vals.append(val_str)
                    if any(row_vals):
                        all_raw_rows.append(row_vals)

    if not all_raw_rows:
        return [], []

    headers = all_raw_rows[0]
    records: List[Dict[str, str]] = []
    for r in all_raw_rows[1:]:
        row_dict = {}
        for idx, h in enumerate(headers):
            row_dict[h] = r[idx] if idx < len(r) else ""
        records.append(row_dict)

    return headers, records


def parse_delimited(file_path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    """Parse CSV or TSV file into header list and row dictionaries."""
    text = file_path.read_text(encoding="utf-8-sig", errors="replace")
    if not text.strip():
        return [], []

    # Detect delimiter
    first_line = text.strip().splitlines()[0]
    delimiter = "\t" if "\t" in first_line and first_line.count("\t") > first_line.count(",") else ","

    reader = csv.DictReader(text.splitlines(), delimiter=delimiter)
    headers = list(reader.fieldnames or [])
    records = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
    return headers, records


def load_table(file_path: Path, sheet_name: Optional[str] = None) -> Tuple[List[str], List[Dict[str, str]]]:
    """Load table data from Excel (.xlsx) or CSV/TSV file."""
    suffix = file_path.suffix.lower()
    if suffix in (".xlsx", ".xlsm"):
        return parse_xlsx(file_path, sheet_name=sheet_name)
    elif suffix in (".csv", ".tsv", ".txt"):
        return parse_delimited(file_path)
    else:
        # Try CSV first, if binary or zip try XLSX
        try:
            return parse_delimited(file_path)
        except Exception:
            return parse_xlsx(file_path, sheet_name=sheet_name)


def compare_spreadsheets(
    file1_path: Path,
    file2_path: Path,
    key_column: Optional[str] = None,
    sheet_name: Optional[str] = None,
    ignore_columns: Optional[List[str]] = None,
) -> ComparisonReport:
    """Compare two spreadsheets and produce a structured ComparisonReport."""
    headers1, rows1 = load_table(file1_path, sheet_name=sheet_name)
    headers2, rows2 = load_table(file2_path, sheet_name=sheet_name)

    ignore_set = set(ignore_columns or [])
    all_headers = sorted(list(set(headers1) | set(headers2)))
    eval_headers = [h for h in all_headers if h not in ignore_set and h != key_column]

    diffs: List[RowDiff] = []
    added_count = 0
    removed_count = 0
    modified_count = 0
    identical_count = 0

    if key_column and (key_column in headers1 or key_column in headers2):
        # Key-based comparison
        map1: Dict[str, Dict[str, str]] = {}
        for idx, r in enumerate(rows1):
            k = r.get(key_column, f"ROW_{idx+1}")
            map1[k] = r

        map2: Dict[str, Dict[str, str]] = {}
        for idx, r in enumerate(rows2):
            k = r.get(key_column, f"ROW_{idx+1}")
            map2[k] = r

        all_keys = list(map1.keys()) + [k for k in map2.keys() if k not in map1]

        for k in all_keys:
            in1 = k in map1
            in2 = k in map2

            if in1 and not in2:
                removed_count += 1
                diffs.append(RowDiff(key_value=k, diff_type="removed", details=map1[k]))
            elif in2 and not in1:
                added_count += 1
                diffs.append(RowDiff(key_value=k, diff_type="added", details=map2[k]))
            else:
                r1 = map1[k]
                r2 = map2[k]
                cell_diffs: List[CellDiff] = []
                for col in eval_headers:
                    val1 = r1.get(col, "")
                    val2 = r2.get(col, "")
                    if val1 != val2:
                        cell_diffs.append(CellDiff(column=col, old_value=val1, new_value=val2))

                if cell_diffs:
                    modified_count += 1
                    diffs.append(RowDiff(key_value=k, diff_type="modified", cell_diffs=cell_diffs))
                else:
                    identical_count += 1
    else:
        # Index-based row-by-row comparison
        max_rows = max(len(rows1), len(rows2))
        for idx in range(max_rows):
            k = f"Row #{idx + 1}"
            if idx >= len(rows1):
                added_count += 1
                diffs.append(RowDiff(key_value=k, diff_type="added", details=rows2[idx]))
            elif idx >= len(rows2):
                removed_count += 1
                diffs.append(RowDiff(key_value=k, diff_type="removed", details=rows1[idx]))
            else:
                r1 = rows1[idx]
                r2 = rows2[idx]
                cell_diffs = []
                for col in eval_headers:
                    val1 = r1.get(col, "")
                    val2 = r2.get(col, "")
                    if val1 != val2:
                        cell_diffs.append(CellDiff(column=col, old_value=val1, new_value=val2))

                if cell_diffs:
                    modified_count += 1
                    diffs.append(RowDiff(key_value=k, diff_type="modified", cell_diffs=cell_diffs))
                else:
                    identical_count += 1

    is_identical = (added_count == 0 and removed_count == 0 and modified_count == 0)

    return ComparisonReport(
        file1=str(file1_path),
        file2=str(file2_path),
        is_identical=is_identical,
        total_rows_file1=len(rows1),
        total_rows_file2=len(rows2),
        added_count=added_count,
        removed_count=removed_count,
        modified_count=modified_count,
        identical_count=identical_count,
        columns_file1=headers1,
        columns_file2=headers2,
        diffs=diffs,
    )


def format_report_text(report: ComparisonReport) -> str:
    """Format report into human-readable markdown summary."""
    lines = [
        "Spreadsheet Comparison Report",
        "=" * 60,
        f"Base File:     {report.file1} ({report.total_rows_file1} rows)",
        f"Compared File: {report.file2} ({report.total_rows_file2} rows)",
        f"Status:        {'IDENTICAL' if report.is_identical else 'DIFFERENCES FOUND'}",
        "-" * 60,
        f"Summary:       {report.identical_count} identical, {report.modified_count} modified, {report.added_count} added, {report.removed_count} removed",
        "",
    ]

    if not report.is_identical:
        lines.append("Discrepancy Details:")
        for d in report.diffs:
            if d.diff_type == "modified":
                changes = ", ".join(f"{cd.column}: '{cd.old_value}' -> '{cd.new_value}'" for cd in d.cell_diffs)
                lines.append(f"  [MODIFIED] {d.key_value}: {changes}")
            elif d.diff_type == "added":
                lines.append(f"  [ADDED]    {d.key_value}: {d.details}")
            elif d.diff_type == "removed":
                lines.append(f"  [REMOVED]  {d.key_value}: {d.details}")

    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compares two Excel spreadsheets or CSV files row-by-row and cell-by-cell."
    )
    parser.add_argument("file1", help="Path to base spreadsheet (CSV or XLSX)")
    parser.add_argument("file2", help="Path to compared spreadsheet (CSV or XLSX)")
    parser.add_argument("--key", help="Primary key column name used to align rows across files")
    parser.add_argument("--sheet", help="Worksheet name (for .xlsx files)")
    parser.add_argument("--ignore", nargs="*", default=[], help="Columns to ignore during comparison")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON format")
    parser.add_argument("--output", help="Save report to specified output path")

    args = parser.parse_args(argv)

    p1 = Path(args.file1)
    p2 = Path(args.file2)

    if not p1.exists():
        print(f"Error: File 1 does not exist: {p1}", file=sys.stderr)
        return 2
    if not p2.exists():
        print(f"Error: File 2 does not exist: {p2}", file=sys.stderr)
        return 2

    try:
        report = compare_spreadsheets(
            p1,
            p2,
            key_column=args.key,
            sheet_name=args.sheet,
            ignore_columns=args.ignore,
        )
    except Exception as err:
        print(f"Error during comparison: {err}", file=sys.stderr)
        return 2

    if args.json:
        output_text = json.dumps(report.to_dict(), indent=2)
    else:
        output_text = format_report_text(report)

    if args.output:
        Path(args.output).write_text(output_text + "\n", encoding="utf-8")
    else:
        print(output_text)

    return 0 if report.is_identical else 1


if __name__ == "__main__":
    sys.exit(main())
