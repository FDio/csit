import unittest

import pandas as pd

from dashboard.data.fixture_data import FixtureDataReader
from dashboard.services.trending import TrendingService


STATUS = {
    "status": "ready",
    "last_success_at": "2026-08-10T08:00:00+00:00",
}


def trending_data():
    common = {
        "dut_type": "vpp",
        "dut_version": "26.06-release",
        "hosts": ["10.0.0.1", "10.0.0.2"],
        "passed": True,
        "tg_type": "trex",
    }
    return pd.DataFrame([
        {
            **common,
            "job": "csit-vpp-perf-mrr-daily-master-2n-emr",
            "build": 101,
            "start_time": "2026-08-01T10:00:00+00:00",
            "test_type": "mrr",
            "test_id": (
                "tests.vpp.perf.ip4_tunnels."
                "2n1l-100ge2p1e810cq-avf-ethip4geneve."
                "64b-1c-avf-ethip4geneve-mrr"
            ),
            "result_receive_rate_rate_avg": 10_000_000.0,
            "result_receive_rate_rate_unit": "pps",
            "result_receive_rate_bandwidth_avg": 25_000_000_000.0,
            "result_receive_rate_bandwidth_unit": "bps",
        },
        {
            **common,
            "job": "csit-vpp-perf-mrr-daily-master-2n-emr",
            "build": 102,
            "start_time": "2026-08-02T10:00:00+00:00",
            "test_type": "mrr",
            "test_id": (
                "tests.vpp.perf.ip4_tunnels."
                "2n1l-100ge2p1e810cq-avf-ethip4geneve."
                "64b-1c-avf-ethip4geneve-mrr"
            ),
            "result_receive_rate_rate_avg": 11_000_000.0,
            "result_receive_rate_rate_unit": "pps",
            "result_receive_rate_bandwidth_avg": 27_000_000_000.0,
            "result_receive_rate_bandwidth_unit": "bps",
        },
        {
            **common,
            "job": "csit-vpp-perf-ndrpdr-daily-master-2n-emr",
            "build": 103,
            "start_time": "2026-08-03T10:00:00+00:00",
            "test_type": "ndrpdr",
            "test_id": (
                "tests.vpp.perf.ip4.2n1l-100ge2p1e810cq-ethip4base."
                "1518b-2c-ethip4base-ndrpdr"
            ),
            "result_ndr_lower_rate_value": 20_000_000.0,
            "result_ndr_lower_rate_unit": "pps",
            "result_ndr_lower_bandwidth_value": 30_000_000_000.0,
            "result_ndr_lower_bandwidth_unit": "bps",
            "result_pdr_lower_rate_value": 21_000_000.0,
            "result_pdr_lower_rate_unit": "pps",
            "result_pdr_lower_bandwidth_value": 31_000_000_000.0,
            "result_pdr_lower_bandwidth_unit": "bps",
            "result_latency_forward_pdr_50_avg": 7.5,
            "result_latency_forward_pdr_50_unit": "us",
        },
        {
            **common,
            "job": "csit-vpp-perf-hoststack-daily-master-2n-emr",
            "build": 104,
            "start_time": "2026-08-04T10:00:00+00:00",
            "test_type": "hoststack",
            "test_id": (
                "tests.vpp.perf.hoststack."
                "2n1l-25ge2p1e810xxv-eth-ip4tcphttp."
                "2048b-1c-eth-ip4tcphttp-cps"
            ),
            "result_rate_value": 115_500.0,
            "result_rate_unit": "cps",
            "result_bandwidth_value": 2_500_000_000.0,
            "result_bandwidth_unit": "bps",
            "result_latency_value": 150.0,
            "result_latency_unit": "us",
        },
        {
            **common,
            "dut_type": "dpdk",
            "job": "csit-dpdk-perf-mrr-daily-master-2n-emr",
            "build": 105,
            "start_time": "2026-08-05T10:00:00+00:00",
            "test_type": "mrr",
            "test_id": (
                "tests.dpdk.perf.l2.2n1l-25ge2p1e810xxv-l2fwd."
                "64b-0c-l2fwd-mrr"
            ),
            "result_receive_rate_rate_avg": 9_000_000.0,
            "result_receive_rate_rate_unit": "pps",
        },
        {
            **common,
            "job": "csit-vpp-perf-mrr-daily-master-2n-emr",
            "build": 999,
            "start_time": "2026-08-06T10:00:00+00:00",
            "test_type": "mrr",
            "test_id": "not-a-csit-test-id",
            "result_receive_rate_rate_avg": 1.0,
        },
    ])


class TrendingServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = TrendingService()
        self.data = trending_data()

    def test_catalog_parses_dimensions_and_prettifies_areas(self):
        payload = self.service.catalog_payload(
            self.data,
            STATUS,
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="all",
            select_defaults=True,
        )

        self.assertNotIn("error", payload)
        self.assertEqual(payload["unclassified_row_count"], 1)
        self.assertEqual(payload["option_labels"]["area"]["ip4_tunnels"], "IPv4 Tunnels")
        self.assertEqual(payload["row_count"], 1)
        record = payload["records"][0]
        self.assertEqual(record["framesize"], "64B")
        self.assertEqual(record["cores"], "1c")
        self.assertEqual(record["test_type"], "mrr")
        self.assertEqual(
            record["name"],
            "vpp-2n-emr-100ge2p1e810cq-avf-ip4_tunnels-64B-1c-ethip4geneve",
        )
        self.assertEqual(record["testbed"], "10.0.0.1")

    def test_catalog_uses_dpdk_area_and_default_driver(self):
        payload = self.service.catalog_payload(
            self.data,
            STATUS,
            dut="dpdk",
            select_defaults=True,
        )

        record = payload["records"][0]
        self.assertEqual(record["area"], "dpdk")
        self.assertEqual(record["area_label"], "DPDK")
        self.assertEqual(record["infra"], "2n-emr-25ge2p1e810xxv-dpdk")
        self.assertEqual(record["cores"], "0c")

    def test_ndrpdr_expands_to_distinct_ndr_and_pdr_series(self):
        catalog = self.service.catalog_payload(
            self.data,
            STATUS,
            dut="vpp",
            area="ip4",
            test="ethip4base",
            infra="2n-emr-100ge2p1e810cq-dpdk",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="all",
            select_defaults=True,
        )

        self.assertEqual(catalog["row_count"], 2)
        self.assertEqual(
            {record["test_type"] for record in catalog["records"]},
            {"ndr", "pdr"},
        )
        series_ids = [record["series_id"] for record in catalog["records"]]
        points = self.service.series_payload(
            self.data,
            STATUS,
            series=series_ids,
        )
        by_type = {record["test_type"]: record for record in points["records"]}
        self.assertEqual(by_type["ndr"]["throughput_value"], 20_000_000.0)
        self.assertIsNone(by_type["ndr"]["latency_value"])
        self.assertEqual(by_type["pdr"]["latency_value"], 7.5)
        self.assertEqual(by_type["pdr"]["latency_unit"], "us")
        self.assertEqual(by_type["pdr"]["dut_type"], "vpp")
        self.assertEqual(by_type["pdr"]["tg_type"], "trex")
        self.assertEqual(
            by_type["pdr"]["test_id"],
            self.data.iloc[2]["test_id"],
        )

    def test_catalog_defaults_are_cascading_and_pages_matches(self):
        defaults = self.service.catalog_payload(
            self.data,
            STATUS,
            select_defaults=True,
        )
        first = self.service.catalog_payload(
            self.data,
            STATUS,
            dut="vpp",
            area="ip4",
            test="ethip4base",
            infra="2n-emr-100ge2p1e810cq-dpdk",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="all",
            select_defaults=True,
            limit=1,
        )

        self.assertEqual(defaults["filters"]["dut"], "vpp")
        self.assertEqual(defaults["filters"]["testbed"], "all")
        self.assertEqual(first["returned_count"], 1)
        self.assertEqual(first["next_offset"], 1)
        self.assertTrue(first["has_more"])
        self.assertIn("hoststack", first["filter_options"]["area"])

    def test_catalog_preserves_selected_framesize_when_multiple_are_available(self):
        additional = self.data.iloc[[0]].copy()
        additional.loc[:, "test_id"] = (
            "tests.vpp.perf.ip4_tunnels."
            "2n1l-100ge2p1e810cq-avf-ethip4geneve."
            "1518b-1c-ethip4geneve-mrr"
        )
        data = pd.concat([self.data, additional], ignore_index=True)

        payload = self.service.catalog_payload(
            data,
            STATUS,
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="all",
            framesize="1518B",
            cores="all",
            test_type="all",
            select_defaults=True,
        )

        self.assertNotIn("error", payload)
        self.assertEqual(payload["filter_options"]["framesize"], ["64B", "1518B"])
        self.assertEqual(payload["filters"]["framesize"], "1518B")
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["records"][0]["framesize"], "1518B")

    def test_catalog_uses_first_host_as_testbed(self):
        other_testbed = self.data.iloc[[0]].copy()
        other_testbed.at[other_testbed.index[0], "hosts"] = [
            "10.0.0.9", "10.0.0.8",
        ]
        data = pd.concat([self.data, other_testbed], ignore_index=True)

        catalog = self.service.catalog_payload(
            data,
            STATUS,
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="10.0.0.9",
            framesize="all",
            cores="all",
            test_type="all",
            select_defaults=True,
        )

        self.assertEqual(
            catalog["filter_options"]["testbed"],
            ["10.0.0.1", "10.0.0.9"],
        )
        self.assertEqual(catalog["filters"]["testbed"], "10.0.0.9")
        self.assertEqual(catalog["row_count"], 1)
        self.assertEqual(catalog["records"][0]["testbed"], "10.0.0.9")

    def test_host_changes_do_not_split_logical_series(self):
        other_hosts = self.data.iloc[[0]].copy()
        other_hosts.at[other_hosts.index[0], "hosts"] = [
            "10.0.0.9", "10.0.0.8",
        ]
        other_hosts.loc[:, "build"] = 106
        other_hosts.loc[:, "start_time"] = "2026-08-07T10:00:00+00:00"
        data = pd.concat([self.data, other_hosts], ignore_index=True)

        catalog = self.service.catalog_payload(
            data,
            STATUS,
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="all",
            framesize="64B",
            cores="1c",
            test_type="mrr",
            select_defaults=True,
        )

        self.assertEqual(catalog["row_count"], 1)
        self.assertEqual(
            catalog["filter_options"]["testbed"],
            ["10.0.0.1", "10.0.0.9"],
        )
        series_id = catalog["records"][0]["series_id"]
        series = self.service.series_payload(
            data,
            STATUS,
            series=[series_id],
        )
        self.assertEqual(series["row_count"], 3)
        self.assertEqual(
            {tuple(record["hosts"]) for record in series["records"]},
            {
                ("10.0.0.1", "10.0.0.2"),
                ("10.0.0.9", "10.0.0.8"),
            },
        )

    def test_catalog_counts_rows_without_hosts_as_unclassified(self):
        missing_hosts = self.data.iloc[[0]].copy()
        missing_hosts.at[missing_hosts.index[0], "hosts"] = None
        data = pd.concat([self.data, missing_hosts], ignore_index=True)

        catalog = self.service.catalog_payload(
            data,
            STATUS,
            select_defaults=True,
        )

        self.assertEqual(catalog["unclassified_row_count"], 2)

    def test_series_points_are_chronological_and_report_unknown_ids(self):
        catalog = self.service.catalog_payload(
            self.data,
            STATUS,
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="all",
            select_defaults=True,
        )
        series_id = catalog["records"][0]["series_id"]
        first = self.service.series_payload(
            self.data,
            STATUS,
            series=[series_id, "stale-series"],
            limit=1,
        )

        self.assertEqual(first["unknown_series"], ["stale-series"])
        self.assertEqual(first["records"][0]["build"], 101)
        self.assertTrue(first["has_more"])
        second = self.service.series_payload(
            self.data,
            STATUS,
            series=[series_id],
            offset=first["next_offset"],
            limit=1,
        )
        self.assertEqual(second["records"][0]["build"], 102)
        self.assertFalse(second["has_more"])

    def test_catalog_series_and_analysis_use_only_passed_rows(self):
        failed = self.data.iloc[[0]].copy()
        failed.loc[:, "build"] = 103
        failed.loc[:, "start_time"] = "2026-08-03T10:00:00+00:00"
        failed.loc[:, "passed"] = False
        failed.loc[:, "result_receive_rate_rate_avg"] = 100_000_000.0
        unknown = failed.copy()
        unknown.loc[:, "build"] = 104
        unknown["passed"] = pd.Series([pd.NA], dtype="boolean")
        data = pd.concat([self.data, failed, unknown], ignore_index=True)

        catalog = self.service.catalog_payload(
            data,
            STATUS,
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="all",
            framesize="64B",
            cores="1c",
            test_type="mrr",
            select_defaults=True,
        )
        series_id = catalog["records"][0]["series_id"]
        payload = self.service.series_payload(
            data, STATUS, series=[series_id],
        )

        self.assertEqual(
            [record["build"] for record in payload["records"]],
            [101, 102],
        )
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(
            payload["records"][1]["throughput_analysis"]["trend"],
            11_000_000.0,
        )

    def test_series_analysis_uses_full_history_before_pagination(self):
        catalog = self.service.catalog_payload(
            self.data,
            STATUS,
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="all",
            framesize="64B",
            cores="1c",
            test_type="mrr",
            select_defaults=True,
        )
        series_id = catalog["records"][0]["series_id"]

        first = self.service.series_payload(
            self.data, STATUS, series=[series_id], limit=1,
        )
        second = self.service.series_payload(
            self.data, STATUS, series=[series_id], offset=1, limit=1,
        )

        self.assertEqual(
            first["records"][0]["throughput_analysis"]["classification"],
            "normal",
        )
        self.assertEqual(
            second["records"][0]["throughput_analysis"]["classification"],
            "progression",
        )
        self.assertEqual(first["trend_analysis"]["engine"], "jumpavg")
        self.assertEqual(first["trend_analysis"]["version"], "0.4.2")

    def test_invalid_catalog_filter_returns_validation_error(self):
        payload = self.service.catalog_payload(
            self.data,
            STATUS,
            dut="unknown",
            select_defaults=False,
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "dut")

    def test_fixture_catalog_covers_all_logical_test_types(self):
        fixture = FixtureDataReader("ignored").read_all_data()["trending"]
        catalog = self.service.catalog_payload(fixture, STATUS)
        logical_types = {
            record["test_type"] for record in catalog["records"]
        }
        ids = [record["series_id"] for record in catalog["records"]]
        points = self.service.series_payload(fixture, STATUS, series=ids)
        soak = next(
            record for record in points["records"]
            if record["test_type"] == "soak"
        )

        self.assertEqual(
            logical_types,
            {"hoststack", "mrr", "ndr", "pdr", "soak"},
        )
        self.assertEqual(soak["throughput_unit"], "pps")
        self.assertEqual(soak["bandwidth_unit"], "bps")

    def test_fixture_pdr_contains_trends_and_both_anomaly_classes(self):
        fixture = FixtureDataReader("ignored").read_all_data()["trending"]
        catalog = self.service.catalog_payload(
            fixture,
            STATUS,
            dut="vpp",
            area="ip4",
            test="ethip4base",
            infra="2n-skx-100ge2p1e810cq-dpdk",
            testbed="all",
            framesize="1518B",
            cores="2c",
            test_type="pdr",
            select_defaults=True,
        )
        series_id = catalog["records"][0]["series_id"]
        payload = self.service.series_payload(
            fixture, STATUS, series=[series_id],
        )

        for metric in ("throughput", "bandwidth", "latency"):
            classifications = {
                record[f"{metric}_analysis"]["classification"]
                for record in payload["records"]
            }
            self.assertEqual(
                classifications,
                {"normal", "progression", "regression"},
            )
        by_build = {
            record["build"]: record for record in payload["records"]
        }
        self.assertLess(
            by_build[206]["latency_value"],
            by_build[203]["latency_value"],
        )
        self.assertEqual(
            by_build[206]["latency_analysis"]["classification"],
            "progression",
        )
        self.assertGreater(
            by_build[207]["latency_value"],
            by_build[206]["latency_value"],
        )
        self.assertEqual(
            by_build[207]["latency_analysis"]["classification"],
            "regression",
        )


if __name__ == "__main__":
    unittest.main()
