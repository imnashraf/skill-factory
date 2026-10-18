"""Unit tests for template routing heuristic (T2.04, AC2.04)."""
from __future__ import annotations

import unittest
from skillfactory.templates.router import route_template


class RouterTests(unittest.TestCase):
    def test_sample_prompts_classification(self):
        """AC2.04: Test router against 20 realistic sample prompts with >= 90% accuracy."""
        test_cases = [
            # File Transform cases
            ("Convert CSV files to JSON schema records", "file-transform"),
            ("Parse Excel sheets and extract tabular data", "file-transform"),
            ("Transform XML documents into YAML format", "file-transform"),
            ("Clean and compress raw log files", "file-transform"),
            ("Extract text from PDF invoices and output structured JSON", "file-transform"),

            # Checklist / Review cases
            ("Perform code review on GitHub pull requests", "checklist-review"),
            ("Security audit checklist for container configurations", "checklist-review"),
            ("Verify compliance with accessibility standards", "checklist-review"),
            ("Inspection checklist for API endpoint schemas", "checklist-review"),
            ("Quality review checklist for documentation PRs", "checklist-review"),

            # Workflow Runbook cases
            ("Deploy web services to production clusters", "workflow-runbook"),
            ("Step-by-step incident response playbook", "workflow-runbook"),
            ("Release procedure and rollback runbook", "workflow-runbook"),
            ("DevOps server maintenance runbook", "workflow-runbook"),
            ("Disaster recovery and database restore procedures", "workflow-runbook"),

            # Python Script cases
            ("Automate daily web scraping of competitor prices", "python-script"),
            ("CLI tool to calculate statistical metrics", "python-script"),
            ("Fetch data from REST API and store in database", "python-script"),
            ("Python script to benchmark network latency", "python-script"),

            # Instructions-only cases
            ("Prompt guidelines for technical writing and blog post drafting", "instructions-only"),
        ]

        correct = 0
        total = len(test_cases)

        for prompt, expected in test_cases:
            assigned, reason = route_template(prompt)
            if assigned == expected:
                correct += 1
            else:
                print(f"Mismatch: '{prompt}' -> got '{assigned}', expected '{expected}' (reason: {reason})")

        accuracy = correct / total
        self.assertGreaterEqual(
            accuracy,
            0.90,
            f"Router accuracy was {accuracy:.1%}, expected >= 90.0% ({correct}/{total} correct)",
        )

    def test_explicit_requires_scripts_flag(self):
        # When requires_scripts is False, should route to instructions-only
        family, _ = route_template("Some arbitrary task description", requires_scripts=False)
        self.assertEqual(family, "instructions-only")

        # When requires_scripts is True, should route to script-based template
        family2, _ = route_template("Some arbitrary task description", requires_scripts=True)
        self.assertEqual(family2, "python-script")


if __name__ == "__main__":
    unittest.main()
