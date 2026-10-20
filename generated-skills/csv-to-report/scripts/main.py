#!/usr/bin/env python3
"""CSV to Executive Report Generator (csv-to-report).

Analyzes tabular CSV/TSV data, computes descriptive statistics, and generates
clean Markdown, HTML, or JSON summary reports.
Pure Python standard library implementation with zero external dependencies.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ColumnStats:
    name: str
    dtype: str
    total_count: int
    null_count: int
    # Numeric
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean: Optional[float] = None
    sum_val: Optional[float] = None
    # Categorical
    unique_count: Optional[int] = None
    top_values: Optional[List[Tuple[str, int]]] = None

    def to_dict(self) -> dict:
        return asdict(self)


def infer_and_convert(val: str) -> Tuple[str, Any]:
    val = val.strip()
    if not val:
        return ("null", None)
    # Integer
    if re_match_int(val):
        try:
            return ("int", int(val))
        except ValueError:
            pass
    # Float
    try:
        f = float(val)
        if not math.isnan(f) and not math.isinf(f):
            return ("float", f)
    except ValueError:
        pass
    # Boolean
    if val.lower() in ("true", "false", "yes", "no"):
        return ("bool", val.lower() in ("true", "yes"))
    return ("str", val)


def re_match_int(s: str) -> bool:
    if s.startswith(("-", "+")):
        return s[1:].isdigit()
    return s.isdigit()


def analyze_csv(file_path: Path) -> Tuple[int, List[ColumnStats]]:
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8", errors="replace")
    if not content.strip():
        return 0, []

    # Detect delimiter
    first_line = content.splitlines()[0]
    delimiter = ","
    if "\t" in first_line:
        delimiter = "\t"
    elif ";" in first_line and "," not in first_line:
        delimiter = ";"

    reader = csv.reader(content.splitlines(), delimiter=delimiter)
    try:
        headers = next(reader)
    except StopIteration:
        return 0, []

    headers = [h.strip() or f"col_{i}" for i, h in enumerate(headers)]
    raw_columns: Dict[str, List[Any]] = {h: [] for h in headers}
    row_count = 0

    for row in reader:
        if not row or not any(row):
            continue
        row_count += 1
        for idx, h in enumerate(headers):
            val = row[idx] if idx < len(row) else ""
            raw_columns[h].append(val)

    stats_list: List[ColumnStats] = []
    for h in headers:
        values = raw_columns[h]
        typed = [infer_and_convert(v) for v in values]
        null_count = sum(1 for t, v in typed if t == "null")
        non_null = [(t, v) for t, v in typed if t != "null"]

        if not non_null:
            stats_list.append(ColumnStats(name=h, dtype="null", total_count=row_count, null_count=null_count))
            continue

        num_numeric = sum(1 for t, v in non_null if t in ("int", "float"))
        is_numeric = (num_numeric / len(non_null)) >= 0.8

        if is_numeric:
            nums = [float(v) for t, v in non_null if t in ("int", "float")]
            min_v = min(nums)
            max_v = max(nums)
            mean_v = sum(nums) / len(nums)
            sum_v = sum(nums)
            dtype = "int" if all(t == "int" for t, v in non_null) else "float"
            stats_list.append(
                ColumnStats(
                    name=h,
                    dtype=dtype,
                    total_count=row_count,
                    null_count=null_count,
                    min_val=round(min_v, 2),
                    max_val=round(max_v, 2),
                    mean=round(mean_v, 2),
                    sum_val=round(sum_v, 2),
                )
            )
        else:
            str_vals = [str(v) for t, v in non_null]
            counter = Counter(str_vals)
            unique_c = len(counter)
            top_3 = counter.most_common(3)
            stats_list.append(
                ColumnStats(
                    name=h,
                    dtype="str",
                    total_count=row_count,
                    null_count=null_count,
                    unique_count=unique_c,
                    top_values=top_3,
                )
            )

    return row_count, stats_list


def render_markdown(title: str, file_path: str, row_count: int, stats: List[ColumnStats]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- **File:** `{file_path}`",
        f"- **Total Rows:** {row_count:,}",
        f"- **Total Columns:** {len(stats)}",
        "",
        "## Numeric Column Metrics",
        "",
        "| Column | Type | Nulls | Min | Max | Mean | Sum |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    has_num = False
    for s in stats:
        if s.dtype in ("int", "float"):
            has_num = True
            lines.append(f"| **{s.name}** | `{s.dtype}` | {s.null_count} | {s.min_val} | {s.max_val} | {s.mean} | {s.sum_val} |")

    if not has_num:
        lines.append("| *(None)* | — | — | — | — | — | — |")

    lines.extend([
        "",
        "## Categorical Column Distributions",
        "",
        "| Column | Type | Nulls | Unique | Top Values (Frequency) |",
        "| --- | --- | --- | --- | --- |",
    ])

    has_cat = False
    for s in stats:
        if s.dtype not in ("int", "float"):
            has_cat = True
            top_str = ", ".join(f"`{k}` ({v})" for k, v in (s.top_values or []))
            lines.append(f"| **{s.name}** | `{s.dtype}` | {s.null_count} | {s.unique_count or 0} | {top_str or '—'} |")

    if not has_cat:
        lines.append("| *(None)* | — | — | — | — |")

    lines.append("")
    return "\n".join(lines)


def render_html(title: str, md_content: str) -> str:
    # Minimal zero-dependency HTML wrapper
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #24292f; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
th, td {{ border: 1px solid #d0d7de; padding: 8px 12px; text-align: left; }}
th {{ background: #f6f8fa; }}
code {{ background: #eff1f3; padding: 2px 4px; border-radius: 4px; }}
</style>
</head>
<body>
<pre>{md_content}</pre>
</body>
</html>
"""


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="csv-to-report",
        description="Convert tabular CSV/TSV data into structured analytical reports.",
    )
    parser.add_argument("file", help="Path to input CSV or TSV file")
    parser.add_argument("--format", choices=["markdown", "json", "html"], default="markdown", help="Report output format")
    parser.add_argument("--title", default="Data Summary Report", help="Report header title")
    parser.add_argument("--out", help="Output file path (default: stdout)")

    args = parser.parse_args(argv)
    in_path = Path(args.file)

    try:
        rows, stats = analyze_csv(in_path)
    except Exception as err:
        print(f"[ERROR] Failed to analyze CSV: {err}", file=sys.stderr)
        return 2

    if args.format == "json":
        data = {
            "status": "success",
            "file": str(in_path.resolve()),
            "rows": rows,
            "columns": len(stats),
            "stats": [s.to_dict() for s in stats],
        }
        output_text = json.dumps(data, indent=2)
    elif args.format == "html":
        md = render_markdown(args.title, str(in_path), rows, stats)
        output_text = render_html(args.title, md)
    else:
        output_text = render_markdown(args.title, str(in_path), rows, stats)

    if args.out:
        out_p = Path(args.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output_text, encoding="utf-8")
        print(f"[OK] Report written to {out_p}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
