"""Unit tests for skillfactory/spec.py (T1.02, AC1.02)."""
from __future__ import annotations

import unittest
from skillfactory.spec import SkillSpec, SpecValidationError, validate_spec_dict


class SpecTests(unittest.TestCase):
    def test_valid_spec(self):
        spec = SkillSpec(
            name="valid-skill",
            description="A valid skill description.",
            template_family="python-script",
            version="0.1.0",
        )
        self.assertEqual(spec.validate(), [])
        spec.validate_or_raise()

    def test_invalid_names(self):
        invalid_names = [
            "",                      # empty
            "MySkill",               # uppercase
            "has_underscore",        # underscores
            "has space",             # spaces
            "-leading-dash",         # leading hyphen
            "trailing-dash-",        # trailing hyphen
            "double--dash",          # consecutive hyphens
            "a" * 65,                # > 64 chars
        ]
        for name in invalid_names:
            spec = SkillSpec(name=name, description="Sample description")
            errors = spec.validate()
            self.assertTrue(len(errors) > 0, f"Expected validation failure for name: {name}")

    def test_windows_reserved_names(self):
        """DEF-02 / EC-03: Catch Windows reserved device names."""
        for name in ["con", "prn", "aux", "nul", "com1", "com9", "lpt1", "lpt9"]:
            spec = SkillSpec(name=name, description="Sample description")
            errors = spec.validate()
            self.assertTrue(any("reserved by Windows" in e for e in errors), f"Failed for {name}: {errors}")

    def test_platform_reserved_names(self):
        """DEF-02: Catch platform reserved names like 'synced'."""
        spec = SkillSpec(name="synced", description="Sample description")
        errors = spec.validate()
        self.assertTrue(any("reserved by target platforms" in e for e in errors))

    def test_description_length(self):
        # Empty description
        spec = SkillSpec(name="test-skill", description="")
        self.assertTrue(len(spec.validate()) > 0)

        # > 1024 characters
        long_desc = "x" * 1025
        spec2 = SkillSpec(name="test-skill", description=long_desc)
        errors = spec2.validate()
        self.assertTrue(any("at most 1024 characters" in e for e in errors))

    def test_json_roundtrip(self):
        spec = SkillSpec(
            name="json-skill",
            description="Testing JSON serialization",
            template_family="instructions-only",
            author="Author Name",
            inputs=["file1", "file2"],
            outputs=["result"],
            steps=["Step 1", "Step 2"],
            metadata={"key": "value"},
        )
        json_str = spec.to_json()
        loaded = SkillSpec.from_json(json_str)
        self.assertEqual(spec.to_dict(), loaded.to_dict())

    def test_validate_spec_dict(self):
        valid_dict = {
            "name": "dict-skill",
            "description": "Valid description",
            "template_family": "python-script",
        }
        self.assertEqual(validate_spec_dict(valid_dict), [])

        invalid_dict = {"name": "BAD NAME"}
        self.assertTrue(len(validate_spec_dict(invalid_dict)) > 0)


if __name__ == "__main__":
    unittest.main()
