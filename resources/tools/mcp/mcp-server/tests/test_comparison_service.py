import math
import unittest

import pandas as pd

from dashboard.data.fixture_data import FixtureDataReader
from dashboard.services.comparison import (
    RAW_EXPORT_COLUMNS,
    ComparisonService,
    normalize_dut_version,
)


def status():
    return {"status": "ready", "last_success_at": "2026-09-17T10:00:00+00:00"}


def comparison_data():
    test_id = (
        "tests.vpp.perf.ip4.2n1l-100ge2p1e810cq-avf-ethip4-ip4base-mrr."
        "64b-1c-avf-ethip4-ip4base-mrr"
    )
    rows = []
    for release, version, base, builds in (
        ("rls2606", "26.06-release-x86_64-g3d02ce21e", 10_000_000, range(101, 106)),
        ("rls2610", "26.10-release-aarch64-gabcdef12", 12_000_000, range(201, 206)),
    ):
        for index, build in enumerate(builds):
            value = base + index * 100_000
            if release == "rls2606" and index == 4:
                value = 80_000_000
            rows.append({
                "job": f"csit-vpp-perf-mrr-release-2n-skx",
                "build": build,
                "dut_type": "vpp",
                "dut_version": version,
                "tg_type": "trex",
                "hosts": [f"10.0.{index}.1", f"10.0.{index}.2"],
                "start_time": f"2026-09-{index + 1:02d}T10:00:00+00:00",
                "passed": True,
                "test_id": test_id,
                "test_type": "mrr",
                "release": release,
                "result_receive_rate_rate_avg": value,
                "result_receive_rate_rate_unit": "pps",
            })
    rows.append({**rows[0], "build": 999, "passed": False})

    ndrpdr_id = (
        "tests.vpp.perf.ip4_tunnels.2n1l-100ge2p1e810cq-avf-ethip4gtpuhw-"
        "ip4base-ndrpdr.1518b-2c-avf-ethip4gtpuhw-ip4base-ndrpdr"
    )
    for release, version, build, rate, latency in (
        ("rls2606", "26.06-release", 301, 20_000_000, 8.0),
        ("rls2610", "26.10-release", 401, 22_000_000, 7.0),
    ):
        rows.append({
            "job": "csit-vpp-perf-ndrpdr-release-2n-emr",
            "build": build,
            "dut_type": "vpp",
            "dut_version": version,
            "tg_type": "trex",
            "hosts": ["10.1.0.1", "10.1.0.2"],
            "start_time": "2026-09-10T10:00:00+00:00",
            "passed": True,
            "test_id": ndrpdr_id,
            "test_type": "ndrpdr",
            "release": release,
            "result_pdr_lower_rate_value": rate,
            "result_pdr_lower_rate_unit": "pps",
            "result_latency_forward_pdr_50_avg": latency,
            "result_latency_forward_pdr_50_unit": "us",
        })
    return pd.DataFrame(rows)


class ComparisonServiceTests(unittest.TestCase):
    def setUp(self):
        self.data = comparison_data()
        self.service = ComparisonService()

    def complete_filters(self):
        return {
            "release": "rls2606",
            "dut": "vpp",
            "dut_version": "26.06-release",
            "infra": "2n-skx-100ge2p1e810cq-avf",
            "framesize": "64B",
            "cores": "1c",
            "test_type": "mrr",
            "parameter": "dut_version",
            "value": "rls2610::26.10-release",
        }

    def test_version_normalization(self):
        self.assertEqual(
            normalize_dut_version("26.06-release-x86_64-g3d02ce21e"),
            "26.06-release",
        )
        self.assertEqual(normalize_dut_version("26.10-rc1-oct"), "26.10-rc1-oct")

    def test_catalog_has_empty_initial_cascade_and_cross_release_versions(self):
        initial = self.service.catalog_payload(self.data, status())
        self.assertFalse(initial["complete"])
        self.assertIsNone(initial["filters"]["release"])
        self.assertEqual(
            [item["value"] for item in initial["filter_options"]["release"]],
            ["rls2606", "rls2610"],
        )

        payload = self.service.catalog_payload(self.data, status(), **{
            key: value for key, value in self.complete_filters().items()
            if key not in {"parameter", "value"}
        })
        self.assertIn(
            {"value": "dut_version", "label": "DUT Version"},
            payload["filter_options"]["parameter"],
        )

        complete = self.service.catalog_payload(
            self.data, status(), **self.complete_filters()
        )
        self.assertTrue(complete["complete"])
        self.assertEqual(complete["matching_test_count"], 1)
        self.assertIn(
            {"value": "rls2610::26.10-release", "label": "rls2610 / 26.10-release"},
            complete["filter_options"]["value"],
        )

    def test_summary_uses_passed_samples_and_tukey_outlier_removal(self):
        broad = self.service.table_payload(
            self.data, status(), **self.complete_filters()
        )
        record = broad["records"][0]
        self.assertEqual(record["reference_count"], 5)
        self.assertEqual(record["compared_count"], 5)
        self.assertEqual(record["reference_outliers_removed"], 0)
        self.assertGreater(record["reference_mean"], 20)
        self.assertIsNotNone(record["relative_change_stdev"])

        trimmed = self.service.table_payload(
            self.data,
            status(),
            remove_extreme_outliers=True,
            **self.complete_filters(),
        )
        record = trimmed["records"][0]
        self.assertEqual(record["reference_count"], 4)
        self.assertEqual(record["reference_outliers_removed"], 1)
        self.assertAlmostEqual(record["reference_mean"], 10.15)
        self.assertAlmostEqual(record["compared_mean"], 12.2)
        self.assertAlmostEqual(record["relative_change_mean"], 20.2)

    def test_latency_is_a_meaningful_pseudo_type(self):
        catalog = self.service.catalog_payload(
            self.data,
            status(),
            release="rls2606",
            dut="vpp",
            dut_version="26.06-release",
            infra="2n-emr-100ge2p1e810cq-avf",
            framesize="1518B",
            cores="2c",
            test_type="latency",
            parameter="dut_version",
            value="rls2610::26.10-release",
        )
        self.assertTrue(catalog["complete"])
        table = self.service.table_payload(
            self.data, status(), **catalog["filters"]
        )
        self.assertEqual(table["records"][0]["unit"], "us")
        self.assertEqual(table["records"][0]["reference_mean"], 8.0)
        self.assertEqual(table["records"][0]["relative_change_mean"], -12.5)

    def test_raw_data_includes_failed_rows_and_exact_columns(self):
        payload = self.service.data_payload(
            self.data, status(), **self.complete_filters()
        )
        self.assertEqual(payload["row_count"], 11)
        self.assertIn(False, {record["passed"] for record in payload["records"]})
        self.assertEqual(
            list(payload["records"][0]),
            [*RAW_EXPORT_COLUMNS, "ref_cmp"],
        )
        self.assertEqual(payload["records"][0]["ref_cmp"], "reference")

    def test_pagination_and_invalid_selection(self):
        payload = self.service.table_payload(
            self.data, status(), limit=1, **self.complete_filters()
        )
        self.assertEqual(payload["returned_count"], 1)
        invalid = self.service.table_payload(
            self.data, status(), release="missing", offset=-1
        )
        self.assertEqual(invalid["error"], "validation_error")

    def test_fixture_data_exposes_cross_release_comparison(self):
        fixture = FixtureDataReader("unused").read_all_data()["iterative"]
        catalog = ComparisonService().catalog_payload(
            fixture,
            status(),
            release="rls2606",
            dut="vpp",
            dut_version="26.06-release",
            infra="2n-skx-100ge2p1e810cq-avf",
            framesize="64B",
            cores="1c",
            test_type="mrr",
            parameter="dut_version",
            value="rls2610::26.10-release",
        )
        self.assertTrue(catalog["complete"])
        self.assertEqual(catalog["matching_test_count"], 1)


if __name__ == "__main__":
    unittest.main()
