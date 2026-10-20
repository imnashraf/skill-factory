#!/usr/bin/env python3
"""Smart File Organizer & Renamer (file-organizer).

Organizes files into structured categories, applies sanitization, date organization,
and collision avoidance with dry-run support.
Pure Python standard library implementation with zero external dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CATEGORY_EXTENSIONS: Dict[str, set[str]] = {
    "documents": {".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt"},
    "spreadsheets": {".xlsx", ".xls", ".csv", ".tsv", ".ods"},
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"},
    "media": {".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".flac"},
    "archives": {".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"},
    "code": {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".yaml", ".yml", ".sh"},
}


@dataclass
class MoveOperation:
    source_path: str
    target_path: str
    category: str
    renamed: bool

    def to_dict(self) -> dict:
        return asdict(self)


def categorize_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    for cat, exts in CATEGORY_EXTENSIONS.items():
        if ext in exts:
            return cat
    return "other"


def sanitize_filename(name: str) -> str:
    # Replace spaces with underscores and remove problematic filesystem characters
    name = re.sub(r"[^\w\s.-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name


def get_unique_target_path(target_path: Path) -> Path:
    """Ensure target path does not collide with existing file by appending incrementing index."""
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def plan_organization(
    source_dir: Path,
    dest_dir: Optional[Path] = None,
    by_date: bool = False,
    sanitize: bool = False,
    prefix: str = "",
) -> List[MoveOperation]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    target_root = dest_dir if dest_dir is not None else source_dir
    operations: List[MoveOperation] = []

    for entry in sorted(source_dir.iterdir()):
        if not entry.is_file():
            continue
        # Skip hidden/system files
        if entry.name.startswith("."):
            continue

        category = categorize_file(entry)
        dest_folder = target_root / category

        if by_date:
            mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc)
            date_segment = mtime.strftime("%Y/%m")
            dest_folder = dest_folder / date_segment

        new_name = entry.name
        if sanitize:
            stem = sanitize_filename(entry.stem)
            new_name = f"{stem}{entry.suffix.lower()}"

        if prefix:
            new_name = f"{prefix}_{new_name}"

        ideal_target = dest_folder / new_name
        unique_target = get_unique_target_path(ideal_target)

        # Only add if source and target differ
        if entry.resolve() != unique_target.resolve():
            operations.append(
                MoveOperation(
                    source_path=str(entry),
                    target_path=str(unique_target),
                    category=category,
                    renamed=(entry.name != unique_target.name),
                )
            )

    return operations


def execute_organization(operations: List[MoveOperation], dry_run: bool = False) -> int:
    moved_count = 0
    for op in operations:
        src = Path(op.source_path)
        dest = Path(op.target_path)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dest)
        moved_count += 1
    return moved_count


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Organize and rename files into structured directories.",
    )
    parser.add_argument("source", help="Source directory containing files to organize")
    parser.add_argument("--dest", help="Destination directory (default: organize inside source)")
    parser.add_argument("--by-date", action="store_true", help="Organize into YYYY/MM subdirectories")
    parser.add_argument("--sanitize", action="store_true", help="Replace spaces and special characters with underscores")
    parser.add_argument("--prefix", default="", help="Optional prefix to add to organized filenames")
    parser.add_argument("--dry-run", action="store_true", help="Preview planned operations without moving files")
    parser.add_argument("--json", action="store_true", help="Output plan or results in JSON format")

    args = parser.parse_args(argv)
    source_path = Path(args.source)
    dest_path = Path(args.dest) if args.dest else None

    try:
        operations = plan_organization(
            source_dir=source_path,
            dest_dir=dest_path,
            by_date=args.by_date,
            sanitize=args.sanitize,
            prefix=args.prefix,
        )
    except Exception as err:
        if args.json:
            print(json.dumps({"status": "error", "error": str(err)}, indent=2))
        else:
            print(f"[ERROR] Failed to plan organization: {err}", file=sys.stderr)
        return 2

    if args.dry_run:
        if args.json:
            print(
                json.dumps(
                    {
                        "status": "dry_run",
                        "planned_moves": len(operations),
                        "operations": [op.to_dict() for op in operations],
                    },
                    indent=2,
                )
            )
        else:
            print(f"[INFO] Dry Run: {len(operations)} files to be organized:")
            for op in operations:
                renamed_tag = " (renamed)" if op.renamed else ""
                print(f"  {Path(op.source_path).name} -> {op.category}/{Path(op.target_path).name}{renamed_tag}")
        return 0

    moved_count = execute_organization(operations, dry_run=False)

    if args.json:
        print(
            json.dumps(
                {
                    "status": "success",
                    "files_organized": moved_count,
                    "operations": [op.to_dict() for op in operations],
                },
                indent=2,
            )
        )
    else:
        print(f"[OK] Successfully organized {moved_count} files into structured categories.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
