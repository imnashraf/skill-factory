"""Automated test suite for file-organizer."""
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

from main import (
    categorize_file,
    execute_organization,
    main,
    plan_organization,
    sanitize_filename,
)


class FileOrganizerTests(unittest.TestCase):
    def test_categorization(self):
        self.assertEqual(categorize_file(Path("notes.pdf")), "documents")
        self.assertEqual(categorize_file(Path("data.csv")), "spreadsheets")
        self.assertEqual(categorize_file(Path("photo.png")), "images")
        self.assertEqual(categorize_file(Path("backup.zip")), "archives")
        self.assertEqual(categorize_file(Path("script.py")), "code")
        self.assertEqual(categorize_file(Path("unknown.xyz")), "other")

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("My  Important   File!.pdf"), "My_Important_File.pdf")
        self.assertEqual(sanitize_filename("  spaces  everywhere  "), "spaces_everywhere")

    def test_dry_run_leaves_files_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "intake"
            src.mkdir()
            (src / "document.pdf").write_text("dummy doc", encoding="utf-8")
            (src / "table.xlsx").write_text("dummy sheet", encoding="utf-8")

            # Execute dry run
            from unittest.mock import patch
            with patch("sys.stdout", new_callable=io.StringIO) as fake_out:
                rc = main([str(src), "--dry-run", "--json"])
                self.assertEqual(rc, 0)
                data = json.loads(fake_out.getvalue())
                self.assertEqual(data["status"], "dry_run")
                self.assertEqual(data["planned_moves"], 2)

            # Files must still be at original location
            self.assertTrue((src / "document.pdf").exists())
            self.assertTrue((src / "table.xlsx").exists())
            self.assertFalse((src / "documents").exists())

    def test_live_organization_and_collision_avoidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "intake"
            dest = Path(tmp) / "organized"
            src.mkdir()
            dest.mkdir()

            # Create test files
            (src / "doc1.txt").write_text("doc1", encoding="utf-8")
            (src / "img.png").write_text("img", encoding="utf-8")

            # Create existing collision target in dest
            (dest / "documents").mkdir(parents=True)
            (dest / "documents" / "doc1.txt").write_text("existing doc", encoding="utf-8")

            # Run organization
            rc = main([str(src), "--dest", str(dest), "--sanitize"])
            self.assertEqual(rc, 0)

            # Check that doc1 was renamed with _1 to avoid collision
            self.assertTrue((dest / "documents" / "doc1_1.txt").exists())
            self.assertTrue((dest / "images" / "img.png").exists())
            # Existing target wasn't overwritten
            self.assertEqual((dest / "documents" / "doc1.txt").read_text(), "existing doc")

    def test_prefix_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "intake"
            src.mkdir()
            (src / "contract.pdf").write_text("contract", encoding="utf-8")

            rc = main([str(src), "--prefix", "2026", "--json"])
            self.assertEqual(rc, 0)
            self.assertTrue((src / "documents" / "2026_contract.pdf").exists())

    def test_nonexistent_directory_error(self):
        rc = main(["/nonexistent/fake/directory/xyz"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
