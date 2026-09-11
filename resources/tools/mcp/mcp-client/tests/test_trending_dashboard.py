import unittest
from datetime import UTC, datetime

from trending_dashboard import (
    SERIES_COLORS,
    _series_color_map,
    _trend_hit_region,
    render_trending_content,
)


def catalog_payload():
    return {
        "filters": {
            "dut": "vpp",
            "area": "ip4_tunnels",
            "test": "ethip4geneve",
            "infra": "2n-emr-100ge2p1e810cq-avf",
            "testbed": "all",
            "framesize": "all",
            "cores": "all",
            "test_type": "all",
        },
        "filter_options": {
            "dut": ["vpp"],
            "area": ["ip4_tunnels"],
            "test": ["ethip4geneve"],
            "infra": ["2n-emr-100ge2p1e810cq-avf"],
            "testbed": ["2n-emr"],
            "framesize": ["64B", "1518B"],
            "cores": ["1c", "2c"],
            "test_type": ["mrr", "pdr"],
        },
        "option_labels": {"area": {"ip4_tunnels": "IPv4 Tunnels"}},
        "records": [],
    }


def series_payload():
    series = {
        "series_id": "series-pdr",
        "name": (
            "vpp-2n-emr-100ge2p1e810cq-avf-ip4_tunnels-1518B-2c-"
            "ethip4geneve-pdr"
        ),
        "dut": "vpp",
        "area": "ip4_tunnels",
        "area_label": "IPv4 Tunnels",
        "test": "ethip4geneve",
        "infra": "2n-emr-100ge2p1e810cq-avf",
        "testbed": "2n-emr",
        "framesize": "1518B",
        "cores": "2c",
        "test_type": "pdr",
    }
    return {
        "series": [series],
        "unknown_series": [],
        "records": [{
            **series,
            "start_time": "2026-08-07T10:30:00+00:00",
            "job": "csit-vpp-perf-ndrpdr-daily-master-2n-emr",
            "build": 203,
            "dut_version": "26.06-release",
            "hosts": ["10.0.0.1", "10.0.0.2"],
            "throughput_value": 10_000_000.0,
            "throughput_unit": "pps",
            "bandwidth_value": 25_000_000_000.0,
            "bandwidth_unit": "bps",
            "latency_value": 115_500.0,
            "latency_unit": "us",
        }],
    }


def analyzed_series_payload():
    payload = series_payload()
    first = payload["records"][0]
    records = []
    values = (
        ("2026-08-07T10:30:00+00:00", 10_000_000.0, 25_000_000_000.0, 10.0, "normal"),
        ("2026-08-08T10:30:00+00:00", 13_000_000.0, 30_000_000_000.0, 7.0, "progression"),
        ("2026-08-09T10:30:00+00:00", 8_000_000.0, 20_000_000_000.0, 12.0, "regression"),
    )
    for index, (start_time, throughput, bandwidth, latency, classification) in enumerate(values):
        records.append({
            **first,
            "start_time": start_time,
            "build": 203 + index,
            "throughput_value": throughput,
            "bandwidth_value": bandwidth,
            "latency_value": latency,
            "throughput_analysis": {
                "trend": throughput,
                "stdev": 100_000.0,
                "classification": classification,
            },
            "bandwidth_analysis": {
                "trend": bandwidth,
                "stdev": 200_000_000.0,
                "classification": classification,
            },
            "latency_analysis": {
                "trend": latency,
                "stdev": 0.5,
                "classification": classification,
            },
        })
    payload["records"] = records
    payload["trend_analysis"] = {
        "engine": "jumpavg",
        "version": "0.4.2",
        "classified_series_metrics": 3,
        "skipped_series_metrics": 0,
        "errors": [],
    }
    return payload


class TrendingDashboardTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)

    def test_filters_selected_list_and_actions_are_rendered(self):
        page = render_trending_content(
            catalog_payload(),
            series_payload(),
            ["series-pdr"],
            now=self.now,
        )

        for field in (
                "dut", "area", "test", "infra", "testbed", "framesize",
                "cores", "test_type",
            ):
            self.assertIn(f'name="{field}"', page)
        self.assertIn(">IPv4 Tunnels</option>", page)
        self.assertIn('<option value="all" selected>All</option>', page)
        self.assertIn("Add Selected", page)
        self.assertIn("Remove Selected", page)
        self.assertIn("Remove All", page)
        self.assertIn('name="series" value="series-pdr"', page)
        self.assertIn('name="remove" value="series-pdr"', page)
        self.assertIn("ethip4geneve-pdr", page)
        self.assertIn("series-swatch", page)
        self.assertIn('class="dashboard-actions trending-actions"', page)
        self.assertGreater(
            page.index('class="dashboard-actions trending-actions"'),
            page.index('id="trending-latency-chart-heading"'),
        )
        self.assertLess(page.index("Show URL"), page.index(">Download</button>"))
        self.assertIn('data-export-endpoint="/api/trending/export"', page)
        self.assertIn('data-export-params="series=series-pdr"', page)
        self.assertIn(
            'data-default-filename="trending-2026-08-10 12:00:00"',
            page,
        )

    def test_twenty_selected_series_receive_distinct_deterministic_colors(self):
        series = [
            {"series_id": f"series-{index:02d}", "name": f"Test {index:02d}"}
            for index in range(20)
        ]

        colors = _series_color_map(series)
        reversed_colors = _series_color_map(list(reversed(series)))

        self.assertEqual(len(SERIES_COLORS), 20)
        self.assertEqual(len(colors), 20)
        self.assertEqual(len(set(colors.values())), 20)
        self.assertEqual(colors, reversed_colors)

    def test_three_scatter_charts_use_units_si_ticks_and_five_pixel_points(self):
        page = render_trending_content(
            catalog_payload(),
            series_payload(),
            ["series-pdr"],
            now=self.now,
        )

        self.assertEqual(page.count('<svg class="scatter-chart"'), 3)
        self.assertIn("Throughput [pps]", page)
        self.assertIn("Bandwidth [bps]", page)
        self.assertIn("Average Latency at 50% PDR [us]", page)
        self.assertIn(">11.0M</text>", page)
        self.assertIn(">27.5G</text>", page)
        self.assertIn(">127.1k</text>", page)
        self.assertEqual(page.count('r="2.5"'), 3)
        self.assertIn('axis-label-x axis-label-x-end', page)
        self.assertIn(">2026-08-10</text>", page)

    def test_every_metric_point_uses_the_same_complete_hover_text(self):
        page = render_trending_content(
            catalog_payload(),
            series_payload(),
            ["series-pdr"],
            now=self.now,
        )

        self.assertEqual(page.count('data-tooltip="dut: vpp'), 3)
        for line in (
            "infra: 2n-emr-100ge2p1e810cq-avf",
            "test: ethip4geneve",
            "date: 2026-08-07 10:30",
            "throughput [pps]: 10.0M",
            "bandwidth [bps]: 25.0G",
            "latency [us]: 115.5k",
            "vpp-ver: 26.06-release",
            "csit-ref: csit-vpp-perf-ndrpdr-daily-master-2n-emr/203",
            "hosts: 10.0.0.1, 10.0.0.2",
        ):
            self.assertEqual(page.count(line), 6)

    def test_trend_lines_anomaly_rings_and_legends_render_for_each_metric(self):
        payload = analyzed_series_payload()
        page = render_trending_content(
            catalog_payload(), payload, ["series-pdr"], now=self.now,
        )
        color = _series_color_map(payload["series"])["series-pdr"]

        self.assertEqual(page.count('class="trending-trend-line"'), 3)
        self.assertEqual(page.count(f'stroke="{color}"'), 3)
        self.assertEqual(page.count("Trending graph legend"), 3)
        self.assertEqual(page.count(">Samples</span>"), 3)
        self.assertEqual(page.count(">Trend</span>"), 3)
        self.assertEqual(page.count(">Progression</span>"), 3)
        self.assertEqual(page.count(">Regression</span>"), 3)
        self.assertEqual(page.count("trending-progression"), 3)
        self.assertEqual(page.count("trending-regression"), 3)
        self.assertEqual(page.count('class="trending-trend-hit-target'), 9)
        self.assertEqual(page.count('class="trending-trend-target'), 9)
        self.assertEqual(page.count('class="trending-anomaly'), 6)
        self.assertEqual(page.count('tabindex="0"'), 33)
        self.assertEqual(page.count('role="button"'), 33)

    def test_trend_hit_regions_map_to_nearest_chronological_point(self):
        coordinates = [(0.0, 4.0), (10.0, 8.0), (30.0, 2.0)]

        self.assertEqual(
            _trend_hit_region(coordinates, 0),
            [(0.0, 4.0), (5.0, 6.0)],
        )
        self.assertEqual(
            _trend_hit_region(coordinates, 1),
            [(5.0, 6.0), (10.0, 8.0), (20.0, 5.0)],
        )
        self.assertEqual(
            _trend_hit_region(coordinates, 2),
            [(20.0, 5.0), (30.0, 2.0)],
        )

    def test_trending_targets_and_details_dialog_are_accessible(self):
        page = render_trending_content(
            catalog_payload(),
            analyzed_series_payload(),
            ["series-pdr"],
            now=self.now,
        )

        for target_class in (
                "trending-point chart-tooltip-target trending-details-target",
                "trending-trend-target chart-tooltip-target trending-details-target",
                "trending-trend-hit-target chart-tooltip-target trending-details-target",
            ):
            self.assertIn(f'class="{target_class}"', page)
        self.assertIn(
            "trending-anomaly trending-progression chart-tooltip-target "
            "trending-details-target",
            page,
        )
        self.assertEqual(page.count('<dialog id="trending-details-dialog"'), 1)
        self.assertIn("Detailed Information", page)
        self.assertIn('data-trending-details-content', page)
        self.assertIn('data-copy-trending-details', page)
        self.assertIn('aria-label="Copy detailed information"', page)
        self.assertIn('data-trending-dialog-close', page)
        self.assertIn('aria-label="Close detailed information"', page)
        self.assertIn('data-trending-copy-status', page)
        self.assertIn('aria-live="polite"', page)

    def test_trending_download_and_url_dialogs_are_accessible(self):
        page = render_trending_content(
            catalog_payload(),
            series_payload(),
            ["series-pdr"],
            now=self.now,
        )

        self.assertEqual(page.count('<dialog id="trending-download-dialog"'), 1)
        self.assertIn("Download Trending", page)
        self.assertIn('value="xlsx" checked', page)
        self.assertIn('value="csv"', page)
        self.assertIn('aria-label="Close Trending download dialog"', page)
        self.assertEqual(page.count('<dialog id="trending-url-dialog"'), 1)
        self.assertIn("Share this Trending view", page)
        self.assertIn('data-copy-url', page)
        self.assertIn('aria-label="Copy current Trending URL"', page)
        self.assertIn('data-url-mode="current"', page)

    def test_trending_download_is_disabled_without_graph_samples(self):
        payload = series_payload()
        payload["records"] = []

        page = render_trending_content(
            catalog_payload(), payload, ["series-pdr"], now=self.now,
        )

        self.assertIn(
            'data-default-filename="trending-2026-08-10 12:00:00" disabled',
            page,
        )

    def test_trending_detail_text_is_html_escaped(self):
        payload = analyzed_series_payload()
        payload["series"][0]["test"] = 'unsafe <test> & "quoted"'
        for record in payload["records"]:
            record["test"] = 'unsafe <test> & "quoted"'

        page = render_trending_content(
            catalog_payload(), payload, ["series-pdr"], now=self.now,
        )

        self.assertNotIn('test: unsafe <test> & "quoted"', page)
        self.assertIn(
            "test: unsafe &lt;test&gt; &amp; &quot;quoted&quot;",
            page,
        )

    def test_trend_and_anomaly_hovers_have_distinct_complete_details(self):
        page = render_trending_content(
            catalog_payload(),
            analyzed_series_payload(),
            ["series-pdr"],
            now=self.now,
        )

        trend_tooltip = (
            'data-tooltip="dut: vpp\n'
            'infra: 2n-emr-100ge2p1e810cq-avf\n'
            'test: ethip4geneve\n'
            'date: 2026-08-08 10:30\n'
            'trend [pps]: 13.0M\n'
            'stdev [pps]: 100.0k\n'
            'vpp-ver: 26.06-release\n'
            'csit-ref: csit-vpp-perf-ndrpdr-daily-master-2n-emr/204\n'
            'hosts: 10.0.0.1, 10.0.0.2"'
        )
        anomaly_tooltip = (
            'data-tooltip="dut: vpp\n'
            'infra: 2n-emr-100ge2p1e810cq-avf\n'
            'test: ethip4geneve\n'
            'date: 2026-08-09 10:30\n'
            'trend [pps]: 8.0M\n'
            'classification: regression\n'
            'vpp-ver: 26.06-release\n'
            'csit-ref: csit-vpp-perf-ndrpdr-daily-master-2n-emr/205\n'
            'hosts: 10.0.0.1, 10.0.0.2"'
        )

        self.assertIn(trend_tooltip, page)
        self.assertIn(anomaly_tooltip, page)
        self.assertNotIn("classification: regression\nstdev", page)

    def test_partial_analysis_error_keeps_samples_and_renders_warning(self):
        payload = series_payload()
        payload["trend_analysis"] = {
            "engine": "jumpavg",
            "version": "0.4.2",
            "classified_series_metrics": 0,
            "skipped_series_metrics": 1,
            "errors": [{"metric": "throughput", "message": "bad data"}],
        }

        page = render_trending_content(
            catalog_payload(), payload, ["series-pdr"], now=self.now,
        )

        self.assertIn("Trend analysis partially unavailable", page)
        self.assertIn("1 selected series metric(s) could not be classified", page)
        self.assertEqual(page.count('r="2.5"'), 3)
        self.assertNotIn('class="trending-trend-line"', page)

    def test_chart_without_metric_data_is_omitted_without_placeholder(self):
        payload = series_payload()
        payload["records"][0]["latency_value"] = None
        payload["records"][0]["latency_unit"] = None

        page = render_trending_content(
            catalog_payload(),
            payload,
            ["series-pdr"],
            now=self.now,
        )

        self.assertEqual(page.count('<svg class="scatter-chart"'), 2)
        self.assertNotIn("Average Latency at 50% PDR", page)
        self.assertNotIn("No data", page)

    def test_unknown_series_and_mcp_errors_render_inline(self):
        payload = series_payload()
        payload["unknown_series"] = ["old-id"]
        page = render_trending_content(
            catalog_payload(),
            payload,
            ["series-pdr", "old-id"],
            now=self.now,
        )
        error_page = render_trending_content(
            {"error": "data_unavailable", "message": "Cache is loading."},
            None,
            [],
            now=self.now,
        )

        self.assertIn("1 saved selection(s) are no longer available", page)
        self.assertIn("Trending catalog unavailable", error_page)
        self.assertIn("Cache is loading.", error_page)


if __name__ == "__main__":
    unittest.main()
