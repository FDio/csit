import unittest
from datetime import UTC, datetime

from coverage_dashboard import render_coverage_content


def catalog_payload(*, complete=True):
    filters = {
        "release": "rls2606" if complete else None,
        "dut": "vpp" if complete else None,
        "dut_version": "26.06-release" if complete else None,
        "area": "ip4_tunnels" if complete else None,
        "infra": "2n-zn2-25ge2p1xxv710-avf" if complete else None,
    }
    options = {
        "release": [{"value": "rls2606", "label": "rls2606"}],
        "dut": ([{"value": "vpp", "label": "vpp"}] if complete else []),
        "dut_version": ([{"value": "26.06-release", "label": "26.06-release"}] if complete else []),
        "area": ([{"value": "ip4_tunnels", "label": "IPv4 Tunnels"}] if complete else []),
        "infra": ([{"value": "2n-zn2-25ge2p1xxv710-avf", "label": "2n-zn2-25ge2p1xxv710-avf"}] if complete else []),
    }
    return {
        "dataset": "coverage_catalog",
        "filters": filters,
        "filter_options": options,
        "complete": complete,
    }


def tables_payload():
    record = {
        "suite": "25ge2p1xxv710-avf-ethip4udp-ip4base",
        "accordion_title": "25ge2p1xxv710-avf-ethip4udp-ip4base",
        "test_name": "64B-1c-ethip4udp-ip4base",
        "job": "csit-vpp-coverage-2n-zn2",
        "build": 42,
        "test_id": "tests.vpp.perf.ip4.example.ndrpdr",
        "source_url": (
            "https://logs.fd.io/vex-yul-rot-jenkins-1/"
            "csit-vpp-coverage-2n-zn2/42/tests/vpp/perf/ip4/"
            "example/ndrpdr.info.json.gz"
        ),
        "throughput_ndr": 10.25,
        "throughput_ndr_gbps": 20.5,
        "throughput_pdr": 11.75,
        "throughput_pdr_gbps": 23.5,
        "latency_forward_pdr_10_p50": 12,
        "latency_forward_pdr_10_p90": 18,
        "latency_forward_pdr_10_p99": 25,
    }
    return {
        "dataset": "coverage_tables",
        "records": [record],
        "has_forward_latency": True,
        "has_reverse_latency": False,
    }


class CoverageDashboardTests(unittest.TestCase):
    def test_initial_state_has_only_release_options_and_no_tables(self):
        page = render_coverage_content(catalog_payload(complete=False), None)

        self.assertIn('data-coverage-complete="false"', page)
        self.assertIn('name="release"', page)
        self.assertIn('name="dut" data-coverage-filter disabled', page)
        self.assertNotIn("coverage-accordion", page)
        self.assertNotIn('data-coverage-actions', page)

    def test_complete_state_renders_collapsed_grouped_table_and_link(self):
        page = render_coverage_content(
            catalog_payload(),
            tables_payload(),
            now=datetime(2026, 9, 16, 12, 13, 14, tzinfo=UTC),
        )

        self.assertIn('data-coverage-complete="true"', page)
        self.assertIn('<details class="coverage-accordion">', page)
        self.assertNotIn('<details class="coverage-accordion" open>', page)
        self.assertIn("Throughput", page)
        self.assertIn("Latency Forward [us]", page)
        self.assertNotIn("Latency Reverse [us]", page)
        self.assertIn("10% PDR", page)
        self.assertIn("P50", page)
        self.assertIn("10.25", page)
        self.assertIn("12", page)
        self.assertIn('target="_blank" rel="noopener noreferrer"', page)
        self.assertIn(".info.json.gz", page)
        self.assertIn('data-sortable-table', page)
        self.assertIn('data-export-endpoint="/api/coverage/export"', page)
        self.assertIn('data-default-filename="coverage-2026-09-16 12:13:14"', page)

    def test_missing_cells_remain_empty_and_values_are_escaped(self):
        payload = tables_payload()
        payload["records"][0]["test_name"] = '<unsafe>&"'
        payload["records"][0]["throughput_ndr"] = None
        page = render_coverage_content(catalog_payload(), payload)

        self.assertNotIn('<unsafe>&"', page)
        self.assertIn("&lt;unsafe&gt;&amp;&quot;", page)
        self.assertIn('data-sort-value=""></td>', page)

    def test_json_errors_render_inline(self):
        error = {"error": "data_unavailable", "message": "cache loading"}
        page = render_coverage_content(error, error)

        self.assertIn("Coverage catalog unavailable", page)
        self.assertIn("Coverage tables unavailable", page)
        self.assertIn("cache loading", page)


if __name__ == "__main__":
    unittest.main()
