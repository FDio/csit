import unittest

import pandas as pd

from dashboard.services.analysis import (
    compare_hosts_analysis_payload,
    compare_groups_payload,
    filtered_find_regressions_payload,
    filtered_top_failures_payload,
    find_anomalies_payload,
    top_failures_payload,
    trend_summary_payload,
    validate_analysis_dataset,
)
from dashboard.services.analysis_statistics import (
    anomaly_records,
    compare_groups,
    grouped_summary,
    normalized_group_key,
    numeric_summary,
    top_failures,
    trend_window_summary,
)
from dashboard.services.result_metadata import ResultMetadataService


STATUS = {
    "status": "ready",
    "last_success_at": "2026-06-05T09:30:00+00:00",
}


def make_analysis_data():
    return pd.DataFrame(
        {
            "job": [
                "job-a",
                "job-a",
                "job-b",
                "job-b",
                "job-c",
                "job-c",
            ],
            "test_type": ["mrr", "mrr", "mrr", "mrr", "ndrpdr", "ndrpdr"],
            "dut_type": ["vpp", "vpp", "vpp", "vpp", "dpdk", "dpdk"],
            "release": ["rls2606"] * 6,
            "test_id": [
                "test-a",
                "test-a",
                "test-a",
                "test-a",
                "test-b",
                "test-b",
            ],
            "hosts": [
                ["2n-skx", "host-a"],
                ["2n-skx", "host-a"],
                ["3n-alt", "host-b"],
                ["3n-alt", "host-b"],
                "solo-host",
                "solo-host",
            ],
            "build": [1, 2, 3, 4, 5, 6],
            "start_time": [
                "2026-06-01T00:00:00+00:00",
                "2026-06-02T00:00:00+00:00",
                "2026-06-03T00:00:00+00:00",
                "2026-06-04T00:00:00+00:00",
                "2026-06-05T00:00:00+00:00",
                "2026-06-06T00:00:00+00:00",
            ],
            "passed": [True, False, True, True, False, False],
            "result_rate": [100.0, 110.0, 140.0, 150.0, 98.0, 200.0],
            "result_latency_value": [100.0, 110.0, 80.0, 90.0, 130.0, 120.0],
        }
    )


class AnalysisStatisticsTests(unittest.TestCase):
    def test_numeric_summary_includes_percentiles(self):
        data = pd.DataFrame({"result_rate": [10.0, 20.0, 30.0, 40.0]})

        summary = numeric_summary(data, "result_rate")

        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["min"], 10)
        self.assertEqual(summary["max"], 40)
        self.assertEqual(summary["median"], 25)
        self.assertAlmostEqual(summary["mean"], 25.0)
        self.assertAlmostEqual(summary["p10"], 13.0)
        self.assertAlmostEqual(summary["p90"], 37.0)
        self.assertAlmostEqual(summary["std"], 12.909944, places=5)

    def test_grouped_summary_handles_list_and_scalar_hosts(self):
        records = {
            record["group_key"]: record
            for record in grouped_summary(
                make_analysis_data(),
                group_by="hosts",
                result_column="result_rate",
            )
        }

        self.assertEqual(
            normalized_group_key(["host-a", "2n-skx"]),
            "2n-skx,host-a",
        )
        self.assertEqual(set(records), {
            "2n-skx,host-a",
            "3n-alt,host-b",
            "solo-host",
        })
        self.assertEqual(records["2n-skx,host-a"]["row_count"], 2)
        self.assertEqual(records["2n-skx,host-a"]["passed_count"], 1)
        self.assertEqual(records["2n-skx,host-a"]["failed_count"], 1)
        self.assertEqual(records["2n-skx,host-a"]["failure_rate"], 0.5)
        self.assertEqual(records["2n-skx,host-a"]["result"]["mean"], 105)

    def test_compare_groups_reports_best_worst_and_delta(self):
        summary, records = compare_groups(
            make_analysis_data().iloc[:4],
            group_by="hosts",
            result_column="result_rate",
        )

        self.assertEqual(summary["best_group"], "3n-alt,host-b")
        self.assertEqual(summary["worst_group"], "2n-skx,host-a")
        self.assertEqual(summary["best_mean"], 145)
        self.assertEqual(summary["worst_mean"], 105)
        self.assertEqual(summary["absolute_delta"], 40)
        self.assertAlmostEqual(summary["relative_delta_percent"], 38.095238, places=5)
        self.assertEqual(records[0]["group_key"], "3n-alt,host-b")

    def test_trend_window_summary_compares_recent_and_baseline(self):
        summary = trend_window_summary(
            make_analysis_data(),
            result_column="result_rate",
            order_by="build",
            recent_count=3,
            baseline_count=3,
        )

        self.assertEqual(summary["direction"], "up")
        self.assertEqual(summary["baseline"]["mean"], 116.66666666666667)
        self.assertEqual(summary["recent"]["mean"], 149.33333333333334)
        self.assertAlmostEqual(summary["mean_delta"], 32.66666666666667)

    def test_anomaly_records_are_explainable(self):
        records = anomaly_records(
            pd.DataFrame(
                {
                    "build": [1, 2, 3, 4],
                    "test_id": ["test-a"] * 4,
                    "result_rate": [100.0, 102.0, 98.0, 200.0],
                }
            ),
            result_column="result_rate",
            threshold=1.2,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["actual"], 200)
        self.assertEqual(records[0]["direction"], "above")
        self.assertIn("standard deviations", records[0]["explanation"])

    def test_top_failures_groups_by_hosts(self):
        records = top_failures(
            make_analysis_data(),
            group_by="hosts",
            limit=2,
        )

        self.assertEqual(records[0]["group_key"], "solo-host")
        self.assertEqual(records[0]["failed_count"], 2)
        self.assertEqual(records[0]["failure_rate"], 1.0)
        self.assertEqual(len(records), 2)


class AnalysisPayloadTests(unittest.TestCase):
    def test_validate_analysis_dataset_rejects_unsupported_dataset(self):
        payload = validate_analysis_dataset("statistics")

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "dataset")

    def test_compare_hosts_uses_result_metadata_direction(self):
        payload = compare_hosts_analysis_payload(
            dataset="iterative",
            data=make_analysis_data().iloc[:4],
            result_column="result_latency_value",
            result_metadata=ResultMetadataService(),
            status=STATUS,
        )

        self.assertEqual(payload["analysis"], "compare_hosts")
        self.assertEqual(payload["summary"]["preferred_direction"], "lower")
        self.assertEqual(payload["summary"]["best_group"], "3n-alt,host-b")
        self.assertEqual(payload["filters"]["preferred_direction"], "lower")

    def test_analysis_filters_match_common_dimensions(self):
        payload = filtered_top_failures_payload(
            dataset="iterative",
            data=make_analysis_data(),
            status=STATUS,
            group_by="test_id",
            test_type="mrr",
            dut_type="vpp",
            job="job-a",
            release="rls2606",
            hosts="2n-skx",
            build=2,
            limit=10,
        )

        self.assertEqual(payload["analysis"], "top_failures")
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["summary"]["failed_count"], 1)
        self.assertEqual(payload["filters"]["build"], 2)

    def test_compare_groups_payload_has_stable_internal_shape(self):
        payload = compare_groups_payload(
            dataset="iterative",
            data=make_analysis_data().iloc[:4],
            group_by="hosts",
            result_column="result_rate",
            filters={"test_id": "test-a"},
            status=STATUS,
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["analysis"], "compare_groups")
        self.assertEqual(payload["dataset"], "iterative")
        self.assertEqual(payload["freshness"], STATUS["last_success_at"])
        self.assertEqual(payload["data_status"], "ready")
        self.assertEqual(payload["filters"], {"test_id": "test-a"})
        self.assertEqual(payload["result_column"], "result_rate")
        self.assertEqual(payload["group_by"], "hosts")
        self.assertEqual(payload["summary"]["best_group"], "3n-alt,host-b")
        self.assertTrue(payload["records"])
        self.assertIn("Compared result_rate by hosts", payload["explanation"])

    def test_trend_summary_payload_reports_window_metadata(self):
        payload = trend_summary_payload(
            dataset="trending",
            data=make_analysis_data(),
            result_column="result_rate",
            status=STATUS,
            order_by="start_time",
            recent_count=2,
            baseline_count=2,
        )

        self.assertEqual(payload["analysis"], "trend_summary")
        self.assertEqual(payload["filters"]["order_by"], "start_time")
        self.assertEqual(payload["summary"]["recent_count"], 2)
        self.assertIn(payload["summary"]["direction"], {"up", "down", "flat"})

    def test_find_anomalies_payload_limits_records(self):
        payload = find_anomalies_payload(
            dataset="trending",
            data=pd.DataFrame(
                {
                    "build": [1, 2, 3, 4, 5],
                    "test_id": ["test-a"] * 5,
                    "hosts": ["host-a"] * 5,
                    "result_rate": [100.0, 101.0, 99.0, 98.0, 180.0],
                }
            ),
            result_column="result_rate",
            group_by="hosts",
            threshold=1.0,
            limit=1,
            status=STATUS,
        )

        self.assertEqual(payload["analysis"], "find_anomalies")
        self.assertEqual(payload["summary"]["method"], "z_score")
        self.assertEqual(payload["summary"]["anomaly_count"], 1)
        self.assertEqual(payload["records"][0]["group_key"], "host-a")

    def test_find_anomalies_payload_validates_threshold(self):
        payload = find_anomalies_payload(
            dataset="trending",
            data=make_analysis_data(),
            result_column="result_rate",
            threshold="bad",
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "threshold")

    def test_find_regressions_reports_higher_is_better_drops(self):
        data = pd.DataFrame(
            {
                "test_id": ["test-a"] * 4 + ["test-b"] * 4,
                "build": [1, 2, 3, 4, 1, 2, 3, 4],
                "passed": [True] * 8,
                "result_rate": [100.0, 100.0, 80.0, 70.0, 10.0, 10.0, 20.0, 30.0],
            }
        )

        payload = filtered_find_regressions_payload(
            dataset="iterative",
            data=data,
            result_column="result_rate",
            result_metadata=ResultMetadataService(),
            status=STATUS,
            group_by="test_id",
            recent_count=2,
            baseline_count=2,
            threshold_percent=10.0,
            preferred_direction="higher",
            limit=10,
        )

        self.assertEqual(payload["analysis"], "find_regressions")
        self.assertEqual(payload["summary"]["regression_count"], 1)
        self.assertEqual(payload["records"][0]["group_key"], "test-a")
        self.assertEqual(payload["records"][0]["regression_percent"], 25)

    def test_find_regressions_uses_lower_is_better_metadata(self):
        data = pd.DataFrame(
            {
                "test_id": ["test-a"] * 4,
                "build": [1, 2, 3, 4],
                "passed": [True] * 4,
                "result_latency_value": [100.0, 100.0, 120.0, 130.0],
            }
        )

        payload = filtered_find_regressions_payload(
            dataset="iterative",
            data=data,
            result_column="result_latency_value",
            result_metadata=ResultMetadataService(),
            status=STATUS,
            recent_count=2,
            baseline_count=2,
            threshold_percent=10.0,
            limit=10,
        )

        self.assertEqual(payload["summary"]["preferred_direction"], "lower")
        self.assertEqual(payload["records"][0]["regression_percent"], 25)

    def test_find_regressions_validates_counts_threshold_and_columns(self):
        count_payload = filtered_find_regressions_payload(
            dataset="iterative",
            data=make_analysis_data(),
            result_column="result_rate",
            result_metadata=ResultMetadataService(),
            recent_count=0,
        )
        threshold_payload = filtered_find_regressions_payload(
            dataset="iterative",
            data=make_analysis_data(),
            result_column="result_rate",
            result_metadata=ResultMetadataService(),
            threshold_percent=0,
        )
        group_payload = filtered_find_regressions_payload(
            dataset="iterative",
            data=make_analysis_data(),
            result_column="result_rate",
            result_metadata=ResultMetadataService(),
            group_by="missing",
        )

        self.assertEqual(count_payload["error"], "validation_error")
        self.assertEqual(count_payload["details"]["errors"][0]["field"], "recent_count")
        self.assertEqual(threshold_payload["error"], "validation_error")
        self.assertEqual(
            threshold_payload["details"]["errors"][0]["field"],
            "threshold_percent",
        )
        self.assertEqual(group_payload["error"], "validation_error")
        self.assertEqual(group_payload["details"]["errors"][0]["field"], "group_by")

    def test_top_failures_payload_reports_summary(self):
        payload = top_failures_payload(
            dataset="coverage",
            data=make_analysis_data(),
            group_by="test_id",
            limit=10,
            status=STATUS,
        )

        self.assertEqual(payload["analysis"], "top_failures")
        self.assertEqual(payload["group_by"], "test_id")
        self.assertEqual(payload["summary"]["group_count"], 2)
        self.assertEqual(payload["records"][0]["group_key"], "test-b")
        self.assertEqual(payload["records"][0]["failed_count"], 2)

    def test_payloads_return_validation_error_for_missing_result_column(self):
        payload = compare_groups_payload(
            dataset="iterative",
            data=make_analysis_data(),
            group_by="hosts",
            result_column="missing_result",
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(
            payload["details"]["errors"][0]["field"],
            "result_column",
        )

    def test_payloads_return_validation_error_for_missing_group_column(self):
        payload = top_failures_payload(
            dataset="iterative",
            data=make_analysis_data(),
            group_by="missing_group",
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "group_by")

    def test_payloads_return_validation_error_for_non_numeric_result(self):
        data = make_analysis_data().assign(result_rate=["fast"] * 6)

        payload = trend_summary_payload(
            dataset="trending",
            data=data,
            result_column="result_rate",
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(
            payload["details"]["errors"][0]["field"],
            "result_column",
        )

    def test_payloads_return_validation_error_for_insufficient_samples(self):
        payload = trend_summary_payload(
            dataset="trending",
            data=make_analysis_data().iloc[:2],
            result_column="result_rate",
            recent_count=2,
            baseline_count=2,
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(
            payload["details"]["errors"][0]["field"],
            "recent_count",
        )


if __name__ == "__main__":
    unittest.main()
