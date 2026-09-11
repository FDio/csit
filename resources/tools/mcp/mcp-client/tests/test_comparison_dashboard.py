import unittest
from datetime import UTC, datetime

from comparison_dashboard import render_comparison_content
from tests.test_app import comparison_catalog_payload, comparison_table_payload


class ComparisonDashboardTests(unittest.TestCase):
    def test_initial_state_has_three_fieldsets_and_no_table(self):
        page = render_comparison_content(comparison_catalog_payload(), None)

        self.assertIn("Reference Value", page)
        self.assertIn("Compared Value", page)
        self.assertIn("Data Manipulation", page)
        self.assertIn("Complete the reference", page)
        self.assertNotIn("data-comparison-table", page)

    def test_complete_state_renders_grouped_filterable_table_and_actions(self):
        catalog = comparison_catalog_payload(complete=True)
        catalog["filters"]["remove_extreme_outliers"] = True
        page = render_comparison_content(
            catalog,
            comparison_table_payload(),
            now=datetime(2026, 9, 17, 12, 34, 56, tzinfo=UTC),
        )

        self.assertIn('data-comparison-table', page)
        self.assertIn("rls2606 / 26.06-release [MPPS]", page)
        self.assertIn("rls2610 / 26.10-release [MPPS]", page)
        self.assertIn("Relative Change [%]", page)
        self.assertIn("64B-1c-ethip4-ip4base", page)
        self.assertIn(">10.00<", page)
        self.assertEqual(page.count("data-table-filter="), 7)
        self.assertEqual(page.count("data-sort-column="), 7)
        self.assertIn('data-comparison-outliers checked', page)
        self.assertIn("Download Table", page)
        self.assertIn("Download Raw Data", page)
        self.assertIn('data-export-view="table"', page)
        self.assertIn('data-export-view="data"', page)
        self.assertIn("comparison-table-2026-09-17 12:34:56", page)
        self.assertIn("comparison-data-2026-09-17 12:34:56", page)

    def test_payload_errors_render_inline(self):
        page = render_comparison_content({
            "error": "data_unavailable",
            "message": "Iterative cache is loading.",
        }, None)
        self.assertIn("Comparison catalog unavailable", page)
        self.assertIn("Iterative cache is loading.", page)


if __name__ == "__main__":
    unittest.main()
