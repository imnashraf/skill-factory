"""Unit tests for AST safety scanner and credential detector (Phase 5, Task T5.02, AC5.02)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillfactory.scanner import (
    scan_file,
    scan_python_code,
    scan_secrets_in_text,
    scan_skill_directory,
)


class ScannerTests(unittest.TestCase):
    def test_ast_detects_eval_and_exec(self):
        """AC5.02: Flags eval and exec as CRITICAL."""
        code = "def run(x):\n    return eval(x)\n"
        findings = scan_python_code(code)
        self.assertTrue(any(f.rule_id == "AST001" and f.severity == "CRITICAL" for f in findings))

        code_exec = "def execute(cmd):\n    exec(cmd)\n"
        findings_exec = scan_python_code(code_exec)
        self.assertTrue(any(f.rule_id == "AST001" and f.severity == "CRITICAL" for f in findings_exec))

    def test_ast_detects_dynamic_import(self):
        """AC5.02: Flags __import__ as HIGH."""
        code = "mod = __import__('os')\n"
        findings = scan_python_code(code)
        self.assertTrue(any(f.rule_id == "AST002" and f.severity == "HIGH" for f in findings))

    def test_ast_detects_os_system_and_popen(self):
        """AC5.02: Flags os.system and os.popen as CRITICAL."""
        code = "import os\nos.system('whoami')\n"
        findings = scan_python_code(code)
        self.assertTrue(any(f.rule_id == "AST003" and f.severity == "CRITICAL" for f in findings))

        code_popen = "import os\np = os.popen('cat /etc/passwd')\n"
        findings_popen = scan_python_code(code_popen)
        self.assertTrue(any(f.rule_id == "AST003" and f.severity == "CRITICAL" for f in findings_popen))

    def test_ast_detects_dangerous_root_wipe(self):
        """AC5.02: Flags root deletion via os.remove or shutil.rmtree as CRITICAL."""
        code_remove = "import os\nos.remove('/')\n"
        findings = scan_python_code(code_remove)
        self.assertTrue(any(f.rule_id == "AST004" and f.severity == "CRITICAL" for f in findings))

        code_rmtree = "import shutil\nshutil.rmtree('/')\n"
        findings_rmtree = scan_python_code(code_rmtree)
        self.assertTrue(any(f.rule_id == "AST005" and f.severity == "CRITICAL" for f in findings_rmtree))

    def test_ast_detects_subprocess_shell_true(self):
        """AC5.02: Flags subprocess calls with shell=True as CRITICAL."""
        code = "import subprocess\nsubprocess.run('echo hello', shell=True)\n"
        findings = scan_python_code(code)
        self.assertTrue(any(f.rule_id == "AST007" and f.severity == "CRITICAL" for f in findings))

    def test_ast_handles_syntax_error_cleanly(self):
        """Flags syntax errors in scripts cleanly without crashing."""
        malformed = "def broken(\n"
        findings = scan_python_code(malformed)
        self.assertTrue(any(f.rule_id == "AST000" for f in findings))

    def test_secret_scanner_detects_credentials(self):
        """Flags AWS keys, GitHub tokens, OpenAI keys, and private keys."""
        # AWS Key
        text_aws = "AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'\n"
        findings_aws = scan_secrets_in_text(text_aws)
        self.assertTrue(any(f.rule_id == "SEC001" for f in findings_aws))

        # GitHub Token
        text_gh = "token = 'ghp_' + 'A' * 36\n"
        # Test literal token:
        literal_gh = "github_token: ghp_123456789012345678901234567890123456\n"
        findings_gh = scan_secrets_in_text(literal_gh)
        self.assertTrue(any(f.rule_id == "SEC002" for f in findings_gh))

        # OpenAI Key
        text_oa = "export OPENAI_API_KEY='sk-proj-abcdefghijklmnopqrstuv12345'\n"
        findings_oa = scan_secrets_in_text(text_oa)
        self.assertTrue(any(f.rule_id == "SEC003" for f in findings_oa))

        # Private Key
        text_pk = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n"
        findings_pk = scan_secrets_in_text(text_pk)
        self.assertTrue(any(f.rule_id == "SEC004" for f in findings_pk))

    def test_clean_python_script_passes_clean(self):
        """Clean code produces 0 findings and is_clean == True."""
        clean_code = (
            "import json\n"
            "from pathlib import Path\n\n"
            "def calculate_total(items):\n"
            "    return sum(item.get('price', 0) for item in items)\n"
        )
        findings = scan_python_code(clean_code)
        self.assertEqual(findings, [])

    def test_scan_skill_directory(self):
        """Scan full directory tree and produce aggregated SafetyReport."""
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "sample-skill"
            skill_dir.mkdir()
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()

            (scripts_dir / "safe.py").write_text("print('Safe execution')\n", encoding="utf-8")
            (scripts_dir / "unsafe.py").write_text("eval('2 + 2')\n", encoding="utf-8")

            report = scan_skill_directory(skill_dir)
            self.assertFalse(report.is_clean)
            self.assertGreaterEqual(report.critical_count, 1)
            self.assertTrue(any(f.rule_id == "AST001" for f in report.findings))


if __name__ == "__main__":
    unittest.main()
