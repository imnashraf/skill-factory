"""Test that skillfactory runtime uses standard library only (AC1.09, NFR-02)."""
from __future__ import annotations

import ast
import sys
from pathlib import Path
import unittest


class NoThirdPartyImportsTests(unittest.TestCase):
    def test_only_stdlib_imports(self):
        # Python standard library module names (common standard library prefixes)
        stdlib_modules = set(sys.builtin_module_names) | {
            "argparse", "ast", "asyncio", "base64", "collections", "contextlib",
            "copy", "csv", "dataclasses", "datetime", "decimal", "difflib",
            "enum", "errno", "fnmatch", "functools", "glob", "hashlib",
            "importlib", "inspect", "io", "itertools", "json", "logging",
            "math", "os", "pathlib", "platform", "posixpath", "pprint",
            "random", "re", "shlex", "shutil", "socket", "stat", "string",
            "struct", "subprocess", "sys", "tempfile", "time", "traceback",
            "types", "typing", "unittest", "urllib", "uuid", "warnings",
            "weakref", "zipfile", "__future__",
        }

        package_root = Path(__file__).resolve().parent.parent / "skillfactory"
        self.assertTrue(package_root.exists(), "skillfactory package folder must exist")

        disallowed_imports = []

        for py_file in package_root.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top_pkg = alias.name.split(".")[0]
                        if top_pkg != "skillfactory" and top_pkg not in stdlib_modules:
                            disallowed_imports.append((str(py_file), alias.name))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top_pkg = node.module.split(".")[0]
                        if top_pkg != "skillfactory" and top_pkg not in stdlib_modules:
                            disallowed_imports.append((str(py_file), node.module))

        self.assertEqual(
            disallowed_imports,
            [],
            f"Found non-standard library imports in skillfactory: {disallowed_imports}",
        )


if __name__ == "__main__":
    unittest.main()
