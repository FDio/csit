from datetime import UTC, datetime, timedelta
import unittest

import pandas as pd

from dashboard.services.query import (
    job_statistics_payload,
    result_tool_payload,
)


class DummyDataCache:
    def status_snapshot(self):
        return {
            "status": "ready",
            "last_success_at": "2026-06-05T09:30:00+00:00",
        }


def make_result_data():
    recent_time = datetime.now(tz=UTC).isoformat()
    return pd.DataFrame(
        {
            "job": ["job-a", "job-a", "job-b"],
            "test_id": ["test-a", "test-a", "test-b"],
            "test_type": ["mrr", "mrr", "ndrpdr"],
            "dut_type": ["vpp", "vpp", "dpdk"],
            "hosts": [
                ["2n-skx", "host-a"],
                ["3n-alt", "host-b"],
                ["2n-skx", "host-a"],
            ],
            "build": [11, 12, 13],
            "passed": [True, True, False],
            "release": ["rls2606", "rls2606", "rls2606"],
            "start_time": [recent_time, recent_time, recent_time],
            "result_receive_rate_rate_avg": [100.0, 130.0, 80.0],
        }
    )


class QueryServiceTests(unittest.TestCase):
    def test_result_tool_filters_text_list_hosts_int_and_bool(self):
        payload = result_tool_payload(
            dataset="iterative",
            data=make_result_data(),
            data_cache=DummyDataCache(),
            text_filters=[
                ("test_type", "mrr"),
                ("dut_type", "vpp"),
                ("hosts", "2n-skx"),
                ("test_id", "test-a"),
            ],
            int_filters=[("build", 11)],
            passed=True,
            limit=10,
            offset=0,
            aggregation="none",
            sort_by=None,
            sort_order="desc",
            columns=None,
        )

        self.assertEqual(payload["dataset"], "iterative")
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["returned_count"], 1)
        self.assertFalse(payload["has_more"])
        self.assertIsNone(payload["next_offset"])
        self.assertEqual(payload["records"][0]["hosts"], ["2n-skx", "host-a"])
        self.assertEqual(payload["filters"]["build"], 11)
        self.assertTrue(payload["filters"]["passed"])

    def test_result_tool_aggregates_by_hosts_and_test_id(self):
        payload = result_tool_payload(
            dataset="iterative",
            data=make_result_data(),
            data_cache=DummyDataCache(),
            text_filters=[
                ("test_type", None),
                ("dut_type", None),
                ("job", None),
                ("release", None),
                ("hosts", None),
                ("test_id", "test-a"),
            ],
            int_filters=[("build", None)],
            passed=None,
            limit=10,
            offset=0,
            aggregation="hosts_by_test_id",
            sort_by="result_receive_rate_rate_avg_max",
            sort_order="desc",
            columns=None,
        )
        records = {
            record["hosts"]: record
            for record in payload["records"]
        }

        self.assertEqual(payload["aggregation"], "hosts_by_test_id")
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(set(records), {"2n-skx,host-a", "3n-alt,host-b"})
        self.assertEqual(records["3n-alt,host-b"]["passed_count"], 1)
        self.assertEqual(
            records["3n-alt,host-b"]["result_receive_rate_rate_avg_max"],
            130.0,
        )

    def test_result_tool_sorts_projects_and_pages(self):
        payload = result_tool_payload(
            dataset="iterative",
            data=make_result_data(),
            data_cache=DummyDataCache(),
            text_filters=[
                ("test_type", None),
                ("dut_type", None),
                ("hosts", None),
                ("test_id", None),
            ],
            int_filters=[("build", None)],
            passed=None,
            limit=1,
            offset=1,
            aggregation="none",
            sort_by="result_receive_rate_rate_avg",
            sort_order="desc",
            columns=["test_id", "hosts", "result_receive_rate_rate_avg"],
        )

        self.assertEqual(payload["offset"], 1)
        self.assertEqual(payload["returned_count"], 1)
        self.assertTrue(payload["has_more"])
        self.assertEqual(payload["next_offset"], 2)
        self.assertEqual(
            payload["columns"],
            ["test_id", "hosts", "result_receive_rate_rate_avg"],
        )
        self.assertEqual(payload["records"][0]["result_receive_rate_rate_avg"], 100.0)

    def test_result_tool_reports_final_page_without_next_offset(self):
        payload = result_tool_payload(
            dataset="iterative",
            data=make_result_data(),
            data_cache=DummyDataCache(),
            text_filters=[
                ("test_type", None),
                ("dut_type", None),
                ("hosts", None),
                ("test_id", None),
            ],
            int_filters=[("build", None)],
            passed=None,
            limit=10,
            offset=0,
            aggregation="none",
            sort_by=None,
            sort_order="desc",
            columns=None,
        )

        self.assertFalse(payload["has_more"])
        self.assertIsNone(payload["next_offset"])

    def test_result_tool_reports_aggregated_page_metadata(self):
        payload = result_tool_payload(
            dataset="iterative",
            data=make_result_data(),
            data_cache=DummyDataCache(),
            text_filters=[
                ("test_type", None),
                ("dut_type", None),
                ("job", None),
                ("release", None),
                ("hosts", None),
                ("test_id", "test-a"),
            ],
            int_filters=[("build", None)],
            passed=None,
            limit=1,
            offset=0,
            aggregation="hosts_by_test_id",
            sort_by="result_receive_rate_rate_avg_max",
            sort_order="desc",
            columns=None,
        )

        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(payload["returned_count"], 1)
        self.assertTrue(payload["has_more"])
        self.assertEqual(payload["next_offset"], 1)

    def test_result_tool_returns_validation_errors(self):
        payload = result_tool_payload(
            dataset="iterative",
            data=make_result_data(),
            data_cache=DummyDataCache(),
            text_filters=[("test_type", None)],
            int_filters=[("build", None)],
            passed="maybe",
            limit=0,
            offset=-1,
            aggregation="invalid",
            sort_by="missing_column",
            sort_order="sideways",
            columns=["missing_column"],
        )
        error_fields = {
            error["field"]
            for error in payload["details"]["errors"]
        }

        self.assertEqual(payload["error"], "validation_error")
        self.assertIn("limit", error_fields)
        self.assertIn("offset", error_fields)
        self.assertIn("passed", error_fields)
        self.assertIn("aggregation", error_fields)
        self.assertIn("sort_order", error_fields)
        self.assertIn("sort_by", error_fields)
        self.assertIn("columns", error_fields)

    def test_result_tool_never_exposes_raw_telemetry(self):
        data = make_result_data().assign(
            telemetry=[["secret-a"], ["secret-b"], ["secret-c"]]
        )
        payload = result_tool_payload(
            dataset="trending",
            data=data,
            data_cache=DummyDataCache(),
            text_filters=[("test_id", "test-a")],
            int_filters=[],
            passed=None,
            limit=10,
            offset=0,
            aggregation="none",
            sort_by=None,
            sort_order="desc",
            columns=None,
        )
        rejected = result_tool_payload(
            dataset="trending",
            data=data,
            data_cache=DummyDataCache(),
            text_filters=[],
            int_filters=[],
            passed=None,
            limit=10,
            offset=0,
            aggregation="none",
            sort_by=None,
            sort_order="desc",
            columns=["test_id", "telemetry"],
        )

        self.assertNotIn("telemetry", payload["columns"])
        self.assertNotIn("telemetry", payload["records"][0])
        self.assertEqual(rejected["error"], "validation_error")
        self.assertIn(
            "telemetry_timeseries",
            rejected["details"]["errors"][0]["message"],
        )

    def test_job_statistics_filters_by_job_days_and_limit(self):
        recent_time = datetime.now(tz=UTC).isoformat()
        old_time = (datetime.now(tz=UTC) - timedelta(days=30)).isoformat()
        statistics = pd.DataFrame(
            {
                "job": ["job-a", "job-a", "job-b"],
                "start_time": [recent_time, old_time, recent_time],
                "duration": [100, 200, 300],
            }
        )

        payload = job_statistics_payload(
            data=statistics,
            trending_data=pd.DataFrame(),
            data_cache=DummyDataCache(),
            days=7,
            job="job-a",
            limit=10,
        )

        self.assertEqual(payload["dataset"], "statistics")
        self.assertEqual(payload["row_count"], 1)
        self.assertFalse(payload["has_more"])
        self.assertIsNone(payload["next_offset"])
        self.assertEqual(payload["records"][0]["duration"], 100)
        self.assertEqual(
            payload["filters"],
            {
                "days": 7,
                "job": "job-a",
                "limit": 10,
                "dut": None,
                "test_type": None,
                "cadence": None,
                "testbed": None,
                "select_defaults": False,
            },
        )

    def test_job_statistics_reports_has_more_without_offset_contract(self):
        recent_time = datetime.now(tz=UTC).isoformat()
        statistics = pd.DataFrame(
            {
                "job": ["job-a", "job-b", "job-c"],
                "start_time": [recent_time, recent_time, recent_time],
                "duration": [100, 200, 300],
            }
        )

        payload = job_statistics_payload(
            data=statistics,
            trending_data=pd.DataFrame(),
            data_cache=DummyDataCache(),
            days=None,
            job=None,
            limit=1,
        )

        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(payload["returned_count"], 1)
        self.assertTrue(payload["has_more"])
        self.assertIsNone(payload["next_offset"])

    def test_job_statistics_returns_selected_dimensions_and_joined_counts(self):
        recent_time = datetime.now(tz=UTC).isoformat()
        job = "csit-vpp-perf-mrr-daily-master-2n-skx"
        statistics = pd.DataFrame(
            {
                "job": [job],
                "build": [101],
                "start_time": [recent_time],
                "duration": [123.0],
            }
        )
        trending = pd.DataFrame(
            {
                "job": [job, job, job],
                "build": [101, 101, 101],
                "passed": [True, True, False],
                "dut_version": ["24.10", "24.10", "24.10"],
                "hosts": [
                    ["10.0.0.1", "10.0.0.2"],
                    ["10.0.0.2", "10.0.0.3"],
                    ["10.0.0.1", "10.0.0.3"],
                ],
            }
        )

        payload = job_statistics_payload(
            data=statistics,
            trending_data=trending,
            data_cache=DummyDataCache(),
            days=None,
            job=None,
            limit=10,
            select_defaults=True,
        )

        self.assertEqual(payload["filters"]["dut"], "vpp")
        self.assertEqual(payload["filters"]["test_type"], "mrr")
        self.assertEqual(payload["filters"]["cadence"], "daily")
        self.assertEqual(payload["filters"]["testbed"], "2n-skx")
        self.assertEqual(payload["filter_options"]["testbed"], ["2n-skx"])
        self.assertEqual(payload["records"][0]["passed_count"], 2)
        self.assertEqual(payload["records"][0]["failed_count"], 1)
        self.assertEqual(payload["records"][0]["dut_version"], "24.10")
        self.assertEqual(
            payload["records"][0]["hosts"],
            ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
        )
        self.assertTrue(payload["records"][0]["counts_available"])


if __name__ == "__main__":
    unittest.main()
