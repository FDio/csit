import unittest
from datetime import UTC, datetime

from iterative_dashboard import box_statistics, render_iterative_content
from tests.test_app import iterative_catalog_payload, iterative_series_payload


class IterativeDashboardTests(unittest.TestCase):
    def test_tukey_box_statistics_and_outlier(self):
        summary = box_statistics([8.0, 8.1, 7.9, 8.2, 12.0])

        self.assertEqual(summary["min"], 7.9)
        self.assertEqual(summary["q1"], 8.0)
        self.assertEqual(summary["median"], 8.1)
        self.assertEqual(summary["q3"], 8.2)
        self.assertAlmostEqual(summary["lower_fence"], 7.7)
        self.assertAlmostEqual(summary["upper_fence"], 8.5)
        self.assertEqual(summary["lower_whisker"], 7.9)
        self.assertEqual(summary["upper_whisker"], 8.2)
        self.assertEqual(summary["max"], 12.0)
        self.assertEqual(summary["outliers"], [12.0])

    def test_empty_and_single_sample_statistics(self):
        self.assertIsNone(box_statistics([]))
        summary = box_statistics([5.0])
        self.assertEqual(summary["q1"], 5.0)
        self.assertEqual(summary["median"], 5.0)
        self.assertEqual(summary["q3"], 5.0)
        self.assertEqual(summary["outliers"], [])

    def test_renders_filters_indexed_selection_and_available_charts(self):
        catalog = iterative_catalog_payload()
        series = iterative_series_payload()
        page = render_iterative_content(
            catalog,
            series,
            ["iterative-mrr"],
            now=datetime(2026, 9, 11, tzinfo=UTC),
        )

        for field in (
                "release", "dut", "dut_version", "area", "test", "infra",
                "testbed", "framesize", "cores", "test_type",
            ):
            self.assertIn(f'name="{field}"', page)
        self.assertIn('class="series-index">1</span>', page)
        self.assertIn('class="box-chart"', page)
        self.assertIn('style="min-width: 520px"', page)
        self.assertIn("Throughput", page)
        self.assertIn("Bandwidth", page)
        self.assertNotIn("Average Latency at 50% PDR", page)
        self.assertIn("iterative-outlier", page)
        self.assertIn("Distribution", page)

    def test_samples_and_boxes_are_accessible_and_share_details_dialog(self):
        page = render_iterative_content(
            iterative_catalog_payload(),
            iterative_series_payload(),
            ["iterative-mrr"],
        )

        self.assertIn(
            'class="iterative-box-group iterative-details-target '
            'chart-tooltip-target" tabindex="0" role="button"',
            page,
        )
        self.assertIn("iterative-point", page)
        self.assertIn('tabindex="0" role="button"', page)
        self.assertEqual(page.count('id="iterative-details-dialog"'), 1)
        self.assertIn("Detailed Information", page)
        self.assertIn("data-copy-iterative-details", page)
        self.assertIn("data-iterative-dialog-close", page)
        self.assertIn("upper fence [pps]", page)
        self.assertIn("csit-ref:", page)
        self.assertIn("hosts:", page)

    def test_escapes_series_and_tooltip_values(self):
        payload = iterative_series_payload()
        payload["series"][0]["name"] = '<script>alert("x")</script>'
        payload["records"][0]["job"] = 'job-<unsafe>&"'
        page = render_iterative_content(
            iterative_catalog_payload(),
            payload,
            ["iterative-mrr"],
        )

        self.assertNotIn('<script>alert("x")</script>', page)
        self.assertIn("&lt;script&gt;alert", page)
        self.assertIn("job-&lt;unsafe&gt;&amp;&quot;", page)

    def test_actions_use_selected_series_and_timestamped_default(self):
        page = render_iterative_content(
            iterative_catalog_payload(),
            iterative_series_payload(),
            ["iterative-mrr"],
            now=datetime(2026, 9, 11, 12, 13, 14, tzinfo=UTC),
        )

        self.assertIn('data-export-endpoint="/api/iterative/export"', page)
        self.assertIn('data-export-params="series=iterative-mrr"', page)
        self.assertIn('data-default-filename="iterative-2026-09-11 12:13:14"', page)
        self.assertIn('data-url-dialog-target="#iterative-url-dialog"', page)
        self.assertNotIn("data-open-download-dialog disabled", page)

    def test_json_errors_render_inline_without_charts(self):
        error = {"error": "data_unavailable", "message": "cache loading"}
        page = render_iterative_content(error, error, [])

        self.assertIn("Iterative catalog unavailable", page)
        self.assertIn("Iterative series unavailable", page)
        self.assertIn("cache loading", page)
        self.assertNotIn('class="box-chart"', page)


if __name__ == "__main__":
    unittest.main()
