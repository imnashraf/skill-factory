"""Test that skill generation and validation operate 100% offline (NFR-06)."""
from __future__ import annotations

import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skillfactory.core import generate_skill
from skillfactory.spec import SkillSpec
from skillfactory.validator import validate_skill


class OfflineTests(unittest.TestCase):
    def test_offline_generation_and_validation(self):
        """Ensure no network connections are attempted during creation or validation."""
        def guarded_socket(*args, **kwargs):
            raise RuntimeError("Network call attempted during offline execution!")

        with patch.object(socket, "socket", side_effect=guarded_socket):
            with tempfile.TemporaryDirectory() as tmp:
                spec = SkillSpec(
                    name="offline-skill",
                    description="Guaranteed offline operation test.",
                    template_family="python-script",
                )
                res = generate_skill(spec, Path(tmp))
                self.assertTrue(res.target_path.exists())

                val = validate_skill(res.target_path)
                self.assertTrue(val.is_valid, f"Validation errors: {val.errors}")


if __name__ == "__main__":
    unittest.main()
