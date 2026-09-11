import asyncio
import base64
from datetime import UTC, datetime, timedelta
import inspect
import json
import unittest
import zlib

import pandas as pd
try:
    import pyarrow as pa
except ImportError:
    pa = None

from dashboard.services import serialization
from dashboard.services.telemetry_locator import (
    build_telemetry_locator,
    raw_telemetry_frame,
)
from dashboard.mcp_tools import (
    PRIVATE_RESOURCES,
    PUBLIC_RESOURCES,
    PUBLIC_TOOLS,
    register_mcp_tools,
)
from dashboard.routes import register_routes
from dashboard.services.data_cache import (
    DataCacheService,
    DatasetNotFoundError,
    DataUnavailableError,
)
from dashboard.settings import AppSettings


def log_events(records):
    return [json.loads(record.getMessage()) for record in records]


def make_settings(
        data_mode="s3",
        refresh_interval_seconds=0,
        validation_errors=()
    ):
    return AppSettings(
        server_name="csit_mcp",
        server_version="1.0.0",
        server_description="A FastMCP server providing FD.io CSIT data.",
        public_tags=frozenset({"fd.io", "public"}),
        mcp_path="/mcp",
        data_mode=data_mode,
        refresh_interval_seconds=refresh_interval_seconds,
        cors_allow_origins=("*",),
        data_spec_file="dashboard/data/data.yaml",
        max_time_period=200,
        time_period=15,
        log_format="%(message)s",
        log_date_format="%Y",
        log_level=20,
        start_failures=False,
        start_statistics=False,
        start_trending=False,
        start_report=False,
        start_coverage=False,
        news_title="Failures",
        stats_title="Statistics",
        trend_title="Trending",
        report_title="Report",
        coverage_title="Coverage",
        validation_errors=validation_errors,
    )


class FakeMCP:
    def __init__(self):
        self.resources = []
        self.tools = []
        self.routes = []

    def resource(self, **kwargs):
        def decorator(func):
            self.resources.append((kwargs, func))
            return func

        return decorator

    def tool(self, **kwargs):
        def decorator(func):
            self.tools.append((kwargs, func))
            return func

        return decorator

    def custom_route(self, path, methods):
        def decorator(func):
            self.routes.append((path, methods, func))
            return func

        return decorator


class FakeDataCache:
    def __init__(
            self,
            ready=True,
            refresh_started=True,
            include_trending_test_type=True,
            include_trending_hosts=True
        ):
        self._ready = ready
        self.refresh_started = refresh_started
        recent_time = datetime.now(tz=UTC).isoformat()
        old_time = (datetime.now(tz=UTC) - timedelta(days=30)).isoformat()
        self.statistics = pd.DataFrame(
            {
                "job": ["job-a", "job-b"],
                "build": [1, 2],
                "start_time": [recent_time, old_time],
                "duration": [123, 456],
            }
        )
        self.trending = pd.DataFrame(
            {
                "job": ["job-a", "job-a", "job-b", "job-c"],
                "test_id": ["test-a", "test-a", "test-b", "test-c"],
                "test_type": ["mrr", "mrr", "mrr", "ndrpdr"],
                "dut_type": ["vpp", "vpp", "dpdk", "vpp"],
                "hosts": [
                    ["2n-skx", "host-a"],
                    ["3n-alt", "host-b"],
                    ["2n-skx", "host-a"],
                    ["2n-skx", "host-c"],
                ],
                "build": [11, 12, 13, 14],
                "passed": [True, True, False, True],
                "start_time": [recent_time, recent_time, recent_time, old_time],
                "telemetry": ["encoded-a", "encoded-b", "encoded-c", "encoded-d"],
                "result_receive_rate_rate_avg": [100.0, 160.0, 50.0, 90.0],
            }
        )
        if not include_trending_test_type:
            self.trending = self.trending.drop(columns=["test_type"])
        if not include_trending_hosts:
            self.trending = self.trending.drop(columns=["hosts"])
        self.iterative = pd.DataFrame(
            {
                "job": ["iter-job-a", "iter-job-a", "iter-job-b", "iter-job-b"],
                "test_id": [
                    "iter-test-a",
                    "iter-test-a",
                    "iter-test-b",
                    "iter-test-b",
                ],
                "test_type": ["mrr", "mrr", "ndrpdr", "ndrpdr"],
                "dut_type": ["vpp", "vpp", "dpdk", "dpdk"],
                "hosts": [
                    ["2n-skx", "host-a"],
                    ["3n-alt", "host-b"],
                    ["2n-skx", "host-a"],
                    ["3n-alt", "host-b"],
                ],
                "build": [21, 22, 23, 24],
                "passed": [True, True, False, True],
                "release": ["rls2606", "rls2606", "rls2606", "rls2606"],
                "start_time": [recent_time, recent_time, old_time, old_time],
                "telemetry": ["encoded-a", "encoded-b", None, None],
                "result_receive_rate_rate_avg": [100.0, 130.0, 80.0, 110.0],
            }
        )
        self.coverage = pd.DataFrame(
            {
                "job": ["coverage-job-a", "coverage-job-b", "coverage-job-b"],
                "test_id": [
                    "coverage-test-a",
                    "coverage-test-b",
                    "coverage-test-b",
                ],
                "test_type": ["ndrpdr", "ndrpdr", "ndrpdr"],
                "dut_type": ["vpp", "dpdk", "dpdk"],
                "hosts": [
                    ["2n-skx", "host-a"],
                    ["2n-skx", "host-a"],
                    ["3n-alt", "host-b"],
                ],
                "build": [31, 32, 33],
                "passed": [True, False, True],
                "release": ["rls2606", "rls2606", "rls2606"],
                "start_time": [recent_time, old_time, old_time],
                "result_pdr_lower_rate_value": [10.0, 20.0, 30.0],
            }
        )
        self.telemetry_trending = pd.DataFrame(
            {
                "source_dataset": ["trending", "trending", "trending"],
                "source_row": [0, 1, 2],
                "job": ["job-a", "job-a", "job-b"],
                "build": [11, 12, 13],
                "start_time": [recent_time, recent_time, recent_time],
                "test_type": ["mrr", "mrr", "mrr"],
                "dut_type": ["vpp", "vpp", "dpdk"],
                "dut_version": ["24.10", "24.10", "24.10"],
                "tg_type": ["trex", "trex", "trex"],
                "hosts": [
                    ["2n-skx", "host-a"],
                    ["3n-alt", "host-b"],
                    ["2n-skx", "host-a"],
                ],
                "test_id": ["test-a", "test-a", "test-b"],
                "release": [None, None, None],
                "passed": [True, True, False],
                "metric_name": [
                    "csit_packets_total",
                    "csit_packets_total",
                    "csit_packets_total",
                ],
                "labels": [
                    {"worker": "0"},
                    {"worker": "0"},
                    {"worker": "1"},
                ],
                "label_key": ["worker=0", "worker=0", "worker=1"],
                "value": [100.0, 130.0, 400.0],
                "timestamp": ["1760000000", "1760000060", "1760000120"],
                "type": ["counter", "counter", "counter"],
                "unit": ["packets", "packets", "packets"],
                "help": ["Packets observed"] * 3,
            }
        )
        self.telemetry_iterative = self.telemetry_trending.assign(
            source_dataset="iterative",
            release="rls2606",
        )
        self.telemetry_coverage = pd.DataFrame()

    @property
    def is_serving_ready(self):
        return self._ready

    def status_snapshot(self):
        return {
            "status": "ready" if self._ready else "loading",
            "ready": self._ready,
            "last_attempt_at": None,
            "last_success_at": None,
            "cache_age_seconds": 12.5 if self._ready else None,
            "last_error": None,
            "last_refresh_started_by": "manual" if self._ready else None,
            "load_duration_seconds": None,
            "row_counts": {
                "statistics": len(self.statistics),
                "trending": len(self.trending),
                "iterative": len(self.iterative),
                "coverage": len(self.coverage),
            },
            "telemetry": {
                "statistics": {
                    "available": False,
                    "sample_count": 0,
                    "rows_with_telemetry": 0,
                    "rows_with_errors": 0,
                    "metric_names": [],
                    "metric_name_count": 0,
                },
                "trending": {
                    "available": True,
                    "sample_count": len(self.telemetry_trending),
                    "rows_with_telemetry": 3,
                    "rows_with_errors": 0,
                    "metric_names": ["csit_packets_total"],
                    "metric_name_count": 1,
                },
                "iterative": {
                    "available": True,
                    "sample_count": len(self.telemetry_iterative),
                    "rows_with_telemetry": 2,
                    "rows_with_errors": 0,
                    "metric_names": ["csit_packets_total"],
                    "metric_name_count": 1,
                },
                "coverage": {
                    "available": False,
                    "sample_count": 0,
                    "rows_with_telemetry": 0,
                    "rows_with_errors": 0,
                    "metric_names": [],
                    "metric_name_count": 0,
                },
            },
            "datasets": {
                "statistics": {
                    "status": "loaded" if self._ready else "empty",
                    "required": True,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": None,
                    "telemetry": {
                        "available": False,
                        "sample_count": 0,
                        "rows_with_telemetry": 0,
                        "rows_with_errors": 0,
                        "metric_names": [],
                        "metric_name_count": 0,
                    },
                },
                "trending": {
                    "status": "loaded" if self._ready else "empty",
                    "required": True,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": None,
                    "telemetry": {
                        "available": True,
                        "sample_count": len(self.telemetry_trending),
                        "rows_with_telemetry": 3,
                        "rows_with_errors": 0,
                        "metric_names": ["csit_packets_total"],
                        "metric_name_count": 1,
                    },
                },
                "iterative": {
                    "status": "loaded" if self._ready else "empty",
                    "required": False,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": None,
                    "telemetry": {
                        "available": True,
                        "sample_count": len(self.telemetry_iterative),
                        "rows_with_telemetry": 2,
                        "rows_with_errors": 0,
                        "metric_names": ["csit_packets_total"],
                        "metric_name_count": 1,
                    },
                },
                "coverage": {
                    "status": "loaded" if self._ready else "empty",
                    "required": False,
                    "enabled": True,
                    "configured": True,
                    "normalized_at": None,
                    "telemetry": {
                        "available": False,
                        "sample_count": 0,
                        "rows_with_telemetry": 0,
                        "rows_with_errors": 0,
                        "metric_names": [],
                        "metric_name_count": 0,
                    },
                },
            },
            "configuration": {
                "valid": True,
                "errors": [],
                "values": {
                    "CSIT_DATA_MODE": "s3",
                    "CSIT_TIME_PERIOD": 15,
                    "CSIT_MAX_TIME_PERIOD": 200,
                    "effective_time_period": 15,
                    "CSIT_REFRESH_INTERVAL_SECONDS": 0,
                    "CSIT_CORS_ALLOW_ORIGINS": ["*"],
                    "CSIT_MAX_POOL_SIZE": 30,
                    "CSIT_START_TRENDING": False,
                    "CSIT_START_REPORT": False,
                    "CSIT_START_COVERAGE": False,
                    "CSIT_START_STATISTICS": False,
                    "CSIT_START_FAILURES": False,
                },
            },
            "refresh_history": [
                {
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": None,
                    "started_by": "manual",
                    "status": "ready",
                    "error": None,
                    "row_counts": {
                        "statistics": len(self.statistics),
                        "trending": len(self.trending),
                        "iterative": len(self.iterative),
                        "coverage": len(self.coverage),
                    },
                }
            ] if self._ready else [],
        }

    def start_refresh(self):
        return self.refresh_started

    def get_parquet(self, query="all"):
        if not self._ready:
            raise DataUnavailableError("not ready")
        if query == "statistics":
            return self.statistics
        if query == "trending":
            return self.trending
        if query == "iterative":
            return self.iterative
        if query == "coverage":
            return self.coverage
        if query == "all":
            return {
                "statistics": self.statistics,
                "trending": self.trending,
                "iterative": self.iterative,
                "coverage": self.coverage,
            }
        raise DatasetNotFoundError(f"Unknown parquet dataset: {query}")

    def get_telemetry(self, dataset):
        if not self._ready:
            raise DataUnavailableError("not ready")
        if dataset == "trending":
            return self.telemetry_trending
        if dataset == "iterative":
            return self.telemetry_iterative
        if dataset == "coverage":
            return self.telemetry_coverage
        raise DatasetNotFoundError(f"Unknown telemetry dataset: {dataset}")

    def get_raw_telemetry(self, dataset):
        source = self.get_parquet(dataset).copy(deep=False)
        return raw_telemetry_frame(source)

    def get_telemetry_locator(self, dataset):
        source = self.get_parquet(dataset).copy(deep=False)
        raw = raw_telemetry_frame(source)
        return build_telemetry_locator(source, raw)


class MCPRegistrationTests(unittest.TestCase):
    def test_register_mcp_tools_exposes_same_names(self):
        mcp = FakeMCP()

        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )

        resource_names = {item[0]["name"] for item in mcp.resources}
        tool_names = {item[0]["name"] for item in mcp.tools}

        self.assertEqual(resource_names, {"ServerInfo", "DataParquet"})
        self.assertEqual(tool_names, set(PUBLIC_TOOLS))

    def test_public_tool_signatures_expose_stable_filters(self):
        mcp = FakeMCP()

        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )

        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        self.assertEqual(list(inspect.signature(tools["datasets"]).parameters), [])
        self.assertEqual(
            list(inspect.signature(tools["columns"]).parameters),
            ["dataset"],
        )
        self.assertEqual(
            list(inspect.signature(tools["values"]).parameters),
            ["dataset", "column", "limit"],
        )
        self.assertEqual(
            list(inspect.signature(tools["schema"]).parameters),
            ["dataset"],
        )
        self.assertEqual(
            list(inspect.signature(tools["compare_hosts"]).parameters),
            [
                "dataset",
                "result_column",
                "test_id",
                "test_type",
                "dut_type",
                "job",
                "release",
                "build",
                "passed",
                "preferred_direction",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["trend_summary"]).parameters),
            [
                "dataset",
                "result_column",
                "test_id",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "passed",
                "order_by",
                "recent_count",
                "baseline_count",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["find_regressions"]).parameters),
            [
                "dataset",
                "result_column",
                "group_by",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "passed",
                "order_by",
                "recent_count",
                "baseline_count",
                "threshold_percent",
                "preferred_direction",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["find_anomalies"]).parameters),
            [
                "dataset",
                "result_column",
                "group_by",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "passed",
                "threshold",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["top_failures"]).parameters),
            [
                "dataset",
                "group_by",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "build",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["telemetry_metrics"]).parameters),
            [
                "dataset",
                "metric_name",
                "label_key",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "test_id",
                "build",
                "passed",
                "offset",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["telemetry_metric_values"]).parameters),
            [
                "dataset",
                "metric_name",
                "group_by",
                "label_key",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "test_id",
                "build",
                "passed",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["telemetry_trend_summary"]).parameters),
            [
                "dataset",
                "metric_name",
                "group_by",
                "label_key",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "test_id",
                "passed",
                "order_by",
                "recent_count",
                "baseline_count",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["telemetry_anomalies"]).parameters),
            [
                "dataset",
                "metric_name",
                "group_by",
                "label_key",
                "test_type",
                "dut_type",
                "job",
                "release",
                "hosts",
                "test_id",
                "passed",
                "threshold",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["telemetry_catalog"]).parameters),
            [
                "dataset",
                "dut",
                "area",
                "test",
                "infra",
                "testbed",
                "framesize",
                "cores",
                "test_type",
                "offset",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["telemetry_timeseries"]).parameters),
            [
                "dataset",
                "series",
                "metric",
                "node_names",
                "testbed",
                "days",
                "start_time",
                "end_time",
                "passed",
                "aggregation",
                "offset",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["trending_catalog"]).parameters),
            [
                "dut",
                "area",
                "test",
                "infra",
                "testbed",
                "framesize",
                "cores",
                "test_type",
                "select_defaults",
                "offset",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["trending_series"]).parameters),
            ["series", "offset", "limit"],
        )
        self.assertEqual(
            list(inspect.signature(tools["trending"]).parameters),
            [
                "test_type",
                "dut_type",
                "passed",
                "job",
                "hosts",
                "test_id",
                "build",
                "offset",
                "aggregation",
                "sort_by",
                "sort_order",
                "columns",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["job_statistics"]).parameters),
            [
                "days",
                "job",
                "limit",
                "dut",
                "test_type",
                "cadence",
                "testbed",
                "select_defaults",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["iterative_catalog"]).parameters),
            [
                "release",
                "dut",
                "dut_version",
                "area",
                "test",
                "infra",
                "testbed",
                "framesize",
                "cores",
                "test_type",
                "select_defaults",
                "offset",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["iterative_series"]).parameters),
            ["series", "offset", "limit"],
        )
        self.assertEqual(
            list(inspect.signature(tools["iterative"]).parameters),
            [
                "test_type",
                "dut_type",
                "passed",
                "job",
                "release",
                "hosts",
                "test_id",
                "build",
                "offset",
                "aggregation",
                "sort_by",
                "sort_order",
                "columns",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["coverage_catalog"]).parameters),
            ["release", "dut", "dut_version", "area", "infra"],
        )
        self.assertEqual(
            list(inspect.signature(tools["coverage_tables"]).parameters),
            [
                "release",
                "dut",
                "dut_version",
                "area",
                "infra",
                "offset",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["comparison_catalog"]).parameters),
            [
                "release", "dut", "dut_version", "infra", "framesize",
                "cores", "test_type", "parameter", "value",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["comparison_table"]).parameters),
            [
                "release", "dut", "dut_version", "infra", "framesize",
                "cores", "test_type", "parameter", "value",
                "remove_extreme_outliers", "offset", "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["comparison_data"]).parameters),
            [
                "release", "dut", "dut_version", "infra", "framesize",
                "cores", "test_type", "parameter", "value", "offset",
                "limit",
            ],
        )
        self.assertEqual(
            list(inspect.signature(tools["coverage"]).parameters),
            [
                "test_type",
                "dut_type",
                "passed",
                "job",
                "release",
                "hosts",
                "test_id",
                "build",
                "offset",
                "aggregation",
                "sort_by",
                "sort_order",
                "columns",
                "limit",
            ],
        )

    def test_server_info_resource_shape_is_preserved(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        server_info = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "ServerInfo"
        )

        payload = json.loads(server_info())

        self.assertEqual(payload["name"], "csit_mcp")
        self.assertEqual(payload["data"]["status"], "ready")
        self.assertEqual(payload["data"]["last_refresh_started_by"], "manual")
        self.assertTrue(payload["data"]["configuration"]["valid"])
        self.assertEqual(
            payload["data"]["refresh_history"][0]["started_by"],
            "manual",
        )
        self.assertEqual(
            payload["endpoints"]["tools"],
            list(PUBLIC_TOOLS),
        )
        self.assertEqual(
            payload["endpoints"]["resources"],
            list(PUBLIC_RESOURCES),
        )
        self.assertEqual(
            payload["endpoints"]["public_resources"],
            list(PUBLIC_RESOURCES),
        )
        self.assertEqual(
            payload["endpoints"]["private_resources"],
            list(PRIVATE_RESOURCES),
        )
        self.assertEqual(payload["capabilities"]["tools"], 29)
        self.assertEqual(payload["capabilities"]["resources"], 1)
        self.assertEqual(
            payload["telemetry_queries"]["max_concurrent_queries"], 1
        )
        self.assertEqual(
            payload["telemetry_queries"]["response_cache_max_bytes"],
            8_000_000,
        )

    def test_comparison_tools_return_json_payloads(self):
        from tests.test_comparison_service import comparison_data

        cache = FakeDataCache()
        cache.iterative = comparison_data()
        mcp = FakeMCP()
        register_mcp_tools(mcp=mcp, data_cache=cache, settings=make_settings())
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}
        arguments = {
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

        catalog = json.loads(tools["comparison_catalog"](**arguments))
        table = json.loads(tools["comparison_table"](**arguments))
        data = json.loads(tools["comparison_data"](**arguments))

        self.assertTrue(catalog["complete"])
        self.assertEqual(table["dataset"], "comparison_table")
        self.assertEqual(table["records"][0]["unit"], "MPPS")
        self.assertEqual(data["dataset"], "comparison_data")
        self.assertIn(False, {record["passed"] for record in data["records"]})

    def test_trending_catalog_and_series_return_json_strings(self):
        cache = FakeDataCache()
        cache.trending.loc[:, "test_id"] = (
            "tests.vpp.perf.ip4_tunnels."
            "2n1l-100ge2p1e810cq-avf-ethip4geneve."
            "64b-1c-avf-ethip4geneve-mrr"
        )
        cache.trending.loc[:, "dut_type"] = "vpp"
        cache.trending.loc[:, "tg_type"] = "trex"
        cache.trending.loc[:, "test_type"] = "mrr"
        cache.trending.loc[:, "job"] = (
            "csit-vpp-perf-mrr-daily-master-2n-emr"
        )
        cache.trending["result_receive_rate_rate_unit"] = "pps"
        mcp = FakeMCP()
        register_mcp_tools(mcp=mcp, data_cache=cache, settings=make_settings())
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        catalog_text = tools["trending_catalog"](
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
        catalog = json.loads(catalog_text)
        series_id = catalog["records"][0]["series_id"]
        series_text = tools["trending_series"]([series_id], limit=2)
        series = json.loads(series_text)

        self.assertIsInstance(catalog_text, str)
        self.assertEqual(catalog["dataset"], "trending_catalog")
        self.assertIsInstance(series_text, str)
        self.assertEqual(series["dataset"], "trending_series")
        self.assertEqual(series["series"][0]["series_id"], series_id)
        self.assertEqual(series["records"][0]["throughput_unit"], "pps")
        self.assertEqual(series["records"][0]["dut_type"], "vpp")
        self.assertEqual(series["records"][0]["tg_type"], "trex")
        self.assertEqual(
            series["records"][0]["test_id"],
            cache.trending.iloc[0]["test_id"],
        )
        self.assertEqual(series["trend_analysis"]["engine"], "jumpavg")
        self.assertEqual(series["trend_analysis"]["version"], "0.4.2")
        self.assertEqual(
            series["records"][0]["throughput_analysis"]["classification"],
            "normal",
        )

    def test_targeted_telemetry_tool_returns_authoritative_json(self):
        cache = FakeDataCache()
        cache.trending.loc[:, "test_id"] = (
            "tests.vpp.perf.ip4_tunnels."
            "2n1l-100ge2p1e810cq-avf-ethip4geneve."
            "64b-1c-avf-ethip4geneve-mrr"
        )
        cache.trending.loc[:, "dut_type"] = "vpp"
        cache.trending.loc[:, "tg_type"] = "trex"
        cache.trending.loc[:, "test_type"] = "mrr"
        cache.trending.loc[:, "job"] = (
            "csit-vpp-perf-mrr-daily-master-2n-emr"
        )
        cache.trending["result_receive_rate_rate_unit"] = "pps"
        telemetry = (
            "vpp.runtime.clocks{hostname='sut1',hook='DUT1',"
            "node_name='p4-lookup',rate='mrr',state='active',"
            "thread_id='1',thread_name='vpp_wk_0'} 101\n"
        )
        encoded = base64.b64encode(
            zlib.compress(telemetry.encode("utf-8"))
        ).decode("ascii")
        cache.trending.loc[:, "telemetry"] = pd.Series(
            [[encoded] for _ in range(len(cache.trending))],
            index=cache.trending.index,
        )
        mcp = FakeMCP()
        register_mcp_tools(mcp=mcp, data_cache=cache, settings=make_settings())
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        catalog = json.loads(tools["trending_catalog"](
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
            testbed="all",
            framesize="all",
            cores="all",
            test_type="all",
            select_defaults=True,
        ))
        telemetry_catalog = json.loads(tools["telemetry_catalog"](
            dataset="trending",
            dut="vpp",
            area="ip4_tunnels",
            test="ethip4geneve",
            infra="2n-emr-100ge2p1e810cq-avf",
        ))
        payload = json.loads(tools["telemetry_timeseries"](
            "trending",
            [catalog["records"][0]["series_id"]],
            "cycles_per_packet",
            node_names=["p4-lookup"],
            start_time=(datetime.now(tz=UTC) - timedelta(days=31)).isoformat(),
            end_time=(datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
        ))

        self.assertEqual(
            telemetry_catalog["records"][0]["series_id"],
            catalog["records"][0]["series_id"],
        )
        self.assertEqual(payload["dataset"], "telemetry_timeseries")
        self.assertEqual(payload["metric"], "cycles_per_packet")
        self.assertTrue(payload["records"])
        self.assertEqual(payload["records"][0]["value"], 101)
        self.assertEqual(payload["records"][0]["node_name"], "p4-lookup")
        self.assertFalse(
            payload["completeness"]["representative_index_used"]
        )

    def test_iterative_catalog_and_series_return_json_strings(self):
        cache = FakeDataCache()
        cache.iterative = pd.DataFrame([{
            "job": "csit-vpp-perf-mrr-release-2n-skx",
            "build": 301,
            "test_type": "mrr",
            "dut_type": "vpp",
            "dut_version": "26.06-release",
            "tg_type": "trex",
            "hosts": ["10.30.0.1", "10.30.0.2"],
            "start_time": "2026-06-01T12:00:00+00:00",
            "passed": True,
            "release": "rls2606",
            "test_id": (
                "tests.vpp.perf.ip4."
                "2n1l-100ge2p1e810cq-avf-ethip4-ip4base-mrr."
                "64b-1c-avf-ethip4-ip4base-mrr"
            ),
            "result_receive_rate_rate_avg": 8_000_000.0,
            "result_receive_rate_rate_unit": "pps",
            "result_receive_rate_bandwidth_avg": 8_000_000_000.0,
            "result_receive_rate_bandwidth_unit": "bps",
        }])
        mcp = FakeMCP()
        register_mcp_tools(mcp=mcp, data_cache=cache, settings=make_settings())
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        catalog_text = tools["iterative_catalog"](select_defaults=True)
        catalog = json.loads(catalog_text)
        series_id = catalog["records"][0]["series_id"]
        series_text = tools["iterative_series"]([series_id])
        series = json.loads(series_text)

        self.assertIsInstance(catalog_text, str)
        self.assertEqual(catalog["dataset"], "iterative_catalog")
        self.assertEqual(catalog["filters"]["release"], "rls2606")
        self.assertIsInstance(series_text, str)
        self.assertEqual(series["dataset"], "iterative_series")
        self.assertEqual(series["series"][0]["series_id"], series_id)
        self.assertEqual(series["records"][0]["throughput_unit"], "pps")
        self.assertTrue(series["records"][0]["name"].endswith("-mrr"))

    def test_discovery_tools_return_json_strings(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        datasets_text = tools["datasets"]()
        columns_text = tools["columns"]("trending")
        values_text = tools["values"]("trending", "hosts", limit=10)
        schema_text = tools["schema"]("trending")

        datasets_payload = json.loads(datasets_text)
        columns_payload = json.loads(columns_text)
        values_payload = json.loads(values_text)
        schema_payload = json.loads(schema_text)

        self.assertIsInstance(datasets_text, str)
        self.assertEqual(datasets_payload["datasets"][1]["name"], "trending")
        self.assertEqual(columns_payload["dataset"], "trending")
        self.assertIn("hosts", {column["name"] for column in columns_payload["columns"]})
        self.assertEqual(values_payload["dataset"], "trending")
        self.assertEqual(values_payload["column"], "hosts")
        self.assertEqual(values_payload["values"][0]["value"], ["2n-skx", "host-a"])
        self.assertEqual(schema_payload["dataset"], "trending")
        self.assertTrue(schema_payload["configured"])

    def test_discovery_tools_validate_arguments_and_readiness(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(ready=False),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        dataset_payload = json.loads(tools["columns"]("missing"))
        column_payload = json.loads(tools["values"]("trending", "missing"))
        limit_payload = json.loads(tools["values"]("trending", "hosts", limit=0))
        values_unavailable_payload = json.loads(tools["values"]("trending", "hosts"))
        columns_payload = json.loads(tools["columns"]("trending"))
        schema_payload = json.loads(tools["schema"]("trending"))

        self.assertEqual(dataset_payload["error"], "validation_error")
        self.assertEqual(column_payload["error"], "validation_error")
        self.assertEqual(limit_payload["error"], "validation_error")
        self.assertEqual(values_unavailable_payload["error"], "data_unavailable")
        self.assertFalse(columns_payload["ready"])
        self.assertTrue(schema_payload["configured"])

    def test_discovery_tools_emit_structured_logs(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            tools["datasets"]()
            tools["values"]("trending", "hosts", limit=2)

        events = log_events(logs.records)
        self.assertEqual(
            [event["event"] for event in events],
            ["mcp_discovery_tool_completed", "mcp_discovery_tool_completed"],
        )
        self.assertEqual(events[0]["tool"], "datasets")
        self.assertEqual(events[0]["returned_count"], 4)
        self.assertEqual(events[1]["tool"], "values")
        self.assertEqual(events[1]["dataset"], "trending")
        self.assertEqual(events[1]["column"], "hosts")
        self.assertEqual(events[1]["returned_count"], 2)
        self.assertEqual(events[1]["cache_age_seconds"], 12.5)
        self.assertNotIn("records", logs.output[0])

    def test_discovery_tools_log_validation_and_unavailable_errors(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(ready=False),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            tools["columns"]("missing")
            tools["values"]("trending", "hosts")

        events = log_events(logs.records)
        self.assertEqual(events[0]["event"], "mcp_discovery_tool_completed")
        self.assertEqual(events[0]["error"], "validation_error")
        self.assertEqual(events[1]["error"], "data_unavailable")
        self.assertEqual(events[1]["data_status"], "loading")

    def test_analysis_tools_return_compact_json_strings(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        compare_payload = json.loads(tools["compare_hosts"](
            "iterative",
            "result_receive_rate_rate_avg",
            test_id="iter-test-a",
        ))
        trend_payload = json.loads(tools["trend_summary"](
            "iterative",
            "result_receive_rate_rate_avg",
            test_id="iter-test-a",
            recent_count=1,
            baseline_count=1,
        ))
        regression_payload = json.loads(tools["find_regressions"](
            "iterative",
            "result_receive_rate_rate_avg",
            preferred_direction="lower",
            recent_count=1,
            baseline_count=1,
            threshold_percent=1.0,
        ))
        anomaly_payload = json.loads(tools["find_anomalies"](
            "trending",
            "result_receive_rate_rate_avg",
            threshold=1.0,
            limit=1,
        ))
        failures_payload = json.loads(tools["top_failures"](
            "coverage",
            group_by="test_id",
        ))

        self.assertEqual(compare_payload["analysis"], "compare_hosts")
        self.assertEqual(compare_payload["group_by"], "hosts")
        self.assertEqual(trend_payload["analysis"], "trend_summary")
        self.assertEqual(trend_payload["summary"]["recent_count"], 1)
        self.assertEqual(regression_payload["analysis"], "find_regressions")
        self.assertTrue(regression_payload["records"])
        self.assertEqual(anomaly_payload["analysis"], "find_anomalies")
        self.assertLessEqual(len(anomaly_payload["records"]), 1)
        self.assertEqual(failures_payload["analysis"], "top_failures")
        self.assertEqual(failures_payload["records"][0]["group_key"], "coverage-test-b")

    def test_analysis_tools_validate_arguments_and_readiness(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        dataset_payload = json.loads(tools["compare_hosts"](
            "statistics",
            "result_receive_rate_rate_avg",
        ))
        result_payload = json.loads(tools["trend_summary"](
            "iterative",
            "missing_result",
            recent_count=1,
            baseline_count=1,
        ))
        threshold_payload = json.loads(tools["find_anomalies"](
            "iterative",
            "result_receive_rate_rate_avg",
            threshold=0,
        ))

        unavailable_mcp = FakeMCP()
        register_mcp_tools(
            mcp=unavailable_mcp,
            data_cache=FakeDataCache(ready=False),
            settings=make_settings(),
        )
        unavailable_tools = {
            kwargs["name"]: func for kwargs, func in unavailable_mcp.tools
        }
        unavailable_payload = json.loads(unavailable_tools["compare_hosts"](
            "iterative",
            "result_receive_rate_rate_avg",
        ))

        self.assertEqual(dataset_payload["error"], "validation_error")
        self.assertEqual(result_payload["error"], "validation_error")
        self.assertEqual(threshold_payload["error"], "validation_error")
        self.assertEqual(unavailable_payload["error"], "data_unavailable")

    def test_telemetry_tools_return_compact_json_strings(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        metrics_payload = json.loads(tools["telemetry_metrics"](
            "trending",
            metric_name="csit_packets_total",
            hosts="2n-skx",
            limit=1,
        ))
        values_payload = json.loads(tools["telemetry_metric_values"](
            "trending",
            "csit_packets_total",
            group_by="hosts",
        ))
        trend_payload = json.loads(tools["telemetry_trend_summary"](
            "trending",
            "csit_packets_total",
            recent_count=1,
            baseline_count=1,
        ))
        anomaly_payload = json.loads(tools["telemetry_anomalies"](
            "trending",
            "csit_packets_total",
            threshold=1.0,
        ))

        self.assertTrue(metrics_payload["telemetry"])
        self.assertEqual(metrics_payload["dataset"], "trending")
        self.assertEqual(metrics_payload["records"][0]["metric_name"], "csit_packets_total")
        self.assertEqual(values_payload["analysis"], "telemetry_metric_values")
        self.assertEqual(values_payload["group_by"], "hosts")
        self.assertEqual(trend_payload["analysis"], "telemetry_trend_summary")
        self.assertEqual(anomaly_payload["analysis"], "telemetry_anomalies")

    def test_telemetry_tools_validate_arguments_and_readiness(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        dataset_payload = json.loads(tools["telemetry_metrics"]("statistics"))
        no_telemetry_payload = json.loads(tools["telemetry_metrics"]("coverage"))
        group_payload = json.loads(tools["telemetry_metric_values"](
            "trending",
            "csit_packets_total",
            group_by="missing",
        ))

        unavailable_mcp = FakeMCP()
        register_mcp_tools(
            mcp=unavailable_mcp,
            data_cache=FakeDataCache(ready=False),
            settings=make_settings(),
        )
        unavailable_tools = {
            kwargs["name"]: func for kwargs, func in unavailable_mcp.tools
        }
        unavailable_payload = json.loads(
            unavailable_tools["telemetry_metrics"]("trending")
        )

        self.assertEqual(dataset_payload["error"], "validation_error")
        self.assertEqual(no_telemetry_payload["error"], "validation_error")
        self.assertEqual(group_payload["error"], "validation_error")
        self.assertEqual(unavailable_payload["error"], "data_unavailable")

    def test_analysis_tool_emits_structured_log(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            tools["compare_hosts"]("iterative", "result_receive_rate_rate_avg")

        event = log_events(logs.records)[0]
        self.assertEqual(event["event"], "mcp_analysis_tool_completed")
        self.assertEqual(event["tool"], "compare_hosts")
        self.assertEqual(event["analysis"], "compare_hosts")
        self.assertEqual(event["dataset"], "iterative")
        self.assertEqual(event["result_column"], "result_receive_rate_rate_avg")
        self.assertEqual(event["group_by"], "hosts")
        self.assertEqual(event["data_status"], "ready")
        self.assertEqual(event["cache_age_seconds"], 12.5)
        self.assertNotIn("records", logs.output[0])

    def test_data_parquet_resource_serializes_named_dataset(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        get_parquet = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "DataParquet"
        )

        payload_text = get_parquet("statistics")
        payload = json.loads(payload_text)

        self.assertIsInstance(payload_text, str)
        self.assertEqual(payload["query"], "statistics")
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(payload["total_row_count"], 2)
        self.assertEqual(payload["returned_count"], 2)
        self.assertFalse(payload["has_more"])
        self.assertFalse(payload["truncated"])
        self.assertEqual(payload["records"][0]["job"], "job-a")

    def test_data_parquet_resource_serializes_all_datasets(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        get_parquet = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "DataParquet"
        )

        payload_text = get_parquet("all")
        payload = json.loads(payload_text)

        self.assertIsInstance(payload_text, str)
        self.assertEqual(payload["query"], "all")
        self.assertEqual(payload["datasets"]["statistics"]["row_count"], 2)
        self.assertEqual(payload["datasets"]["trending"]["row_count"], 4)
        self.assertEqual(payload["datasets"]["iterative"]["row_count"], 4)
        self.assertEqual(payload["datasets"]["coverage"]["row_count"], 3)
        self.assertFalse(payload["datasets"]["iterative"]["has_more"])
        self.assertEqual(
            payload["datasets"]["iterative"]["records"][0]["hosts"],
            ["2n-skx", "host-a"],
        )

    def test_data_parquet_resource_emits_structured_log(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        get_parquet = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "DataParquet"
        )

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            get_parquet("all")

        events = log_events(logs.records)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "mcp_resource_completed")
        self.assertEqual(events[0]["resource"], "data://parquet/{query}")
        self.assertEqual(events[0]["query"], "all")
        self.assertEqual(
            events[0]["datasets"]["statistics"]["returned_count"],
            2,
        )
        self.assertEqual(events[0]["cache_age_seconds"], 12.5)
        self.assertNotIn("records", logs.output[0])

    def test_data_parquet_resource_caps_large_dataset_preview(self):
        cache = FakeDataCache()
        cache.statistics = pd.DataFrame(
            {"job": [f"job-{index}" for index in range(1001)]}
        )
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=cache,
            settings=make_settings(),
        )
        get_parquet = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "DataParquet"
        )

        payload = json.loads(get_parquet("statistics"))

        self.assertEqual(payload["row_count"], 1001)
        self.assertEqual(payload["total_row_count"], 1001)
        self.assertEqual(payload["returned_count"], 1000)
        self.assertTrue(payload["has_more"])
        self.assertTrue(payload["truncated"])
        self.assertEqual(len(payload["records"]), 1000)

    def test_trending_tool_returns_stable_response_with_filters(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        payload = json.loads(
            trending(
                test_type="mrr",
                dut_type="vpp",
                passed=True,
                job="job-a",
                hosts="2n-skx",
                test_id="test-a",
                build=11,
                limit=5,
            )
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["dataset"], "trending")
        self.assertEqual(payload["total_row_count"], 4)
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["returned_count"], 1)
        self.assertFalse(payload["has_more"])
        self.assertIsNone(payload["next_offset"])
        self.assertEqual(
            payload["filters"],
            {
                "test_type": "mrr",
                "dut_type": "vpp",
                "job": "job-a",
                "hosts": "2n-skx",
                "test_id": "test-a",
                "build": 11,
                "passed": True,
                "limit": 5,
                "offset": 0,
                "aggregation": "none",
                "sort_by": None,
                "sort_order": "desc",
                "columns": None,
            },
        )
        self.assertEqual(payload["records"][0]["test_id"], "test-a")
        self.assertEqual(payload["records"][0]["hosts"], ["2n-skx", "host-a"])

    def test_trending_tool_filters_by_job(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        payload = json.loads(trending(job="job-a", limit=10))

        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(payload["filters"]["job"], "job-a")
        self.assertEqual(
            {record["job"] for record in payload["records"]},
            {"job-a"},
        )

    def test_trending_tool_accepts_string_boolean_filter(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        payload = json.loads(trending(passed="false"))

        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["filters"]["passed"], False)
        self.assertEqual(payload["records"][0]["test_id"], "test-b")

    def test_trending_tool_validates_missing_filter_column(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(include_trending_test_type=False),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        payload = json.loads(trending(test_type="mrr"))

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "test_type")

    def test_trending_tool_validates_missing_new_filter_column(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(include_trending_hosts=False),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        payload = json.loads(trending(hosts="2n-skx"))

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "hosts")

    def test_trending_tool_applies_offset_after_filtering(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        payload = json.loads(trending(test_type="mrr", offset=1, limit=1))

        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(payload["returned_count"], 1)
        self.assertEqual(payload["offset"], 1)
        self.assertTrue(payload["has_more"])
        self.assertEqual(payload["next_offset"], 2)
        self.assertEqual(payload["filters"]["offset"], 1)
        self.assertEqual(payload["records"][0]["build"], 12)

    def test_trending_tool_aggregates_by_test_id(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        payload = json.loads(trending(test_type="mrr", aggregation="test_id"))
        records = {
            record["test_id"]: record
            for record in payload["records"]
        }

        self.assertEqual(payload["aggregation"], "test_id")
        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(records["test-a"]["row_count"], 2)
        self.assertEqual(records["test-a"]["passed_count"], 2)
        self.assertEqual(records["test-b"]["failed_count"], 1)
        self.assertEqual(records["test-a"]["result_receive_rate_rate_avg_max"], 160.0)

    def test_data_tool_returns_response_too_large_payload(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )
        original_limit = serialization.MAX_SERIALIZED_RESPONSE_BYTES
        serialization.MAX_SERIALIZED_RESPONSE_BYTES = 200
        try:
            payload = json.loads(trending(limit=4))
        finally:
            serialization.MAX_SERIALIZED_RESPONSE_BYTES = original_limit

        self.assertEqual(payload["error"], "response_too_large")
        self.assertEqual(payload["context"]["dataset"], "trending")
        self.assertIn("suggestions", payload)

    def test_data_tool_emits_structured_log(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            trending(test_type="mrr", limit=1)

        events = log_events(logs.records)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "mcp_data_tool_completed")
        self.assertEqual(events[0]["tool"], "trending")
        self.assertEqual(events[0]["dataset"], "trending")
        self.assertEqual(events[0]["aggregation"], "none")
        self.assertEqual(events[0]["limit"], 1)
        self.assertEqual(events[0]["offset"], 0)
        self.assertEqual(events[0]["row_count"], 3)
        self.assertEqual(events[0]["returned_count"], 1)
        self.assertTrue(events[0]["has_more"])
        self.assertEqual(events[0]["data_status"], "ready")
        self.assertEqual(events[0]["cache_age_seconds"], 12.5)
        self.assertNotIn("records", logs.output[0])

    def test_data_tool_logs_validation_and_unavailable_errors(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            tools["iterative"](offset=-1)

        validation_event = log_events(logs.records)[0]
        self.assertEqual(validation_event["event"], "mcp_data_tool_completed")
        self.assertEqual(validation_event["tool"], "iterative")
        self.assertEqual(validation_event["error"], "validation_error")

        unavailable_mcp = FakeMCP()
        register_mcp_tools(
            mcp=unavailable_mcp,
            data_cache=FakeDataCache(ready=False),
            settings=make_settings(),
        )
        unavailable_tools = {
            kwargs["name"]: func for kwargs, func in unavailable_mcp.tools
        }
        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            unavailable_tools["trending"]()

        unavailable_event = log_events(logs.records)[0]
        self.assertEqual(unavailable_event["error"], "data_unavailable")
        self.assertEqual(unavailable_event["data_status"], "loading")

    def test_job_statistics_tool_returns_stable_response_with_filters(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        job_statistics = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "job_statistics"
        )

        payload = json.loads(job_statistics(days=7, job="job-a", limit=1))

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["dataset"], "statistics")
        self.assertEqual(payload["total_row_count"], 2)
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["returned_count"], 1)
        self.assertFalse(payload["has_more"])
        self.assertIsNone(payload["next_offset"])
        self.assertEqual(
            payload["filters"],
            {
                "days": 7,
                "job": "job-a",
                "limit": 1,
                "dut": None,
                "test_type": None,
                "cadence": None,
                "testbed": None,
                "select_defaults": False,
            },
        )
        self.assertEqual(payload["records"][0]["job"], "job-a")

    def test_job_statistics_tool_validates_limit(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        job_statistics = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "job_statistics"
        )

        payload = json.loads(job_statistics(limit=0))

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "limit")

    def test_iterative_tool_returns_stable_response_with_filters(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        payload = json.loads(
            iterative(
                test_type="mrr",
                dut_type="vpp",
                passed=True,
                job="iter-job-a",
                release="rls2606",
                hosts=["2n-skx", "host-a"],
                test_id="iter-test-a",
                build=21,
                limit=10,
            )
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["dataset"], "iterative")
        self.assertEqual(payload["total_row_count"], 4)
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(
            payload["filters"],
            {
                "test_type": "mrr",
                "dut_type": "vpp",
                "job": "iter-job-a",
                "release": "rls2606",
                "hosts": ["2n-skx", "host-a"],
                "test_id": "iter-test-a",
                "build": 21,
                "passed": True,
                "limit": 10,
                "offset": 0,
                "aggregation": "none",
                "sort_by": None,
                "sort_order": "desc",
                "columns": None,
            },
        )
        self.assertEqual(payload["records"][0]["test_id"], "iter-test-a")
        self.assertEqual(payload["records"][0]["hosts"], ["2n-skx", "host-a"])

    def test_iterative_tool_aggregates_by_hosts(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        payload = json.loads(iterative(aggregation="hosts", limit=10))
        records = {
            record["hosts"]: record
            for record in payload["records"]
        }

        self.assertEqual(payload["aggregation"], "hosts")
        self.assertEqual(payload["row_count"], 4)
        self.assertEqual(records["2n-skx,host-a"]["row_count"], 2)
        self.assertEqual(records["2n-skx,host-a"]["passed_count"], 1)
        self.assertEqual(records["2n-skx,host-a"]["failed_count"], 1)
        self.assertEqual(
            records["3n-alt,host-b"]["result_receive_rate_rate_avg_mean"],
            120.0,
        )

    def test_iterative_tool_aggregates_by_hosts_and_test_id(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        payload = json.loads(
            iterative(test_id="iter-test-a", aggregation="hosts_by_test_id")
        )

        self.assertEqual(payload["aggregation"], "hosts_by_test_id")
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(payload["returned_count"], 2)
        self.assertFalse(payload["has_more"])
        self.assertIsNone(payload["next_offset"])
        self.assertEqual(
            {record["hosts"] for record in payload["records"]},
            {"2n-skx,host-a", "3n-alt,host-b"},
        )
        self.assertEqual(payload["records"][0]["test_id"], "iter-test-a")

    def test_iterative_tool_sorts_and_projects_aggregated_results(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        payload = json.loads(
            iterative(
                test_id="iter-test-a",
                aggregation="hosts_by_test_id",
                sort_by="result_receive_rate_rate_avg_max",
                columns=[
                    "test_id",
                    "hosts",
                    "result_receive_rate_rate_avg_max",
                ],
                limit=1,
            )
        )

        self.assertEqual(payload["returned_count"], 1)
        self.assertTrue(payload["has_more"])
        self.assertEqual(payload["next_offset"], 1)
        self.assertEqual(
            payload["columns"],
            ["test_id", "hosts", "result_receive_rate_rate_avg_max"],
        )
        self.assertEqual(payload["records"][0]["hosts"], "3n-alt,host-b")
        self.assertEqual(
            payload["records"][0]["result_receive_rate_rate_avg_max"],
            130.0,
        )

    @unittest.skipIf(pa is None, "pyarrow is not available")
    def test_iterative_tool_handles_arrow_list_hosts(self):
        cache = FakeDataCache()
        hosts = pa.array(
            [
                ["10.30.51.83", "10.30.51.84"],
                ["10.30.51.83", "10.30.51.85"],
                ["10.30.51.83", "10.30.51.84"],
            ],
            type=pa.list_(pa.string()),
        )
        table = pa.table(
            {
                "job": ["iter-job-a", "iter-job-a", "iter-job-b"],
                "test_id": ["iter-test-a", "iter-test-a", "iter-test-b"],
                "test_type": ["mrr", "mrr", "mrr"],
                "dut_type": ["vpp", "vpp", "vpp"],
                "hosts": hosts,
                "build": [21, 22, 23],
                "passed": [True, False, True],
                "release": ["rls2606", "rls2606", "rls2606"],
                "result_receive_rate_rate_avg": [100.0, 130.0, 80.0],
            }
        )
        cache.iterative = table.to_pandas(types_mapper=pd.ArrowDtype)
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=cache,
            settings=make_settings(),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        raw_payload = json.loads(
            iterative(
                sort_by="hosts",
                sort_order="asc",
                columns=["hosts", "test_id"],
                limit=3,
            )
        )
        aggregate_payload = json.loads(
            iterative(
                aggregation="hosts_by_test_id",
                sort_by="hosts",
                sort_order="asc",
                limit=10,
            )
        )

        self.assertNotIn("error", raw_payload)
        self.assertEqual(
            raw_payload["records"][0]["hosts"],
            ["10.30.51.83", "10.30.51.84"],
        )
        self.assertNotIn("error", aggregate_payload)
        self.assertEqual(aggregate_payload["aggregation"], "hosts_by_test_id")
        self.assertEqual(
            {record["hosts"] for record in aggregate_payload["records"]},
            {"10.30.51.83,10.30.51.84", "10.30.51.83,10.30.51.85"},
        )

    def test_iterative_tool_reads_fixture_mode_cache(self):
        data_cache = DataCacheService(
            settings=make_settings(data_mode="fixture"),
        )
        data_cache.load()
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=data_cache,
            settings=make_settings(data_mode="fixture"),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        payload = json.loads(
            iterative(
                test_id=(
                    "tests.vpp.perf.ip4."
                    "2n1l-100ge2p1e810cq-avf-ethip4-ip4base-mrr."
                    "64b-1c-avf-ethip4-ip4base-mrr"
                ),
                aggregation="hosts_by_test_id",
                sort_by="result_receive_rate_rate_avg_max",
                limit=10,
            )
        )
        records = {
            record["hosts"]: record
            for record in payload["records"]
        }

        self.assertEqual(payload["dataset"], "iterative")
        self.assertEqual(payload["aggregation"], "hosts_by_test_id")
        self.assertEqual(payload["row_count"], 11)
        self.assertEqual(payload["returned_count"], 4)
        self.assertEqual(
            set(records),
            {
                "10.30.0.1,10.30.0.2",
                "10.30.0.3,10.30.0.4",
                "10.70.0.1,10.70.0.2",
                "10.70.0.3,10.70.0.4",
            },
        )
        self.assertEqual(
            records["10.30.0.1,10.30.0.2"][
                "result_receive_rate_rate_avg_max"
            ],
            12_000_000.0,
        )

    def test_iterative_tool_validates_offset_and_aggregation(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        offset_payload = json.loads(iterative(offset=-1))
        aggregation_payload = json.loads(iterative(aggregation="invalid"))

        self.assertEqual(offset_payload["error"], "validation_error")
        self.assertEqual(offset_payload["details"]["errors"][0]["field"], "offset")
        self.assertEqual(aggregation_payload["error"], "validation_error")
        self.assertEqual(
            aggregation_payload["details"]["errors"][0]["field"],
            "aggregation",
        )

    def test_iterative_tool_validates_sort_and_columns(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )

        sort_payload = json.loads(iterative(sort_by="missing_column"))
        columns_payload = json.loads(iterative(columns=["missing_column"]))

        self.assertEqual(sort_payload["error"], "validation_error")
        self.assertEqual(sort_payload["details"]["errors"][0]["field"], "sort_by")
        self.assertEqual(columns_payload["error"], "validation_error")
        self.assertEqual(
            columns_payload["details"]["errors"][0]["field"],
            "columns",
        )

    def test_coverage_tool_returns_stable_response_with_filters(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        coverage = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "coverage"
        )

        payload = json.loads(
            coverage(
                test_type="ndrpdr",
                dut_type="dpdk",
                passed=False,
                job="coverage-job-b",
                release="rls2606",
                hosts="2n-skx",
                test_id="coverage-test-b",
                build=32,
                limit=10,
            )
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["dataset"], "coverage")
        self.assertEqual(payload["total_row_count"], 3)
        self.assertEqual(payload["row_count"], 1)
        self.assertFalse(payload["has_more"])
        self.assertIsNone(payload["next_offset"])
        self.assertEqual(
            payload["filters"],
            {
                "test_type": "ndrpdr",
                "dut_type": "dpdk",
                "job": "coverage-job-b",
                "release": "rls2606",
                "hosts": "2n-skx",
                "test_id": "coverage-test-b",
                "build": 32,
                "passed": False,
                "limit": 10,
                "offset": 0,
                "aggregation": "none",
                "sort_by": None,
                "sort_order": "desc",
                "columns": None,
            },
        )
        self.assertEqual(payload["records"][0]["test_id"], "coverage-test-b")
        self.assertEqual(payload["records"][0]["hosts"], ["2n-skx", "host-a"])

    def test_focused_coverage_tools_return_catalog_and_table_payloads(self):
        data_cache = FakeDataCache()
        data_cache.coverage = pd.DataFrame([{
            "job": "csit-vpp-perf-report-coverage-2606-2n-zn2",
            "build": 42,
            "test_type": "ndrpdr",
            "dut_type": "vpp",
            "dut_version": "26.06-release",
            "passed": True,
            "release": "rls2606",
            "test_id": (
                "tests.vpp.perf.ip4."
                "2n1l-25ge2p1xxv710-avf-ethip4-ip4base-ndrpdr."
                "64b-1c-avf-ethip4-ip4base-ndrpdr"
            ),
            "result_pdr_lower_rate_unit": "pps",
            "result_ndr_lower_rate_value": 10_000_000.0,
            "result_pdr_lower_rate_value": 12_000_000.0,
            "result_ndr_lower_bandwidth_value": 20_000_000_000.0,
            "result_pdr_lower_bandwidth_value": 24_000_000_000.0,
        }])
        mcp = FakeMCP()
        register_mcp_tools(mcp, data_cache, make_settings())
        tools = {kwargs["name"]: func for kwargs, func in mcp.tools}

        catalog = json.loads(tools["coverage_catalog"]())
        self.assertFalse(catalog["complete"])
        self.assertEqual(
            catalog["filter_options"]["release"][0]["value"],
            "rls2606",
        )
        tables = json.loads(tools["coverage_tables"](
            "rls2606",
            "vpp",
            "26.06-release",
            "ip4",
            "2n-zn2-25ge2p1xxv710-avf",
        ))
        self.assertEqual(tables["dataset"], "coverage_tables")
        self.assertEqual(tables["returned_count"], 1)
        self.assertEqual(tables["records"][0]["throughput_ndr"], 10.0)

    def test_coverage_tool_aggregates_by_hosts_by_test_id(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        coverage = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "coverage"
        )

        payload = json.loads(
            coverage(test_id="coverage-test-b", aggregation="hosts_by_test_id")
        )
        records = {
            record["hosts"]: record
            for record in payload["records"]
        }

        self.assertEqual(payload["aggregation"], "hosts_by_test_id")
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(records["2n-skx,host-a"]["failed_count"], 1)
        self.assertEqual(records["3n-alt,host-b"]["passed_count"], 1)
        self.assertEqual(
            records["3n-alt,host-b"]["result_pdr_lower_rate_value_mean"],
            30.0,
        )

    def test_data_parquet_resource_serializes_unknown_dataset_error(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        get_parquet = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "DataParquet"
        )

        payload_text = get_parquet("missing")
        payload = json.loads(payload_text)

        self.assertIsInstance(payload_text, str)
        self.assertEqual(payload["error"], "dataset_not_found")

    def test_data_parquet_resource_logs_error_paths(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(),
            settings=make_settings(),
        )
        get_parquet = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "DataParquet"
        )

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            get_parquet("missing")

        event = log_events(logs.records)[0]
        self.assertEqual(event["event"], "mcp_resource_completed")
        self.assertEqual(event["query"], "missing")
        self.assertEqual(event["error"], "dataset_not_found")

    def test_register_routes_preserves_health_response(self):
        mcp = FakeMCP()

        register_routes(mcp, data_cache=FakeDataCache())

        health_check = next(
            func for path, methods, func in mcp.routes
            if path == "/health"
        )
        response = asyncio.run(health_check(None))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.body),
            {"status": "healthy", "service": "mcp-server"},
        )

    def test_register_routes_adds_readiness_response(self):
        mcp = FakeMCP()

        register_routes(mcp, data_cache=FakeDataCache(ready=False))

        path, methods, readiness_check = next(
            item for item in mcp.routes
            if item[0] == "/ready"
        )
        response = asyncio.run(readiness_check(None))
        payload = json.loads(response.body)

        self.assertEqual(path, "/ready")
        self.assertEqual(methods, ["GET"])
        self.assertEqual(response.status_code, 503)
        self.assertEqual(payload["data"]["status"], "loading")
        self.assertIn("refresh_history", payload["data"])

    def test_readiness_response_reports_invalid_configuration(self):
        mcp = FakeMCP()
        data_cache = DataCacheService(
            settings=make_settings(
                validation_errors=(
                    {
                        "field": "CSIT_DATA_MODE",
                        "value": "local",
                        "message": "expected 's3' or 'fixture'",
                    },
                ),
            )
        )
        data_cache.load()

        register_routes(mcp, data_cache=data_cache)

        readiness_check = next(
            func for path, methods, func in mcp.routes
            if path == "/ready"
        )
        response = asyncio.run(readiness_check(None))
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 503)
        self.assertEqual(payload["data"]["status"], "failed")
        self.assertFalse(payload["data"]["configuration"]["valid"])
        self.assertEqual(
            payload["data"]["configuration"]["errors"][0]["field"],
            "CSIT_DATA_MODE",
        )

    def test_register_routes_adds_refresh_response(self):
        mcp = FakeMCP()

        register_routes(mcp, data_cache=FakeDataCache(refresh_started=True))

        path, methods, refresh_data = next(
            item for item in mcp.routes
            if item[0] == "/data/refresh"
        )
        response = asyncio.run(refresh_data(None))
        payload = json.loads(response.body)

        self.assertEqual(path, "/data/refresh")
        self.assertEqual(methods, ["POST"])
        self.assertEqual(response.status_code, 202)
        self.assertEqual(payload["status"], "refresh_started")
        self.assertIn("last_refresh_started_by", payload["data"])

    def test_register_routes_reports_refresh_conflict(self):
        mcp = FakeMCP()

        register_routes(mcp, data_cache=FakeDataCache(refresh_started=False))
        refresh_data = next(
            func for path, methods, func in mcp.routes
            if path == "/data/refresh"
        )

        response = asyncio.run(refresh_data(None))
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(payload["status"], "refresh_in_progress")

    def test_mcp_tools_return_unavailable_payload_before_data_ready(self):
        mcp = FakeMCP()
        register_mcp_tools(
            mcp=mcp,
            data_cache=FakeDataCache(ready=False),
            settings=make_settings(),
        )
        trending = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "trending"
        )
        iterative = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "iterative"
        )
        coverage = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "coverage"
        )
        dashboard = next(
            func for kwargs, func in mcp.tools
            if kwargs["name"] == "dashboard"
        )
        get_parquet = next(
            func for kwargs, func in mcp.resources
            if kwargs["name"] == "DataParquet"
        )

        trending_payload = json.loads(trending())
        iterative_payload = json.loads(iterative())
        coverage_payload = json.loads(coverage())
        parquet_text = get_parquet("statistics")
        parquet_payload = json.loads(parquet_text)
        dashboard_html = dashboard()

        self.assertEqual(trending_payload["error"], "data_unavailable")
        self.assertEqual(iterative_payload["error"], "data_unavailable")
        self.assertEqual(coverage_payload["error"], "data_unavailable")
        self.assertIsInstance(parquet_text, str)
        self.assertEqual(parquet_payload["error"], "data_unavailable")
        self.assertIn("CSIT data is not ready", dashboard_html)


if __name__ == "__main__":
    unittest.main()
