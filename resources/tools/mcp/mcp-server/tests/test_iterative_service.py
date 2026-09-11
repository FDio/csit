import unittest

import pandas as pd

from dashboard.services.iterative import IterativeService


def status():
    return {"status": "ready", "last_success_at": "2026-09-11T10:00:00+00:00"}


def iterative_data():
    base = {
        "job": "csit-vpp-perf-mrr-release-2n-skx",
        "test_type": "mrr",
        "dut_type": "vpp",
        "dut_version": "26.06-release",
        "tg_type": "trex",
        "passed": True,
        "release": "rls2606",
        "test_id": (
            "tests.vpp.perf.ip4.2n1l-100ge2p1e810cq-avf-ethip4-ip4base-mrr."
            "64b-1c-avf-ethip4-ip4base-mrr"
        ),
        "result_receive_rate_rate_unit": "pps",
        "result_receive_rate_bandwidth_unit": "bps",
    }
    rows = []
    for index, (host, rate) in enumerate((("10.0.0.1", 10.0), ("10.0.0.2", 12.0))):
        rows.append({
            **base,
            "build": 100 + index,
            "hosts": [host, "10.0.0.9"],
            "start_time": f"2026-09-{index + 1:02d}T10:00:00+00:00",
            "result_receive_rate_rate_avg": rate,
            "result_receive_rate_bandwidth_avg": rate * 10,
        })
    rows.append({
        **base,
        "job": "csit-vpp-perf-ndrpdr-release-2n-skx",
        "test_type": "ndrpdr",
        "dut_version": "26.10-release",
        "release": "rls2610",
        "build": 200,
        "hosts": ["10.0.0.3", "10.0.0.9"],
        "start_time": "2026-09-03T10:00:00+00:00",
        "test_id": (
            "tests.vpp.perf.ip4.2n1l-100ge2p1e810cq-avf-ethip4-ip4base-ndrpdr."
            "1518b-2c-avf-ethip4-ip4base-ndrpdr"
        ),
        "result_ndr_lower_rate_value": 20.0,
        "result_ndr_lower_rate_unit": "pps",
        "result_ndr_lower_bandwidth_value": 200.0,
        "result_ndr_lower_bandwidth_unit": "bps",
        "result_pdr_lower_rate_value": 18.0,
        "result_pdr_lower_rate_unit": "pps",
        "result_pdr_lower_bandwidth_value": 180.0,
        "result_pdr_lower_bandwidth_unit": "bps",
        "result_latency_forward_pdr_50_avg": 7.0,
        "result_latency_forward_pdr_50_unit": "us",
    })
    rows.append({
        **base,
        "build": 300,
        "hosts": ["10.0.0.4"],
        "start_time": "2026-09-04T10:00:00+00:00",
        "passed": False,
        "result_receive_rate_rate_avg": 999.0,
        "result_receive_rate_bandwidth_avg": 9990.0,
    })
    rows.append({
        **base,
        "build": 400,
        "hosts": ["10.0.0.5"],
        "start_time": "2026-09-05T10:00:00+00:00",
        "test_id": "unparseable",
        "result_receive_rate_rate_avg": 50.0,
        "result_receive_rate_bandwidth_avg": 500.0,
    })
    return pd.DataFrame(rows)


class IterativeServiceTests(unittest.TestCase):
    def setUp(self):
        self.data = iterative_data()
        self.service = IterativeService()

    def test_catalog_prefers_newest_release_version_and_vpp(self):
        payload = self.service.catalog_payload(
            self.data,
            status(),
            select_defaults=True,
        )

        self.assertEqual(payload["filters"]["release"], "rls2610")
        self.assertEqual(payload["filters"]["dut"], "vpp")
        self.assertEqual(payload["filters"]["dut_version"], "26.10-release")
        self.assertEqual(payload["filters"]["testbed"], "all")
        self.assertEqual(payload["filters"]["framesize"], "all")
        self.assertEqual(payload["filters"]["cores"], "all")
        self.assertEqual(payload["filters"]["test_type"], "all")
        self.assertEqual(payload["unclassified_row_count"], 1)

    def test_catalog_expands_ndrpdr_and_suffixes_names(self):
        payload = self.service.catalog_payload(
            self.data,
            status(),
            release="rls2610",
            dut="vpp",
            dut_version="26.10-release",
            area="ip4",
            test="ethip4-ip4base",
            infra="2n-skx-100ge2p1e810cq-avf",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="all",
        )

        self.assertEqual(payload["row_count"], 2)
        names = {record["name"] for record in payload["records"]}
        self.assertTrue(any(name.endswith("-ndr") for name in names))
        self.assertTrue(any(name.endswith("-pdr") for name in names))

    def test_host_changes_do_not_split_one_series(self):
        payload = self.service.catalog_payload(
            self.data,
            status(),
            release="rls2606",
            dut="vpp",
            dut_version="26.06-release",
            area="ip4",
            test="ethip4-ip4base",
            infra="2n-skx-100ge2p1e810cq-avf",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="mrr",
        )

        self.assertEqual(payload["row_count"], 1)
        series_id = payload["records"][0]["series_id"]
        points = self.service.series_payload(
            self.data,
            status(),
            series=[series_id],
        )
        self.assertEqual(points["row_count"], 2)
        self.assertEqual(
            {record["testbed"] for record in points["records"]},
            {"10.0.0.1", "10.0.0.2"},
        )

    def test_only_passed_rows_with_non_negative_metrics_are_indexed(self):
        payload = self.service.catalog_payload(self.data, status())
        self.assertEqual(payload["total_row_count"], 3)
        self.assertTrue(all(
            record["name"].endswith(("-mrr", "-ndr", "-pdr"))
            for record in payload["records"]
        ))

    def test_series_payload_maps_metrics_and_reports_stale_ids(self):
        catalog = self.service.catalog_payload(
            self.data,
            status(),
            release="rls2610",
            dut="vpp",
            dut_version="26.10-release",
            area="ip4",
            test="ethip4-ip4base",
            infra="2n-skx-100ge2p1e810cq-avf",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="pdr",
        )
        series_id = catalog["records"][0]["series_id"]
        payload = self.service.series_payload(
            self.data,
            status(),
            series=[series_id, "stale"],
        )

        self.assertEqual(payload["unknown_series"], ["stale"])
        self.assertEqual(payload["records"][0]["throughput_value"], 18.0)
        self.assertEqual(payload["records"][0]["bandwidth_value"], 180.0)
        self.assertEqual(payload["records"][0]["latency_value"], 7.0)

    def test_pagination_and_validation(self):
        catalog = self.service.catalog_payload(
            self.data,
            status(),
            limit=1,
        )
        self.assertTrue(catalog["has_more"])
        self.assertEqual(catalog["next_offset"], 1)
        invalid = self.service.series_payload(
            self.data,
            status(),
            series=42,
            offset=-1,
        )
        self.assertEqual(invalid["error"], "validation_error")
        fields = {
            item["field"] for item in invalid["details"]["errors"]
        }
        self.assertEqual(fields, {"series", "offset"})


if __name__ == "__main__":
    unittest.main()
