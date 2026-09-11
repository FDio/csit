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
        cache_snapshot_path="",
        refresh_memory_limit_percent=85,
        snapshot_refresh_max_age_seconds=0,
        refresh_worker_timeout_seconds=1800,
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
        cache_snapshot_path=cache_snapshot_path,
        refresh_memory_limit_percent=refresh_memory_limit_percent,
        snapshot_refresh_max_age_seconds=snapshot_refresh_max_age_seconds,
        refresh_worker_timeout_seconds=refresh_worker_timeout_seconds,
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
                    "result_latency_forward_pdr_50_hdrh": ["HIST-encoded"],
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


class StagedDataReader:
    optional_started = threading.Event()
    optional_release = threading.Event()
    calls = []

    def __init__(self, data_spec_file):
        self.data_spec_file = data_spec_file

    def read_all_data(self, days=None, data_types=None):
        selected = tuple(data_types or ())
        self.__class__.calls.append(selected)
        data = make_frames()
        if selected == ("statistics", "trending"):
            return {key: data[key] for key in selected}
        self.__class__.optional_started.set()
        self.__class__.optional_release.wait(timeout=5)
        return {key: data[key] for key in selected}


class DataCacheServiceTests(unittest.TestCase):
    def test_staged_reader_publishes_required_data_before_optional_load(self):
        StagedDataReader.optional_started.clear()
        StagedDataReader.optional_release.clear()
        StagedDataReader.calls = []
        cache = DataCacheService(
            settings=make_settings(),
            data_reader_cls=StagedDataReader,
        )
        load_thread = threading.Thread(
            target=cache.load,
            kwargs={"started_by": "startup"},
        )

        load_thread.start()
        self.assertTrue(StagedDataReader.optional_started.wait(timeout=2))
        self.assertTrue(cache.is_serving_ready)
        self.assertEqual(cache.status, "degraded")
        self.assertEqual(cache.status_snapshot()["row_counts"]["statistics"], 1)
        self.assertEqual(cache.status_snapshot()["row_counts"]["trending"], 1)
        StagedDataReader.optional_release.set()
        load_thread.join(timeout=5)

        self.assertFalse(load_thread.is_alive())
        self.assertEqual(
            StagedDataReader.calls,
            [("statistics", "trending"), ("iterative", "coverage")],
        )
        self.assertEqual(cache.status, "ready")

    def test_s3_reader_retries_transient_stream_failure(self):
        expected = pd.DataFrame({"value": [1]})
        with (
            patch(
                "dashboard.data.data.wr.s3.read_parquet",
                side_effect=[OSError("connection reset"), expected],
            ) as read_parquet,
            patch("dashboard.data.data.sleep") as retry_sleep,
        ):
            actual = Data._create_dataframe_from_parquet("s3://example/data")

        self.assertEqual(read_parquet.call_count, 2)
        retry_sleep.assert_called_once()
        pd.testing.assert_frame_equal(actual, expected)

    def test_persists_and_restores_last_successful_cache_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_path = str(Path(directory) / "snapshot")
            settings = make_settings(cache_snapshot_path=snapshot_path)
            writer = DataCacheService(
                settings=settings,
                data_reader_cls=FakeDataReader,
            )
            writer.load(started_by="startup")
            manifest = json.loads(
                (Path(snapshot_path) / "manifest.json").read_text()
            )

            self.assertEqual(manifest["format_version"], 2)
            self.assertTrue(manifest["generation_id"])
            self.assertIn("statistics.parquet", manifest["files"])
            self.assertTrue(
                manifest["files"]["statistics.parquet"]["schema_sha256"]
            )

            restored = DataCacheService(
                settings=settings,
                data_reader_cls=FailingDataReader,
            )
            self.assertTrue(restored.restore_snapshot())
            self.assertTrue(restored.is_serving_ready)
            self.assertEqual(restored.status, "degraded")
            self.assertEqual(
                restored.get_parquet("statistics").iloc[0]["job"],
                "job-a",
            )
            self.assertIsNotNone(
                restored.status_snapshot()["snapshot"]["restored_at"]
            )
            self.assertEqual(
                restored.status_snapshot()["snapshot"]["generation_id"],
                manifest["generation_id"],
            )

            self.assertTrue(restored._begin_load(started_by="startup"))
            self.assertEqual(restored.status, "degraded")
            self.assertTrue(restored.is_serving_ready)
            with restored._lock:
                restored._is_loading = False

            restored.load(started_by="startup")
            self.assertEqual(restored.status, "degraded")
            self.assertTrue(restored.is_serving_ready)
            self.assertEqual(
                restored.get_parquet("statistics").iloc[0]["job"],
                "job-a",
            )

    def test_corrupt_snapshot_falls_back_to_previous_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_path = Path(directory) / "snapshot"
            settings = make_settings(cache_snapshot_path=str(snapshot_path))
            DataCacheService(
                settings=settings,
                data_reader_cls=FakeDataReader,
            ).load(started_by="startup")
            first_manifest = json.loads(
                (snapshot_path / "manifest.json").read_text()
            )
            DataCacheService(
                settings=settings,
                data_reader_cls=UpdatedDataReader,
            ).load(started_by="manual")
            (snapshot_path / "statistics.parquet").write_bytes(b"corrupt")

            restored = DataCacheService(
                settings=settings,
                data_reader_cls=FailingDataReader,
            )

            self.assertTrue(restored.restore_snapshot())
            self.assertEqual(
                restored.get_parquet("statistics").iloc[0]["job"],
                "job-a",
            )
            self.assertEqual(
                restored.status_snapshot()["snapshot"]["generation_id"],
                first_manifest["generation_id"],
            )

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

    def test_status_snapshot_reports_component_memory(self):
        service = DataCacheService(
            settings=make_settings(),
            data_reader_cls=FakeDataReader,
        )
        service.load()

        memory = service.status_snapshot()["memory"]

        self.assertIn("cgroup", memory)
        self.assertGreater(memory["cache"]["estimated_bytes"], 0)
        self.assertIn("statistics", memory["cache"]["result_data"]["datasets"])

    def test_refresh_is_rejected_without_memory_headroom(self):
        service = DataCacheService(
            settings=make_settings(refresh_memory_limit_percent=85),
            data_reader_cls=FakeDataReader,
        )
        service.load()

        with patch(
            "dashboard.services.data_cache.cgroup_memory_status",
            return_value={
                "current_bytes": 90_000_000,
                "max_bytes": 100_000_000,
                "used_percent": 90.0,
                "events": {},
            },
        ):
            started = service._begin_load(started_by="manual")

        self.assertFalse(started)
        self.assertEqual(
            service.status_snapshot()["last_refresh_skip_reason"],
            "insufficient_memory_headroom",
        )

    def test_fresh_snapshot_can_skip_immediate_remote_refresh(self):
        service = DataCacheService(
            settings=make_settings(snapshot_refresh_max_age_seconds=60),
            data_reader_cls=FakeDataReader,
        )
        service.load()

        self.assertFalse(service.should_refresh_after_restore())
        self.assertEqual(
            service.status_snapshot()["last_refresh_skip_reason"],
            "snapshot_within_freshness_window",
        )

    def test_s3_snapshot_mode_uses_refresh_worker(self):
        service = DataCacheService(
            settings=make_settings(cache_snapshot_path="/tmp/csit-test-snapshot"),
        )

        self.assertTrue(service._uses_refresh_worker())
        service._data_reader_cls = FakeDataReader
        self.assertFalse(service._uses_refresh_worker())

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
        self.assertIn("cache", started["memory"])
        self.assertEqual(completed["started_by"], "startup")
        self.assertEqual(completed["status"], "ready")
        self.assertEqual(completed["row_counts"]["statistics"], 1)
        self.assertIsNone(completed["error"])
        self.assertIsInstance(completed["cache_age_seconds"], float)
        self.assertIn("cgroup", completed["memory"])

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
        self.assertIn("timestamp", str(statistics["start_time"].dtype))
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
            statistics.loc[0, "start_time"].isoformat(),
            "2026-06-05T08:00:00+00:00",
        )
        self.assertTrue(pd.isna(trending.loc[0, "start_time"]))
        self.assertEqual(str(statistics["build"].dtype), "Int64")
        self.assertEqual(str(trending["passed"].dtype), "boolean")
        self.assertTrue(bool(trending.loc[0, "passed"]))
        self.assertEqual(trending.loc[0, "hosts"], ["2n-skx", "host-a"])
        self.assertEqual(trending.loc[0, "result_receive_rate_rate_avg"], 100.5)
        self.assertEqual(trending.loc[0, "result_receive_rate_rate_unit"], "pps")
        self.assertEqual(
            trending.loc[0, "result_latency_forward_pdr_50_hdrh"],
            "HIST-encoded",
        )
        self.assertNotIn("telemetry", trending.columns)
        self.assertEqual(len(service.get_raw_telemetry("trending")), 1)
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
        self.assertEqual(
            snapshot["telemetry_source"]["trending"]["raw_row_count"],
            1,
        )

    @unittest.skipIf(pa is None, "pyarrow is required")
    def test_snapshot_reader_ignores_legacy_arrow_dictionary_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            dictionary = pa.array(["vpp", "vpp", "dpdk"]).dictionary_encode()
            data = pd.DataFrame({
                "dut_type": pd.Series(
                    dictionary,
                    dtype=pd.ArrowDtype(dictionary.type),
                )
            })
            path = Path(directory) / "legacy.parquet"
            data.to_parquet(path, index=False)

            restored = DataCacheService._read_snapshot_frame(path)

        self.assertEqual(list(restored["dut_type"]), ["vpp", "vpp", "dpdk"])

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
        self.assertEqual(snapshot["row_counts"]["iterative"], 16)
        self.assertEqual(snapshot["row_counts"]["coverage"], 5)
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
        self.assertEqual(len(data["iterative"]), 16)
        self.assertEqual(len(data["coverage"]), 5)
        self.assertEqual(
            data["iterative"].loc[0, "hosts"],
            ["10.30.0.1", "10.30.0.2"],
        )

    def test_days_filter_only_applies_to_statistics_and_trending(self):
        data = FixtureDataReader(data_spec_file="ignored").read_all_data(days=15)

        self.assertEqual(len(data["statistics"]), 1)
        self.assertEqual(len(data["trending"]), 7)
        self.assertEqual(len(data["iterative"]), 16)
        self.assertEqual(len(data["coverage"]), 5)


if __name__ == "__main__":
    unittest.main()
