import unittest

import pandas as pd
from hdrh.histogram import HdrHistogram

from dashboard.services.coverage import CoverageService


def status():
    return {"status": "ready", "last_success_at": "2026-09-16T10:00:00+00:00"}


def encoded_histogram(*values):
    histogram = HdrHistogram(1, 1_000_000, 3)
    for value in values:
        histogram.record_value(value)
    return histogram.encode().decode()


def coverage_data():
    base = {
        "job": "csit-vpp-perf-report-coverage-2606-2n-zn2",
        "test_type": "ndrpdr",
        "dut_type": "vpp",
        "dut_version": "26.06-release",
        "tg_type": "trex",
        "passed": True,
        "release": "rls2606",
        "result_pdr_lower_rate_unit": "pps",
        "test_id": (
            "tests.vpp.perf.ip4_tunnels."
            "2n1l-25ge2p1xxv710-avf-ethip4udp-ip4base-ndrpdr."
            "64b-1c-avf-ethip4udp-ip4base-ndrpdr"
        ),
        "result_ndr_lower_rate_value": 10_000_000.0,
        "result_pdr_lower_rate_value": 12_000_000.0,
        "result_ndr_lower_bandwidth_value": 20_000_000_000.0,
        "result_pdr_lower_bandwidth_value": 24_000_000_000.0,
    }
    histogram = encoded_histogram(10, 20, 30, 40)
    return pd.DataFrame([
        {
            **base,
            "build": 100,
            "result_latency_forward_pdr_50_hdrh": histogram,
            "result_latency_reverse_pdr_90_hdrh": histogram,
        },
        {
            **base,
            "build": 101,
            "test_id": base["test_id"].replace("64b-1c", "1518b-2c"),
            "result_latency_forward_pdr_50_hdrh": "invalid",
        },
        {
            **base,
            "build": 102,
            "passed": False,
            "result_ndr_lower_rate_value": 999_000_000.0,
        },
        {
            **base,
            "job": "csit-dpdk-perf-report-coverage-2606-2n-zn2",
            "build": 103,
            "dut_type": "dpdk",
            "dut_version": "24.11",
            "test_id": (
                "tests.dpdk.perf.l3fwd."
                "2n1l-25ge2p1xxv710-l3fwd-ndrpdr."
                "imix-l3fwd-ndrpdr"
            ),
        },
        {
            **base,
            "build": 104,
            "test_id": "invalid",
        },
    ])


class CoverageServiceTests(unittest.TestCase):
    def setUp(self):
        self.data = coverage_data()
        self.service = CoverageService()

    def test_catalog_is_passed_only_and_cascades_without_defaults(self):
        initial = self.service.catalog_payload(self.data, status())

        self.assertFalse(initial["complete"])
        self.assertEqual(initial["total_row_count"], 3)
        self.assertEqual(
            [item["value"] for item in initial["filter_options"]["release"]],
            ["rls2606"],
        )
        self.assertEqual(initial["filter_options"]["dut"], [])
        self.assertEqual(initial["unclassified_row_count"], 1)

        release = self.service.catalog_payload(
            self.data, status(), release="rls2606",
        )
        self.assertEqual(
            [item["value"] for item in release["filter_options"]["dut"]],
            ["dpdk", "vpp"],
        )
        self.assertIsNone(release["filters"]["dut"])
        self.assertEqual(release["filter_options"]["dut_version"], [])

    def test_catalog_normalizes_stale_downstream_filters(self):
        payload = self.service.catalog_payload(
            self.data,
            status(),
            release="rls2606",
            dut="vpp",
            dut_version="stale",
            area="ip4_tunnels",
            infra="stale",
        )

        self.assertEqual(payload["filters"]["dut"], "vpp")
        self.assertIsNone(payload["filters"]["dut_version"])
        self.assertIsNone(payload["filters"]["area"])
        self.assertEqual(payload["filter_options"]["area"], [])

    def test_tables_parse_dimensions_convert_units_and_decode_histograms(self):
        payload = self.service.tables_payload(
            self.data,
            status(),
            release="rls2606",
            dut="vpp",
            dut_version="26.06-release",
            area="ip4_tunnels",
            infra="2n-zn2-25ge2p1xxv710-avf",
        )

        self.assertEqual(payload["row_count"], 2)
        self.assertTrue(payload["has_forward_latency"])
        self.assertTrue(payload["has_reverse_latency"])
        self.assertEqual(payload["histogram_decode_error_count"], 1)
        record = payload["records"][0]
        self.assertEqual(record["accordion_title"], "25ge2p1xxv710-avf-ethip4udp-ip4base")
        self.assertEqual(record["test_name"], "64B-1c-ethip4udp-ip4base")
        self.assertEqual(record["throughput_ndr"], 10.0)
        self.assertEqual(record["throughput_pdr"], 12.0)
        self.assertEqual(record["throughput_ndr_gbps"], 20.0)
        self.assertEqual(record["throughput_pdr_gbps"], 24.0)
        self.assertEqual(record["latency_forward_pdr_50_p50"], 20)
        self.assertEqual(record["latency_forward_pdr_50_p99"], 40)
        self.assertIn("/tests/vpp/perf/ip4_tunnels/", record["source_url"])
        self.assertTrue(record["source_url"].endswith(".info.json.gz"))

    def test_dpdk_area_driver_fallback_and_missing_cores(self):
        payload = self.service.tables_payload(
            self.data,
            status(),
            release="rls2606",
            dut="dpdk",
            dut_version="24.11",
            area="dpdk",
            infra="2n-zn2-25ge2p1xxv710-dpdk",
        )

        record = payload["records"][0]
        self.assertEqual(record["area_label"], "DPDK")
        self.assertEqual(record["driver"], "dpdk")
        self.assertEqual(record["test_name"], "imix--l3fwd")

    def test_tables_validate_required_filters_and_paginate(self):
        invalid = self.service.tables_payload(
            self.data,
            status(),
            release="rls2606",
            dut="vpp",
            dut_version=None,
            area=None,
            infra=None,
        )
        self.assertEqual(invalid["error"], "validation_error")

        page = self.service.tables_payload(
            self.data,
            status(),
            release="rls2606",
            dut="vpp",
            dut_version="26.06-release",
            area="ip4_tunnels",
            infra="2n-zn2-25ge2p1xxv710-avf",
            limit=1,
        )
        self.assertTrue(page["has_more"])
        self.assertEqual(page["next_offset"], 1)


if __name__ == "__main__":
    unittest.main()
