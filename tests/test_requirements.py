"""Unit tests for Natural-Language Requirements Engine (Phase 16, Workstream 16B)."""
from __future__ import annotations

import unittest

from skillfactory.ai.requirements import (
    AssumptionRegister,
    StructuredRequirementSpec,
    parse_natural_language_requirement,
)


class TestRequirementsEngine(unittest.TestCase):
    """Validates natural language requirements parsing and assumption registration."""

    def test_excel_diff_requirement(self):
        req = "Create a skill that compares two Excel files and highlights differences."
        spec = parse_natural_language_requirement(req, preferred_name="excel-comparison")

        self.assertEqual(spec.skill_name, "excel-comparison")
        self.assertEqual(spec.domain, "Personal")
        self.assertGreaterEqual(len(spec.inputs), 2)
        self.assertGreaterEqual(len(spec.outputs), 1)
        self.assertGreaterEqual(len(spec.validation_rules), 2)
        self.assertGreaterEqual(len(spec.acceptance_criteria), 2)

        # Verify Assumption Register contains explicit, non-empty assumptions
        self.assertGreaterEqual(len(spec.assumption_register.items), 2)
        categories = [a.category for a in spec.assumption_register.items]
        self.assertIn("Data Format", categories)

        md = spec.to_markdown()
        self.assertIn("# Specification: excel-comparison", md)
        self.assertIn("Assumption Register", md)

    def test_attendance_validator_requirement(self):
        req = "Create a skill that validates employee attendance data."
        spec = parse_natural_language_requirement(req)

        self.assertIn("attendance", spec.skill_name)
        self.assertEqual(spec.domain, "Professional")
        self.assertGreaterEqual(len(spec.inputs), 1)
        self.assertGreaterEqual(len(spec.acceptance_criteria), 2)

        categories = [a.category for a in spec.assumption_register.items]
        self.assertIn("Date Format", categories)

    def test_raid_log_requirement(self):
        req = "Create a skill that reviews project RAID logs."
        spec = parse_natural_language_requirement(req, preferred_name="raid-reviewer")

        self.assertEqual(spec.skill_name, "raid-reviewer")
        self.assertEqual(spec.domain, "Professional")
        self.assertEqual(spec.category, "Project Management")
        self.assertGreaterEqual(len(spec.validation_rules), 2)

        categories = [a.category for a in spec.assumption_register.items]
        self.assertIn("Severity Scale", categories)

    def test_invoice_reconciliation_requirement(self):
        req = "Create a skill that checks invoice discrepancies."
        spec = parse_natural_language_requirement(req)

        self.assertIn("invoice", spec.skill_name)
        self.assertEqual(spec.domain, "Professional")
        self.assertGreaterEqual(len(spec.acceptance_criteria), 2)

        categories = [a.category for a in spec.assumption_register.items]
        self.assertIn("Currency", categories)

    def test_general_requirement_parsing(self):
        req = "Extract email addresses and phone numbers from raw markdown documents"
        spec = parse_natural_language_requirement(req)

        self.assertTrue(len(spec.skill_name) > 0)
        self.assertGreaterEqual(len(spec.security_requirements), 2)
        # Check security controls include path traversal and size limits
        controls = [s.control_type for s in spec.security_requirements]
        self.assertIn("Path Traversal Defense", controls)
        self.assertIn("File Size Limiting", controls)

        # Serialization to dict
        data = spec.to_dict()
        self.assertEqual(data["skill_name"], spec.skill_name)
        self.assertIsInstance(data["assumption_register"], list)


if __name__ == "__main__":
    unittest.main()
