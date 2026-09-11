import re
import unittest
from datetime import UTC, datetime, timedelta

from dashboard import render_dashboard_page


class DashboardRenderingTests(unittest.TestCase):
    def setUp(self):
        self.datasets = {
            "data_status": "ready",
            "freshness": "2026-08-04T09:30:00+00:00",
        }
        self.mcp_status = {
            "connected": True,
            "url": "http://mcp-server:8000/mcp",
        }
        self.now = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)

    def test_statistics_charts_are_zero_based_tightly_scaled_and_end_on_date(self):
        payload = self._statistics_payload()

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        self.assertEqual(page.count('<svg class="bar-chart"'), 2)
        self.assertIn('class="bar-passed"', page)
        self.assertIn('class="bar-failed"', page)
        self.assertIn('class="bar-duration"', page)
        self.assertIn(">0</text>", page)
        self.assertIn(">15</text>", page)
        self.assertNotIn(">13.2</text>", page)
        self.assertIn(">00:02</text>", page)
        self.assertIn(">2026-08-04</text>", page)
        self.assertNotIn(">Today</text>", page)
        self.assertIn('class="axis-label axis-label-x axis-label-x-end"', page)
        self.assertIn('font-size="10"', page)
        self.assertIn("Passed / Failed Tests", page)
        self.assertIn("Duration", page)

    def test_long_time_period_keeps_visible_gaps_between_run_bars(self):
        payload = self._statistics_payload()
        payload["records"] = [
            {
                **payload["records"][0],
                "build": 1000 + index,
                "start_time": (self.now - timedelta(days=149 - index)).isoformat(),
            }
            for index in range(150)
        ]

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        for bar_class in ("bar-passed", "bar-duration"):
            bars = [
                (float(x), float(width))
                for x, width in re.findall(
                    rf'class="{bar_class}" x="([\d.]+)"[^>]*'
                    r'width="([\d.]+)"',
                    page,
                )
            ]
            self.assertEqual(len(bars), 150)
            for (x, width), (next_x, _) in zip(bars, bars[1:]):
                self.assertGreater(next_x - (x + width), 0.0)

    def test_dense_runs_at_the_same_plot_time_are_separated(self):
        payload = self._statistics_payload()
        payload["records"] = [
            {
                **payload["records"][0],
                "build": 2000 + index,
                "start_time": "2099-01-01T10:00:00+00:00",
            }
            for index in range(150)
        ]

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        self.assertIn("min-width: 1900px", page)
        for bar_class in ("bar-passed", "bar-duration"):
            bars = [
                (float(x), float(width))
                for x, width in re.findall(
                    rf'class="{bar_class}" x="([\d.]+)"[^>]*'
                    r'width="([\d.]+)"',
                    page,
                )
            ]
            self.assertEqual(len(bars), 150)
            for (x, width), (next_x, _) in zip(bars, bars[1:]):
                self.assertGreater(next_x - (x + width), 0.0)

    def test_future_timestamp_is_clamped_and_formatted_in_tooltip(self):
        payload = self._statistics_payload()
        payload["records"][0]["start_time"] = "2099-01-01T10:00:00+00:00"

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        self.assertIn("date: 2099-01-01 10:00", page)
        self.assertIn(">2026-08-04</text>", page)
        self.assertNotIn(">Today</text>", page)

    def test_both_charts_use_the_same_multiline_run_tooltip(self):
        payload = self._statistics_payload()

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        self.assertEqual(page.count('data-tooltip="date: 2026-08-01 10:00'), 2)
        self.assertNotIn("<title>date:", page)
        self.assertEqual(page.count('aria-label="date: 2026-08-01 10:00'), 2)

    def test_both_chart_bars_expose_identical_clickable_run_metadata(self):
        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            self._statistics_payload(),
            now=self.now,
        )

        self.assertEqual(page.count('class="run-bar" tabindex="0" role="button"'), 2)
        self.assertEqual(
            page.count(
                'data-run-job="csit-vpp-perf-mrr-daily-master-2n-skx"'
            ),
            2,
        )
        self.assertEqual(page.count('data-run-build="201"'), 2)
        self.assertEqual(page.count('data-failed-count="2"'), 2)

    def test_statistics_page_contains_accessible_details_and_action_dialogs(self):
        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            self._statistics_payload(),
            now=self.now,
        )

        self.assertEqual(page.count("<dialog "), 3)
        self.assertIn('id="run-details-dialog"', page)
        self.assertIn("Detailed Information", page)
        self.assertIn("Run Statistics", page)
        self.assertIn("List of Failed Tests", page)
        self.assertIn('aria-label="Close detailed information"', page)
        self.assertIn('aria-label="Copy run statistics"', page)
        self.assertIn('aria-label="Copy failed tests"', page)
        self.assertIn('data-failed-status role="status"', page)
        self.assertIn('data-copy-status aria-live="polite"', page)
        self.assertIn('id="download-dialog"', page)
        self.assertIn("Download Statistics", page)
        self.assertIn('value="xlsx" checked', page)
        self.assertIn('value="csv"', page)
        self.assertIn('aria-label="Close download dialog"', page)
        self.assertIn('id="show-url-dialog"', page)
        self.assertIn("Current Page URL", page)
        self.assertIn('aria-label="Copy current page URL"', page)
        self.assertIn(
            '<label for="current-page-url">Share this Statistics view</label>',
            page,
        )

    def test_statistics_actions_use_selected_filters_and_default_filename(self):
        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            self._statistics_payload(),
            now=self.now,
        )

        self.assertIn('class="statistics-actions"', page)
        self.assertLess(page.index("Show URL"), page.index(">Download</button>"))
        self.assertIn(
            'data-default-filename="stats-vpp-mrr-daily-2n-skx"',
            page,
        )
        self.assertIn('data-filter-dut="vpp"', page)
        self.assertIn('data-filter-test-type="mrr"', page)
        self.assertIn('data-filter-cadence="daily"', page)
        self.assertIn('data-filter-testbed="2n-skx"', page)
        self.assertEqual(page.count('data-filter-dut="vpp"'), 2)

    def test_tooltip_omits_unavailable_optional_fields(self):
        payload = self._statistics_payload()
        record = payload["records"][0]
        record["counts_available"] = False
        record.pop("dut_version")
        record.pop("hosts")

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        self.assertNotIn("passed:", page)
        self.assertNotIn("failed:", page)
        self.assertNotIn("vpp-ver:", page)
        self.assertNotIn("hosts:", page)

    def test_selected_filters_and_unavailable_counts_are_rendered(self):
        payload = self._statistics_payload()
        payload["records"][0]["counts_available"] = False

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        self.assertIn('<option value="vpp" selected>vpp</option>', page)
        self.assertIn('<option value="mrr" selected>mrr</option>', page)
        self.assertIn('class="run-bar count-unavailable"', page)
        self.assertNotIn("passed: 10", page)
        self.assertNotIn("failed: 2", page)

    def test_empty_statistics_render_two_empty_states(self):
        payload = self._statistics_payload()
        payload["records"] = []

        page = render_dashboard_page(
            "statistics",
            self.datasets,
            self.mcp_status,
            payload,
            now=self.now,
        )

        self.assertEqual(
            page.count("No runs are available for this selection."),
            2,
        )
        self.assertNotIn('<svg class="bar-chart"', page)
        self.assertIn("data-open-download-dialog", page)
        self.assertIn("data-filter-testbed=\"2n-skx\" disabled", page)

    @staticmethod
    def _statistics_payload():
        return {
            "filters": {
                "dut": "vpp",
                "test_type": "mrr",
                "cadence": "daily",
                "testbed": "2n-skx",
            },
            "filter_options": {
                "dut": ["dpdk", "vpp"],
                "test_type": ["mrr"],
                "cadence": ["daily"],
                "testbed": ["2n-skx"],
            },
            "records": [
                {
                    "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                    "build": 201,
                    "start_time": "2026-08-01T10:00:00+00:00",
                    "duration": 120.0,
                    "dut": "vpp",
                    "dut_version": "24.10-release",
                    "hosts": ["10.0.0.1", "10.0.0.2"],
                    "passed_count": 10,
                    "failed_count": 2,
                    "counts_available": True,
                }
            ],
        }


if __name__ == "__main__":
    unittest.main()
