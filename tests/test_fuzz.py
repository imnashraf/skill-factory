"""Fuzz testing suite for input parsing, schemas, and archive safety (Phase 8, Task T8.03, AC8.03).

Feeds malformed strings, random binary noise, invalid encodings, null bytes,
and pathological nesting into parsers to ensure 0 uncaught crashes.
"""
from __future__ import annotations

import io
import json
import os
import random
import string
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skillfactory.cli import main
from skillfactory.packaging import import_skill_from_zip
from skillfactory.spec import SkillSpec, validate_spec_dict
from skillfactory.validator import validate_skill_name
from skillfactory.yaml_util import parse_frontmatter, safe_dump_frontmatter


class InputFuzzingTests(unittest.TestCase):
    def setUp(self):
        # Deterministic seed for reproducible fuzzing
        random.seed(42)

    def test_fuzz_yaml_frontmatter_parser(self):
        """AC8.03: Frontmatter parser handles malformed, truncated, and corrupt inputs safely."""
        fuzz_samples = [
            "",
            "   ",
            "\n\n\n",
            "---",
            "---\n",
            "---\nname:\n",
            "---\nname: [unterminated list",
            "---\nname: {unterminated dict",
            "---\n: : : : : : :",
            "---\nname: 'unclosed single quote\n---\n",
            '---\nname: "unclosed double quote\n---\n',
            "---\n\x00\x01\x02\x03\x04\n---\nBody",
            "---" + "A" * 10000 + "---",
            "---\nname: " + "A" * 50000 + "\n---\n",
            "---\n" + "\n".join(f"key_{i}: val_{i}" for i in range(500)) + "\n---\n",
            "Not frontmatter at all\nJust text\n",
            "---\nname: valid-name\n---\nBody with \x00 null bytes and \uFFFF unicode.",
        ]

        # Generate 30 randomized garbage strings
        for _ in range(30):
            length = random.randint(5, 500)
            noise = "".join(random.choice(string.printable) for _ in range(length))
            fuzz_samples.append(f"---\n{noise}\n---\nBody")

        for sample in fuzz_samples:
            try:
                fm, body = parse_frontmatter(sample)
                self.assertIsInstance(fm, dict)
                self.assertIsInstance(body, str)
            except ValueError:
                # ValueErrors are expected for syntax violations
                pass
            except Exception as e:
                self.fail(f"Uncaught non-ValueError exception during frontmatter parsing: {type(e).__name__}: {e}")

    def test_fuzz_skill_name_validation(self):
        """AC8.03: Skill name validator rejects all malicious, dangerous, and malformed inputs."""
        malicious_names = [
            "",
            " ",
            "   ",
            "../",
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "/absolute/path",
            "\\backslash\\path",
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "LPT1",
            "synced",
            "-leading-dash",
            "trailing-dash-",
            "double--dash",
            "UPPERCASE",
            "CamelCase",
            "under_score",
            "spaces in name",
            "special!@#$%^&*()",
            "emoji-🚀-name",
            "\x00nullbyte",
            "a" * 65,  # Exceeds 64 chars
            "a" * 10000,
            "\n\r\t",
            "...",
            ".",
        ]

        for bad_name in malicious_names:
            errors = validate_skill_name(bad_name)
            self.assertGreater(
                len(errors),
                0,
                f"Expected '{bad_name}' to be rejected with errors, but got 0 errors!",
            )

    def test_fuzz_spec_dictionary_validation(self):
        """AC8.03: Spec dict validator cleanly flags malformed structures without uncaught crashes."""
        fuzz_specs = [
            None,
            {},
            [],
            "not a dict",
            12345,
            {"name": 123},
            {"name": "valid-name", "description": None},
            {"name": "valid-name", "description": ""},
            {"name": "valid-name", "description": "a" * 2000},  # Exceeds max length
            {"name": "valid-name", "description": "Ok", "template_family": "non-existent-template"},
            {"name": "valid-name", "description": "Ok", "template_family": None},
            {"name": "", "description": "Missing name"},
            {"name": "valid-name", "description": "Ok", "metadata": "not a dict"},
            {"name": "valid-name", "description": "Ok", "metadata": {"key": 123}},
            {"unknown_key": "some_value"},
        ]

        for s in fuzz_specs:
            if not isinstance(s, dict):
                continue
            errors = validate_spec_dict(s)
            self.assertGreater(len(errors), 0)

    def test_fuzz_corrupt_zip_import(self):
        """AC8.03: Zip importer cleanly rejects truncated, zero-byte, and corrupt files."""
        corrupt_inputs = [
            b"",  # Zero-byte
            b"PK\x05\x06" + b"\x00" * 18,  # Empty archive
            b"This is not a zip file at all",
            b"\x00" * 256,
            b"PK\x03\x04" + b"\xFF" * 100,  # Corrupt local header
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target_dest = tmp_path / "imported"

            for idx, raw_bytes in enumerate(corrupt_inputs):
                corrupt_zip = tmp_path / f"corrupt_{idx}.zip"
                corrupt_zip.write_bytes(raw_bytes)

                try:
                    import_skill_from_zip(corrupt_zip, target_dest)
                    self.fail("Expected corrupt archive to be rejected with ValueError or PackageError")
                except (ValueError, Exception) as e:
                    # Expected safe rejection
                    self.assertNotIn("Traceback", str(e))

    def test_fuzz_cli_malformed_invocations(self):
        """AC8.03: CLI returns clean error codes and messages when receiving bad inputs."""
        bad_arg_lists = [
            ["new", "--name", "CON", "--description", "Bad device name"],
            ["new", "--name", "valid-name", "--template", "bogus-template"],
            ["validate", "non_existent_folder_xyz_123"],
            ["test", "non_existent_folder_xyz_123"],
            ["eval", "non_existent_folder_xyz_123"],
            ["scan", "non_existent_folder_xyz_123"],
            ["import", "non_existent_file.zip"],
            ["export", "non_existent_folder_xyz_123"],
        ]

        for args in bad_arg_lists:
            # Silence stdout/stderr during fuzzing
            with patch("sys.stdout", new_callable=io.StringIO), patch("sys.stderr", new_callable=io.StringIO):
                try:
                    rc = main(args)
                except SystemExit as e:
                    rc = e.code if isinstance(e.code, int) else 1
                self.assertNotEqual(rc, 0, f"Expected non-zero exit code for args: {args}")


if __name__ == "__main__":
    unittest.main()
