"""Automated test suite for security-config-scanner."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
import sys

# Ensure scripts dir is importable
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from main import Finding, main, mask_secret, scan_directory


class SecurityScannerTests(unittest.TestCase):
    def test_clean_directory_has_zero_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hello.py").write_text("print('hello world')\n", encoding="utf-8")
            findings = scan_directory(d)
            self.assertEqual(len(findings), 0)

    def test_detects_credentials_and_masks_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            # Create files with synthetic test tokens constructed dynamically
            fake_aws = "AKIA" + "IOSFODNN7EXAMPLE"
            fake_rsa = "-----" + "BEGIN RSA PRIVATE KEY-----" + "\nMIIE...\n" + "-----END RSA PRIVATE KEY-----"
            (d / "aws.env").write_text(f"AWS_ACCESS_KEY_ID={fake_aws}\n", encoding="utf-8")
            (d / "github.txt").write_text("token = 'ghp_' + '123456789012345678901234567890123456'\n", encoding="utf-8")
            (d / "id_rsa").write_text(f"{fake_rsa}\n", encoding="utf-8")

            findings = scan_directory(d)
            rule_ids = {f.rule_id for f in findings}
            self.assertIn("SEC-01", rule_ids)
            self.assertIn("SEC-04", rule_ids)

            # Check masking
            for f in findings:
                if f.rule_id == "SEC-01":
                    self.assertNotIn(fake_aws, f.snippet)
                    self.assertIn("...", f.snippet)

    def test_detects_insecure_configurations(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "server.py").write_text("DEBUG = True\napp.config['CORS'] = '*'\n", encoding="utf-8")
            findings = scan_directory(d)
            rule_ids = {f.rule_id for f in findings}
            self.assertIn("CFG-02", rule_ids)

    def test_severity_filtering(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            fake_aws = "AKIA" + "IOSFODNN7EXAMPLE"
            (d / "mixed.txt").write_text(
                "DEBUG = True\n"  # MEDIUM
                f"AWS_KEY={fake_aws}\n",  # CRITICAL
                encoding="utf-8"
            )
            # Filter only CRITICAL
            crit_findings = scan_directory(d, min_severity="CRITICAL")
            self.assertEqual(len(crit_findings), 1)
            self.assertEqual(crit_findings[0].severity, "CRITICAL")

    def test_cli_json_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            fake_aws = "AKIA" + "IOSFODNN7EXAMPLE"
            (d / "bad.env").write_text(f"AWS_ACCESS_KEY_ID={fake_aws}\n", encoding="utf-8")

            # Run CLI with --json and --fail-on-findings
            from unittest.mock import patch
            with patch("sys.stdout", new_callable=io.StringIO) as fake_out:
                rc = main([str(d), "--json", "--fail-on-findings"])
                self.assertEqual(rc, 1)
                data = json.loads(fake_out.getvalue())
                self.assertEqual(data["status"], "success")
                self.assertGreater(data["total_findings"], 0)

    def test_missing_directory_returns_error_code(self):
        rc = main(["/nonexistent/directory/path/that/does/not/exist"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
