import tempfile
import unittest
from pathlib import Path

import pandas as pd

from dashboard.services.data_cache import DataUnavailableError
from dashboard.services.discovery import DiscoveryService
from dashboard.settings import AppSettings


def make_settings(data_spec_file, start_report=True, start_coverage=True):
    return AppSettings(
        server_name="csit_mcp",
        server_version="1.0.0",
        server_description="A FastMCP server providing FD.io CSIT data.",
        public_tags=frozenset({"fd.io", "public"}),
        mcp_path="/mcp",
        data_mode="s3",
        refresh_interval_seconds=0,
        cors_allow_origins=("*",),
        data_spec_file=data_spec_file,
        max_time_period=200,
        time_period=15,
        log_format="%(message)s",
        log_date_format="%Y",
        log_level=20,
        start_failures=False,
        start_statistics=False,
        start_trending=False,
        start_report=start_report,
        start_coverage=start_coverage,
        news_title="Failures",
        stats_title="Statistics",
        trend_title="Trending",
        report_title="Report",
        coverage_title="Coverage",
    )


def write_data_spec(directory):
    spec_path = Path(directory) / "data.yaml"
    spec_path.write_text(
        """
- data_type: statistics
  partition: stats_type
  partition_name: sra
  path: s3://example/statistics
  schema: statistics
  columns:
    - job
    - build
    - start_time
    - duration
- data_type: trending
  partition: test_type
  partition_name: mrr
  path: s3://example/trending
  schema: trending_mrr
  columns:
    - job
    - build
    - test_type
    - dut_type
    - dut_version
    - tg_type
    - hosts
    - test_id
    - result_receive_rate_rate_avg
- data_type: trending
  partition: test_type
  partition_name: ndrpdr
  path: s3://example/trending
  schema: trending_ndrpdr
  columns:
    - job
    - build
    - test_type
    - dut_type
    - dut_version
    - tg_type
    - hosts
    - test_id
    - result_pdr_lower_rate_value
- data_type: iterative
  partition: test_type
  partition_name: mrr
  release: rls2606
  path: s3://example/iterative
  schema: iterative_mrr
  columns:
    - job
    - build
    - test_type
    - release
    - hosts
    - test_id
    - result_receive_rate_rate_avg
- data_type: coverage
  partition: test_type
  partition_name: ndrpdr
  release: rls2606
  path: s3://example/coverage
  schema: coverage_ndrpdr
  columns:
    - job
    - build
    - test_type
    - release
    - hosts
    - test_id
    - result_pdr_lower_rate_value
""",
        encoding="utf-8",
    )
    return str(spec_path)


class FakeDataCache:
    def __init__(self, ready=True):
        self.ready = ready
        self.statistics = pd.DataFrame(
            {
                "job": ["job-a"],
                "build": [1],
                "start_time": ["2026-06-05T10:00:00+00:00"],
                "duration": [123.4],
            }
        )
        self.trending = pd.DataFrame(
            {
                "job": ["job-a", "job-b", "job-c"],
                "build": [11, 12, 13],
                "test_type": ["mrr", "mrr", "ndrpdr"],
                "dut_type": ["vpp", "vpp", "dpdk"],
                "hosts": [
                    ["2n-skx", "host-a"],
                    ["2n-skx", "host-a"],
                    ["3n-alt", "host-b"],
                ],
                "test_id": ["test-a", "test-a", "test-b"],
                "result_receive_rate_rate_avg": [100.0, 130.0, None],
            }
        )
        self.iterative = pd.DataFrame(
            {
                "job": ["iter-job"],
                "build": [21],
                "test_type": ["mrr"],
                "release": ["rls2606"],
                "hosts": [["2n-skx", "host-a"]],
                "test_id": ["iter-test-a"],
                "result_receive_rate_rate_avg": [100.0],
            }
        )
        self.coverage = pd.DataFrame()

    def status_snapshot(self):
        status = "ready" if self.ready else "loading"
        return {
            "status": status,
            "ready": self.ready,
            "last_success_at": "2026-06-05T09:30:00+00:00" if self.ready else None,
            "row_counts": {
                "statistics": len(self.statistics) if self.ready else 0,
                "trending": len(self.trending) if self.ready else 0,
                "iterative": len(self.iterative) if self.ready else 0,
                "coverage": len(self.coverage) if self.ready else 0,
            },
            "datasets": {
                "statistics": {
                    "status": "loaded" if self.ready else "empty",
                    "required": True,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": "2026-06-05T09:30:00+00:00" if self.ready else None,
                },
                "trending": {
                    "status": "loaded" if self.ready else "empty",
                    "required": True,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": "2026-06-05T09:30:00+00:00" if self.ready else None,
                },
                "iterative": {
                    "status": "loaded" if self.ready else "empty",
                    "required": False,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": "2026-06-05T09:30:00+00:00" if self.ready else None,
                },
                "coverage": {
                    "status": "empty",
                    "required": False,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": None,
                },
            },
        }

    def get_parquet(self, query="all"):
        if not self.ready:
            raise DataUnavailableError("not ready")
        if query == "statistics":
            return self.statistics
        if query == "trending":
            return self.trending
        if query == "iterative":
            return self.iterative
        if query == "coverage":
            return self.coverage
        return {
            "statistics": self.statistics,
            "trending": self.trending,
            "iterative": self.iterative,
            "coverage": self.coverage,
        }


class DiscoveryServiceTests(unittest.TestCase):
    def make_service(self, ready=True):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        data_spec_file = write_data_spec(temp_dir.name)
        return DiscoveryService(
            data_cache=FakeDataCache(ready=ready),
            settings=make_settings(data_spec_file),
        )

    def test_datasets_payload_includes_status_counts_and_partitions(self):
        payload = self.make_service().datasets_payload()
        datasets = {
            item["name"]: item
            for item in payload["datasets"]
        }

        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue(payload["ready"])
        self.assertEqual(set(datasets), {"statistics", "trending", "iterative", "coverage"})
        self.assertEqual(datasets["trending"]["row_count"], 3)
        self.assertEqual(datasets["trending"]["status"], "loaded")
        self.assertEqual(len(datasets["trending"]["partitions"]), 2)
        self.assertIn(
            "result_receive_rate_rate_avg",
            datasets["trending"]["result_columns"],
        )

    def test_columns_payload_returns_config_only_before_readiness(self):
        payload = self.make_service(ready=False).columns_payload("trending")
        columns = {
            item["name"]: item
            for item in payload["columns"]
        }

        self.assertFalse(payload["ready"])
        self.assertIsNone(payload["row_count"])
        self.assertTrue(columns["hosts"]["configured"])
        self.assertFalse(columns["hosts"]["cached"])
        self.assertIsNone(columns["hosts"]["dtype"])
        self.assertIsNotNone(columns["result_receive_rate_rate_avg"]["metadata"])
        self.assertEqual(
            columns["result_receive_rate_rate_avg"]["metadata"]["unit_column"],
            "result_receive_rate_rate_unit",
        )

    def test_columns_payload_enriches_cached_metadata_when_ready(self):
        payload = self.make_service().columns_payload("trending")
        columns = {
            item["name"]: item
            for item in payload["columns"]
        }

        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(columns["hosts"]["dtype"], "object")
        self.assertTrue(columns["hosts"]["list_valued"])
        self.assertTrue(columns["test_type"]["dimension_column"])
        self.assertTrue(columns["dut_version"]["dimension_column"])
        self.assertTrue(columns["tg_type"]["dimension_column"])
        self.assertTrue(columns["result_receive_rate_rate_avg"]["result_column"])
        self.assertEqual(columns["result_receive_rate_rate_avg"]["null_count"], 1)
        self.assertEqual(
            columns["result_receive_rate_rate_avg"]["metadata"]["preferred_direction"],
            "higher",
        )

    def test_values_payload_returns_scalar_and_list_values(self):
        service = self.make_service()

        test_type_payload = service.values_payload("trending", "test_type", limit=2)
        hosts_payload = service.values_payload("trending", "hosts", limit=10)
        host_values = {
            item["key"]: item
            for item in hosts_payload["values"]
        }

        self.assertEqual(test_type_payload["returned_count"], 2)
        self.assertEqual(test_type_payload["values"][0]["key"], "mrr")
        self.assertEqual(test_type_payload["values"][0]["count"], 2)
        self.assertEqual(host_values["2n-skx,host-a"]["count"], 2)
        self.assertEqual(host_values["2n-skx,host-a"]["value"], ["2n-skx", "host-a"])

    def test_schema_payload_returns_configured_schema_entries(self):
        payload = self.make_service().schema_payload("trending")

        self.assertTrue(payload["configured"])
        self.assertEqual(payload["entry_count"], 2)
        self.assertIn("test_id", payload["configured_columns"])
        self.assertIn("result_pdr_lower_rate_value", payload["result_columns"])
        self.assertIn("result_pdr_lower_rate_value", payload["result_metadata"])
        self.assertEqual(payload["schemas"][0]["partition"], "test_type")
        self.assertIn("result_receive_rate_rate_avg", payload["schemas"][0]["result_columns"])
        self.assertIn(
            "result_receive_rate_rate_avg",
            payload["schemas"][0]["result_metadata"],
        )

    def test_validation_errors_for_unknown_dataset_column_and_limit(self):
        service = self.make_service()

        dataset_payload = service.columns_payload("missing")
        column_payload = service.values_payload("trending", "missing")
        limit_payload = service.values_payload("trending", "test_type", limit=0)

        self.assertEqual(dataset_payload["error"], "validation_error")
        self.assertEqual(dataset_payload["details"]["errors"][0]["field"], "dataset")
        self.assertEqual(column_payload["error"], "validation_error")
        self.assertEqual(column_payload["details"]["errors"][0]["field"], "column")
        self.assertEqual(limit_payload["error"], "validation_error")
        self.assertEqual(limit_payload["details"]["errors"][0]["field"], "limit")

    def test_values_payload_requires_ready_cache(self):
        payload = self.make_service(ready=False).values_payload("trending", "test_type")

        self.assertEqual(payload["error"], "data_unavailable")


if __name__ == "__main__":
    unittest.main()
