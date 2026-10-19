"""Unit tests for Domain Taxonomy and Multi-Attribute Catalog Search (Phase 17, Workstreams 17A, 17B)."""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from skillfactory.library import (
    CatalogEntry,
    CatalogIndex,
    get_taxonomy,
    index_directory,
    register_custom_domain,
    reset_taxonomy,
    search_catalog,
)


class TestLibraryAndSearch(unittest.TestCase):
    """Validates 3-tier domain taxonomy and multi-attribute offline search."""

    def setUp(self) -> None:
        reset_taxonomy()

    def tearDown(self) -> None:
        reset_taxonomy()

    def test_default_taxonomy_structure(self) -> None:
        tax = get_taxonomy()
        self.assertIn("Personal", tax)
        self.assertIn("Professional", tax)
        self.assertIn("Developer and AI", tax)

        self.assertIn("Productivity", tax["Personal"])
        self.assertIn("Finance", tax["Professional"])
        self.assertIn("Cybersecurity", tax["Developer and AI"])

    def test_dynamic_domain_registration(self) -> None:
        register_custom_domain("Bioinformatics", ["Genomics", "Proteomics"])
        tax = get_taxonomy()
        self.assertIn("Bioinformatics", tax)
        self.assertEqual(tax["Bioinformatics"], ["Genomics", "Proteomics"])

        # Extending existing domain
        register_custom_domain("Personal", ["Wellness"])
        tax2 = get_taxonomy()
        self.assertIn("Wellness", tax2["Personal"])

    def test_multi_attribute_search_filtering(self) -> None:
        entries = [
            CatalogEntry(
                name="excel-comparison",
                description="Compare two excel sheets",
                path="/tmp/excel",
                domain="Personal",
                category="Productivity",
                compatibility="claude-code,cursor",
                grade="Grade A",
                eval_score=95,
                template_family="python-script",
                tags=["excel", "diff"],
            ),
            CatalogEntry(
                name="invoice-reconciler",
                description="Match invoices",
                path="/tmp/invoice",
                domain="Professional",
                category="Finance",
                compatibility="claude-code",
                grade="Grade A",
                eval_score=92,
                template_family="python-script",
                tags=["invoice", "finance"],
            ),
            CatalogEntry(
                name="docker-auditor",
                description="Audit dockerfiles",
                path="/tmp/docker",
                domain="Developer and AI",
                category="Cybersecurity",
                compatibility="cursor",
                grade="Grade B",
                eval_score=82,
                template_family="workflow",
                tags=["docker", "security"],
            ),
        ]
        index = CatalogIndex(skills=entries, source_dir="/tmp", total_skills=3, updated_at="now")

        # 1. Search by domain
        res_prof = search_catalog(index, domain_filter="Professional")
        self.assertEqual(len(res_prof), 1)
        self.assertEqual(res_prof[0][0].name, "invoice-reconciler")

        # 2. Search by grade
        res_grade_a = search_catalog(index, grade_filter="A")
        self.assertEqual(len(res_grade_a), 2)

        # 3. Search by type / template_family
        res_workflow = search_catalog(index, type_filter="workflow")
        self.assertEqual(len(res_workflow), 1)
        self.assertEqual(res_workflow[0][0].name, "docker-auditor")

        # 4. Search by platform
        res_cursor = search_catalog(index, platform_filter="cursor")
        self.assertEqual(len(res_cursor), 2)

        # 5. Combined query and filters
        res_combo = search_catalog(
            index,
            query="excel",
            domain_filter="Personal",
            grade_filter="A",
        )
        self.assertEqual(len(res_combo), 1)
        self.assertEqual(res_combo[0][0].name, "excel-comparison")

    def test_search_latency_budget(self) -> None:
        """Verify search latency budget remains well under 10ms for 100 entries."""
        entries = [
            CatalogEntry(
                name=f"skill-{idx}",
                description=f"Skill description {idx} for automated processing",
                path=f"/tmp/skill-{idx}",
                domain="Personal" if idx % 2 == 0 else "Developer and AI",
                category="Productivity",
                grade="Grade A",
                template_family="python-script",
                tags=["data", f"tag-{idx}"],
            )
            for idx in range(100)
        ]
        index = CatalogIndex(skills=entries, source_dir="/tmp", total_skills=100, updated_at="now")

        start = time.perf_counter()
        results = search_catalog(index, query="skill-42", domain_filter="Personal")
        duration_ms = (time.perf_counter() - start) * 1000

        self.assertLess(duration_ms, 10.0, f"Search took {duration_ms:.2f}ms, exceeding 10ms budget")
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
