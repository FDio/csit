import asyncio
import base64
import json
import tempfile
import threading
import time
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

import pandas as pd
try:
    import pyarrow as pa
except ImportError:
    pa = None

from dashboard.data.data import Data
from dashboard.data.fixture_data import FixtureDataReader
from dashboard.services.data_cache import DataCacheService, DataUnavailableError
from dashboard.services.telemetry import normalize_dataset_telemetry
from dashboard.settings import AppSettings


def log_events(records):
    return [json.loads(record.getMessage()) for record in records]


def make_settings(
        time_period=15,
        max_time_period=200,
        data_mode="s3",
        refresh_interval_seconds=0,
        data_spec_file="data.yaml",
        start_report=False,
        start_coverage=False,
        telemetry_max_source_rows=500,
        telemetry_max_samples=100_000,
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
        data_spec_file=data_spec_file,
        max_time_period=max_time_period,
        time_period=time_period,
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
        telemetry_max_source_rows=telemetry_max_source_rows,
        telemetry_max_samples=telemetry_max_samples,
        validation_errors=validation_errors,
    )


def make_frames():
    return {
        "statistics": pd.DataFrame(
            {
                "job": ["job-a"],
                "build": [1],
                "start_time": [pd.Timestamp("2026-06-05")],
                "duration": [123],
                "year": [2026],
                "month": [6],
                "day": [5],
                "stats_type": ["sra"],
            }
        ),
        "trending": pd.DataFrame({"test_id": ["test-a"]}),
        "iterative": pd.DataFrame(),
        "coverage": pd.DataFrame(),
    }


def encoded_telemetry(value=100.0):
    text = (
        "# HELP csit_packets_total Packets observed\n"
        "# TYPE csit_packets_total counter\n"
        f"csit_packets_total{{worker=\"0\"}} {value}\n"
        "# EOF\n"
    )
    return base64.b64encode(zlib.compress(text.encode())).decode()


def write_data_spec(directory, dataset_names):
    spec_path = Path(directory) / "data.yaml"
    spec_path.write_text(
        "\n".join(
            (
                f"- data_type: {dataset_name}\n"
                "  partition: test_type\n"
                "  partition_name: fixture\n"
                "  path: s3://example/fixture\n"
                "  columns:\n"
                "    - test_id\n"
            )
            for dataset_name in dataset_names
        ),
        encoding="utf-8",
    )
    return str(spec_path)


class FakeDataReader:
    last_data_spec_file = None
    last_days = None

    def __init__(self, data_spec_file):
        FakeDataReader.last_data_spec_file = data_spec_file

    def read_all_data(self, days=None):
        FakeDataReader.last_days = days
        return make_frames()


class FailingDataReader:
    def __init__(self, data_spec_file):
        self.data_spec_file = data_spec_file

    def read_all_data(self, days=None):
        raise RuntimeError("boom")


class EmptyRequiredDataReader:
    def __init__(self, data_spec_file):
        self.data_spec_file = data_spec_file

    def read_all_data(self, days=None):
        data = make_frames()
        data["statistics"] = pd.DataFrame()
        return data


class SlowDataReader:
    def __init__(self, data_spec_file):
        self.data_spec_file = data_spec_file

    def read_all_data(self, days=None):
        time.sleep(0.05)
        return make_frames()


class UnexpectedDataReader:
    constructed = False

    def __init__(self, data_spec_file):
        UnexpectedDataReader.constructed = True

    def read_all_data(self, days=None):
        return make_frames()


class UnconfiguredOptionalDataReader:
    def __init__(self, data_spec_file):
        self.data_spec_file = data_spec_file

    def read_all_data(self, days=None):
        data = make_frames()
        data["iterative"] = pd.DataFrame()
        data["coverage"] = pd.DataFrame()
        return data


class NormalizationDataReader:
    def __init__(self, data_spec_file):
        self.data_spec_file = data_spec_file

    def read_all_data(self, days=None):
        return {
            "statistics": pd.DataFrame(
                {
                    "job": ["job-a"],
                    "build": ["10"],
                    "start_time": ["2026-06-05T10:00:00+02:00"],
                    "duration": [123],
                }
            ),
            "trending": pd.DataFrame(
                {
                    "test_id": ["test-a"],
                    "test_type": ["mrr"],
                    "dut_type": ["vpp"],
                    "hosts": [("2n-skx", "host-a")],
                    "build": ["11"],
                    "passed": ["yes"],
                    "start_time": ["bad timestamp"],
                    "telemetry": [[encoded_telemetry(100.5)]],
                    "result_receive_rate_rate_avg": ["100.5"],
                    "result_receive_rate_rate_unit": ["pps"],
                }
            ),
            "iterative": pd.DataFrame(),
            "coverage": pd.DataFrame(),
        }


class UpdatedDataReader:
    def __init__(self, data_spec_file):
        self.data_spec_file = data_spec_file

    def read_all_data(self, days=None):
        data = make_frames()
        data["statistics"]["job"] = ["job-updated"]
        return data


class DataCacheServiceTests(unittest.TestCase):
    def test_resolves_default_s3_reader(self):
        service = DataCacheService(settings=make_settings())

        self.assertIs(service._resolve_data_reader_cls(), Data)

    def test_resolves_fixture_reader_for_fixture_mode(self):
        service = DataCacheService(
            settings=make_settings(data_mode="fixture"),
        )

        self.assertIs(service._resolve_data_reader_cls(), FixtureDataReader)

    def test_invalid_data_mode_marks_load_failed(self):
        service = DataCacheService(
            settings=make_settings(data_mode="invalid"),
        )

        service.load()
        snapshot = service.status_snapshot()

        self.assertEqual(snapshot["status"], "failed")
        self.assertFalse(snapshot["ready"])
        self.assertIn("Unsupported CSIT_DATA_MODE", snapshot["last_error"])

    def test_status_snapshot_reports_cache_age(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )

        self.assertIsNone(service.status_snapshot()["cache_age_seconds"])
        service.load()
        cache_age = service.status_snapshot()["cache_age_seconds"]

        self.assertIsInstance(cache_age, float)
        self.assertGreaterEqual(cache_age, 0.0)

    def test_successful_refresh_emits_structured_logs(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )

        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            service.load(started_by="startup")

        events = log_events(logs.records)
        started = next(
            event for event in events
            if event["event"] == "data_refresh_started"
        )
        completed = next(
            event for event in events
            if event["event"] == "data_refresh_completed"
        )
        self.assertEqual(started["started_by"], "startup")
        self.assertEqual(started["status"], "loading")
        self.assertEqual(completed["started_by"], "startup")
        self.assertEqual(completed["status"], "ready")
        self.assertEqual(completed["row_counts"]["statistics"], 1)
        self.assertIsNone(completed["error"])
        self.assertIsInstance(completed["cache_age_seconds"], float)

    def test_failed_and_degraded_refreshes_emit_completion_logs(self):
        failed = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FailingDataReader,
        )
        with self.assertLogs("csit_mcp.observability", level="INFO") as failed_logs:
            failed.load()
        failed_completed = [
            event for event in log_events(failed_logs.records)
            if event["event"] == "data_refresh_completed"
        ][0]
        self.assertEqual(failed_completed["status"], "failed")
        self.assertIn("boom", failed_completed["error"])

        degraded = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )
        degraded.load()
        degraded._data_reader_cls = FailingDataReader
        with self.assertLogs("csit_mcp.observability", level="INFO") as degraded_logs:
            degraded.load()
        degraded_completed = [
            event for event in log_events(degraded_logs.records)
            if event["event"] == "data_refresh_completed"
        ][0]
        self.assertEqual(degraded_completed["status"], "degraded")
        self.assertIn("boom", degraded_completed["error"])

    def test_invalid_configuration_fails_before_reader_construction(self):
        UnexpectedDataReader.constructed = False
        service = DataCacheService(
            settings=make_settings(
                validation_errors=(
                    {
                        "field": "CSIT_TIME_PERIOD",
                        "value": "abc",
                        "message": "expected an integer",
                    },
                ),
            ),
            data_reader_cls=UnexpectedDataReader,
        )

        service.load(started_by="startup")
        snapshot = service.status_snapshot()

        self.assertFalse(UnexpectedDataReader.constructed)
        self.assertEqual(snapshot["status"], "failed")
        self.assertFalse(snapshot["ready"])
        self.assertIn("Invalid CSIT configuration", snapshot["last_error"])
        self.assertIn("CSIT_TIME_PERIOD", snapshot["last_error"])
        self.assertFalse(snapshot["configuration"]["valid"])
        self.assertEqual(
            snapshot["configuration"]["errors"][0]["field"],
            "CSIT_TIME_PERIOD",
        )
        self.assertEqual(len(snapshot["refresh_history"]), 1)
        self.assertEqual(snapshot["refresh_history"][0]["started_by"], "startup")
        self.assertEqual(snapshot["refresh_history"][0]["status"], "failed")

    def test_load_caps_time_period(self):
        service = DataCacheService(
            settings=make_settings(time_period=999, max_time_period=200),
            data_reader_cls=FakeDataReader,
        )

        service.load()

        self.assertEqual(FakeDataReader.last_data_spec_file, "data.yaml")
        self.assertEqual(FakeDataReader.last_days, 200)
        snapshot = service.status_snapshot()
        self.assertEqual(snapshot["status"], "ready")
        self.assertEqual(snapshot["last_refresh_started_by"], "manual")
        self.assertEqual(len(snapshot["refresh_history"]), 1)
        self.assertEqual(snapshot["refresh_history"][0]["started_by"], "manual")
        self.assertEqual(snapshot["refresh_history"][0]["status"], "ready")

    def test_get_parquet_returns_all_and_named_datasets(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )
        service.load()

        all_data = service.get_parquet()
        statistics = service.get_parquet("statistics")
        trending = service.get_parquet("trending")

        self.assertIs(all_data, service.data)
        self.assertEqual(list(statistics["job"]), ["job-a"])
        self.assertEqual(list(trending["test_id"]), ["test-a"])
        self.assertEqual(statistics["start_time"].dtype, object)
        self.assertTrue(service.status_snapshot()["ready"])

    def test_loaded_data_is_normalized_before_ready(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=NormalizationDataReader,
        )

        service.load()
        statistics = service.get_parquet("statistics")
        trending = service.get_parquet("trending")
        snapshot = service.status_snapshot()

        self.assertEqual(service.status, "ready")
        self.assertEqual(
            statistics.loc[0, "start_time"],
            "2026-06-05T08:00:00+00:00",
        )
        self.assertIsNone(trending.loc[0, "start_time"])
        self.assertEqual(str(statistics["build"].dtype), "Int64")
        self.assertEqual(str(trending["passed"].dtype), "boolean")
        self.assertTrue(bool(trending.loc[0, "passed"]))
        self.assertEqual(trending.loc[0, "hosts"], ["2n-skx", "host-a"])
        self.assertEqual(trending.loc[0, "result_receive_rate_rate_avg"], 100.5)
        self.assertEqual(trending.loc[0, "result_receive_rate_rate_unit"], "pps")
        self.assertEqual(int(trending.loc[0, "telemetry_metric_count"]), 1)
        self.assertIsNone(trending.loc[0, "telemetry_decode_error"])
        self.assertIsNone(trending.loc[0, "telemetry_parse_error"])
        self.assertEqual(
            service.get_telemetry("trending").loc[0, "metric_name"],
            "csit_packets_total",
        )
        self.assertEqual(
            service.get_telemetry("trending").loc[0, "value"],
            100.5,
        )
        self.assertIn("datasets", snapshot)
        self.assertEqual(snapshot["datasets"]["statistics"]["status"], "loaded")
        self.assertEqual(snapshot["datasets"]["statistics"]["row_count"], 1)
        self.assertEqual(
            snapshot["datasets"]["statistics"]["normalized_at"],
            snapshot["last_success_at"],
        )
        self.assertEqual(
            snapshot["datasets"]["trending"]["telemetry"]["sample_count"],
            1,
        )
        self.assertEqual(snapshot["telemetry"]["trending"]["sample_count"], 1)
        self.assertEqual(
            snapshot["telemetry"]["trending"]["decode_error_count"],
            0,
        )
        self.assertEqual(
            snapshot["telemetry"]["trending"]["parse_error_count"],
            0,
        )

    def test_get_parquet_does_not_mutate_cached_statistics(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )
        service.load()
        before = service.data["statistics"].copy(deep=True)

        service.get_parquet("statistics")
        service.get_parquet()

        pd.testing.assert_frame_equal(before, service.data["statistics"])

    def test_enabled_optional_empty_data_marks_degraded_but_ready(self):
        service = DataCacheService(
            settings=make_settings(start_coverage=True),
            data_reader_cls=FakeDataReader,
        )

        service.load()
        snapshot = service.status_snapshot()

        self.assertEqual(snapshot["status"], "degraded")
        self.assertTrue(snapshot["ready"])
        self.assertIn("coverage", snapshot["last_error"])
        self.assertEqual(snapshot["row_counts"]["statistics"], 1)
        self.assertEqual(snapshot["datasets"]["coverage"]["status"], "empty")
        self.assertEqual(snapshot["refresh_history"][-1]["status"], "degraded")
        self.assertIn("coverage", snapshot["refresh_history"][-1]["error"])

    def test_unconfigured_optional_data_does_not_mark_degraded(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_spec_file = write_data_spec(
                temp_dir,
                ["statistics", "trending"],
            )
            service = DataCacheService(
                settings=make_settings(
                    data_spec_file=data_spec_file,
                    start_coverage=True,
                    start_report=True,
                ),
                data_reader_cls=UnconfiguredOptionalDataReader,
            )

            service.load()
            snapshot = service.status_snapshot()

        self.assertEqual(snapshot["status"], "ready")
        self.assertTrue(snapshot["ready"])
        self.assertIsNone(snapshot["last_error"])
        self.assertEqual(
            snapshot["datasets"]["iterative"]["status"],
            "not_configured",
        )
        self.assertEqual(
            snapshot["datasets"]["coverage"]["status"],
            "not_configured",
        )

    def test_initial_required_data_failure_marks_failed(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=EmptyRequiredDataReader,
        )

        service.load()
        snapshot = service.status_snapshot()

        self.assertEqual(snapshot["status"], "failed")
        self.assertFalse(snapshot["ready"])
        self.assertEqual(snapshot["refresh_history"][-1]["status"], "failed")
        self.assertIn("statistics", snapshot["refresh_history"][-1]["error"])
        with self.assertRaises(DataUnavailableError):
            service.get_parquet("statistics")

    def test_failed_refresh_preserves_previous_successful_cache(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )
        service.load()
        previous_status = service.status_snapshot()["datasets"]

        service._data_reader_cls = FailingDataReader
        service.load()
        snapshot = service.status_snapshot()
        statistics = service.get_parquet("statistics")

        self.assertEqual(snapshot["status"], "degraded")
        self.assertTrue(snapshot["ready"])
        self.assertIn("boom", snapshot["last_error"])
        self.assertEqual(list(statistics["job"]), ["job-a"])
        self.assertEqual(snapshot["datasets"], previous_status)
        self.assertEqual(len(snapshot["refresh_history"]), 2)
        self.assertEqual(snapshot["refresh_history"][-1]["status"], "degraded")
        self.assertIn("boom", snapshot["refresh_history"][-1]["error"])
        self.assertEqual(
            snapshot["refresh_history"][-1]["row_counts"]["statistics"],
            1,
        )

    def test_successful_refresh_replaces_normalized_cache_and_metadata(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )
        service.load()

        service._data_reader_cls = UpdatedDataReader
        service.load()

        statistics = service.get_parquet("statistics")
        self.assertEqual(list(statistics["job"]), ["job-updated"])

    def test_background_refresh_rejects_concurrent_start(self):
        async def run_refresh():
            service = DataCacheService(
                settings=make_settings(),
                data_reader_cls=SlowDataReader,
            )

            with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
                self.assertTrue(service.start_refresh())
                self.assertFalse(service.start_refresh())

            while service.is_loading:
                await asyncio.sleep(0.01)

            events = log_events(logs.records)
            skipped = next(
                event for event in events
                if event["event"] == "data_refresh_skipped"
            )
            self.assertEqual(skipped["reason"], "already_running")
            self.assertEqual(service.status_snapshot()["status"], "ready")

        asyncio.run(run_refresh())

    def test_result_cache_is_ready_while_telemetry_indexing_continues(self):
        async def run_refresh():
            indexing_started = threading.Event()
            continue_indexing = threading.Event()

            def blocking_index(dataset, data, **kwargs):
                if dataset == "trending":
                    indexing_started.set()
                    continue_indexing.wait(timeout=2)
                return normalize_dataset_telemetry(dataset, data, **kwargs)

            service = DataCacheService(
                settings=make_settings(),
                data_reader_cls=NormalizationDataReader,
            )
            with patch(
                "dashboard.services.data_cache.normalize_dataset_telemetry",
                side_effect=blocking_index,
            ):
                self.assertTrue(service.start_refresh(started_by="startup"))
                while not indexing_started.is_set():
                    await asyncio.sleep(0.01)

                snapshot = service.status_snapshot()
                self.assertTrue(snapshot["ready"])
                self.assertEqual(snapshot["status"], "ready")
                self.assertEqual(
                    snapshot["telemetry"]["trending"]["status"],
                    "indexing",
                )
                self.assertEqual(
                    service.get_parquet("trending").loc[0, "test_id"],
                    "test-a",
                )
                with self.assertRaises(DataUnavailableError):
                    service.get_telemetry("trending")

                continue_indexing.set()
                while service.is_loading:
                    await asyncio.sleep(0.01)

            self.assertEqual(
                service.status_snapshot()["telemetry"]["trending"]["status"],
                "ready",
            )

        asyncio.run(run_refresh())

    def test_refresh_history_is_capped_to_recent_attempts(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )

        for index in range(12):
            service.load(started_by=f"manual-{index}")

        snapshot = service.status_snapshot()
        history = snapshot["refresh_history"]

        self.assertEqual(len(history), 10)
        self.assertEqual(history[0]["started_by"], "manual-2")
        self.assertEqual(history[-1]["started_by"], "manual-11")

    def test_background_refresh_records_source_and_single_history_entry(self):
        async def run_refresh():
            service = DataCacheService(
                settings=make_settings(),
                data_reader_cls=SlowDataReader,
            )

            self.assertTrue(service.start_refresh(started_by="manual"))
            self.assertFalse(service.start_refresh(started_by="manual"))

            while service.is_loading:
                await asyncio.sleep(0.01)

            snapshot = service.status_snapshot()
            self.assertEqual(snapshot["last_refresh_started_by"], "manual")
            self.assertEqual(len(snapshot["refresh_history"]), 1)
            self.assertEqual(snapshot["refresh_history"][0]["started_by"], "manual")
            self.assertEqual(snapshot["refresh_history"][0]["status"], "ready")

        asyncio.run(run_refresh())

    def test_fixture_mode_loads_ready_cache(self):
        service = DataCacheService(
            settings=make_settings(data_mode="fixture"),
        )

        service.load()
        snapshot = service.status_snapshot()

        self.assertEqual(snapshot["status"], "ready")
        self.assertTrue(snapshot["ready"])
        self.assertEqual(snapshot["row_counts"]["statistics"], 1)
        self.assertEqual(snapshot["row_counts"]["trending"], 7)
        self.assertEqual(snapshot["row_counts"]["iterative"], 3)
        self.assertEqual(snapshot["row_counts"]["coverage"], 2)
        self.assertEqual(snapshot["datasets"]["coverage"]["status"], "loaded")
        self.assertGreater(snapshot["telemetry"]["trending"]["sample_count"], 0)
        self.assertGreater(snapshot["telemetry"]["iterative"]["sample_count"], 0)

    @unittest.skipIf(pa is None, "pyarrow is not available")
    def test_arrow_list_hosts_are_normalized_at_cache_boundary(self):
        class ArrowHostsDataReader:
            def __init__(self, data_spec_file):
                self.data_spec_file = data_spec_file

            def read_all_data(self, days=None):
                hosts = pa.array(
                    [["10.30.51.83", "10.30.51.84"]],
                    type=pa.list_(pa.string()),
                )
                trending = pa.table(
                    {
                        "test_id": ["arrow-test"],
                        "hosts": hosts,
                        "build": [1],
                        "passed": [True],
                    }
                ).to_pandas(types_mapper=pd.ArrowDtype)
                data = make_frames()
                data["trending"] = trending
                return data

        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=ArrowHostsDataReader,
        )
        service.load()

        trending = service.get_parquet("trending")

        self.assertEqual(
            trending.loc[0, "hosts"],
            ["10.30.51.83", "10.30.51.84"],
        )
        self.assertIsInstance(trending.loc[0, "hosts"], list)


class FixtureDataReaderTests(unittest.TestCase):
    def test_loads_all_fixture_datasets(self):
        data = FixtureDataReader(data_spec_file="ignored").read_all_data()

        self.assertEqual(
            set(data),
            {"statistics", "trending", "iterative", "coverage"},
        )
        self.assertEqual(len(data["statistics"]), 2)
        self.assertEqual(len(data["trending"]), 8)
        self.assertEqual(len(data["iterative"]), 3)
        self.assertEqual(len(data["coverage"]), 2)
        self.assertEqual(
            data["iterative"].loc[0, "hosts"],
            ["2n-skx", "host-a"],
        )

    def test_days_filter_only_applies_to_statistics_and_trending(self):
        data = FixtureDataReader(data_spec_file="ignored").read_all_data(days=15)

        self.assertEqual(len(data["statistics"]), 1)
        self.assertEqual(len(data["trending"]), 7)
        self.assertEqual(len(data["iterative"]), 3)
        self.assertEqual(len(data["coverage"]), 2)


if __name__ == "__main__":
    unittest.main()
