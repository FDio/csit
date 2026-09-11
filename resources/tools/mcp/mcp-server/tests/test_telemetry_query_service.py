import base64
from concurrent.futures import ThreadPoolExecutor
import json
import time
import unittest
import zlib

from dashboard.services.telemetry_query import TelemetryQueryService
from dashboard.services.telemetry_locator import (
    build_telemetry_locator,
    raw_telemetry_frame,
    telemetry_catalog_payload,
)
from dashboard.services.data_cache import DataCacheService
from dashboard.services.trending import TrendingService
from dashboard.settings import get_settings
from dashboard.data.fixture_data import FixtureDataReader
from tests.test_trending_service import STATUS, trending_data


def encoded_runtime(value, *, node="p4-lookup", hostname="10.0.0.1"):
    text = (
        "vpp.runtime.clocks{hostname=" + hostname + ",hook=poll,rate=scalar,"
        "node_name=" + node + ",state=active} " + str(value) + "\n"
        "vpp.runtime.clocks{hostname=" + hostname + ",hook=poll,rate=scalar,"
        "node_name=unrelated,state=active} 999\n"
    )
    return base64.b64encode(zlib.compress(text.encode())).decode()


def encoded_production_metrics(
        direct_value=101.0,
        runtime_value=202.0,
        *,
        node="p4-lookup",
        state="active",
        threads=("1",),
    ):
    lines = []
    for thread_id in threads:
        labels = (
            "hostname='sut1',hook='DUT1',rate='mrr',"
            f"node_name='{node}',thread_id='{thread_id}',"
            f"thread_name='vpp_wk_{thread_id}'"
        )
        if direct_value is not None:
            lines.append(
                "vpp.inst_and_clock.clocks_per_packets{"
                f"{labels}}} {direct_value}\n"
            )
        if runtime_value is not None:
            lines.append(
                "vpp.runtime.clocks{"
                f"{labels},state='{state}'}} {runtime_value}\n"
            )
    return base64.b64encode(
        zlib.compress("".join(lines).encode())
    ).decode()


class TelemetryQueryServiceTests(unittest.TestCase):
    def setUp(self):
        self.data = trending_data().iloc[:2].copy()
        self.data["telemetry"] = [
            [encoded_runtime(101.0)],
            [encoded_runtime(111.0)],
        ]
        self.settings = get_settings(environ={
            "CSIT_TIME_PERIOD": "200",
            "CSIT_TELEMETRY_QUERY_MAX_CONCURRENT": "1",
            "CSIT_TELEMETRY_QUERY_QUEUE_TIMEOUT_SECONDS": "1",
            "CSIT_TELEMETRY_QUERY_TIMEOUT_SECONDS": "30",
            "CSIT_TELEMETRY_QUERY_MAX_SOURCE_ROWS": "20",
            "CSIT_TELEMETRY_QUERY_MAX_SAMPLES": "100",
            "CSIT_TELEMETRY_QUERY_CACHE_ENTRIES": "8",
        })
        self.trending = TrendingService()
        catalog = self.trending.catalog_payload(
            self.data, STATUS, select_defaults=True
        )
        self.series_id = catalog["records"][0]["series_id"]
        self.service = TelemetryQueryService(
            settings=self.settings,
            trending_service=self.trending,
        )

    def query(self, **overrides):
        arguments = {
            "dataset": "trending",
            "series": [self.series_id],
            "metric": "cycles_per_packet",
            "node_names": ["p4-lookup"],
            "testbed": "10.0.0.1",
            "days": 30,
            "start_time": "2026-08-01T00:00:00+00:00",
            "end_time": "2026-08-31T23:59:59+00:00",
            "passed": True,
            "aggregation": "per_run",
            "offset": 0,
            "limit": 100,
        }
        arguments.update(overrides)
        return self.service.timeseries_payload(
            self.data, STATUS, **arguments
        )

    def test_targeted_query_uses_authoritative_source_rows(self):
        payload = self.query()

        self.assertNotIn("error", payload)
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(
            [record["value"] for record in payload["records"]],
            [101, 111],
        )
        self.assertEqual(payload["records"][0]["unit"], "cycles/packet")
        self.assertEqual(payload["records"][0]["node_name"], "p4-lookup")
        self.assertTrue(payload["completeness"]["complete"])
        self.assertFalse(
            payload["completeness"]["representative_index_used"]
        )
        self.assertEqual(
            payload["completeness"]["decoded_source_row_count"], 2
        )

    def test_production_labels_are_canonical_and_direct_metric_wins(self):
        self.data["telemetry"] = [
            [encoded_production_metrics(101.0, 201.0)],
            [encoded_production_metrics(111.0, 211.0)],
        ]

        payload = self.query()

        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(
            [record["value"] for record in payload["records"]],
            [101, 111],
        )
        self.assertEqual(
            {record["source_metric"] for record in payload["records"]},
            {"vpp.inst_and_clock.clocks_per_packets"},
        )
        self.assertEqual(payload["records"][0]["node_name"], "p4-lookup")
        self.assertEqual(payload["records"][0]["hostname"], "sut1")
        self.assertEqual(payload["records"][0]["thread_id"], "1")
        selection = payload["completeness"]["selection"]
        self.assertEqual(selection["parsed_source_metric_sample_count"], 4)
        self.assertEqual(selection["node_matched_sample_count"], 4)
        self.assertEqual(selection["semantic_policy_matched_sample_count"], 4)

    def test_runtime_fallback_keeps_only_active_samples(self):
        self.data["telemetry"] = [
            [encoded_production_metrics(None, 201.0, state="active")],
            [encoded_production_metrics(None, 999.0, state="any wait")],
        ]

        payload = self.query()

        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["records"][0]["value"], 201)
        self.assertEqual(payload["records"][0]["source_metric"], (
            "vpp.runtime.clocks"
        ))

    def test_semantic_records_preserve_thread_identity(self):
        self.data = self.data.iloc[:1].copy()
        self.data["telemetry"] = [[encoded_production_metrics(
            101.0, None, threads=("1", "2")
        )]]

        payload = self.query()

        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(
            [record["thread_id"] for record in payload["records"]],
            ["1", "2"],
        )

    def test_empty_result_reports_the_filtering_stage(self):
        self.data["telemetry"] = [
            [encoded_production_metrics(None, 201.0, state="any wait")],
            [encoded_production_metrics(None, 211.0, state="any wait")],
        ]

        missing_node = self.query(node_names=["missing-node"])
        policy_mismatch = self.query(node_names=[], metric="cycles_per_packet")
        no_source_metric = self.query(
            node_names=[], metric="missing.metric"
        )
        no_source_rows = self.query(
            start_time="2025-01-01T00:00:00+00:00",
            end_time="2025-01-31T00:00:00+00:00",
        )

        self.assertIn(
            "requested_nodes_not_found",
            missing_node["completeness"]["reasons"],
        )
        self.assertIn(
            "p4-lookup",
            missing_node["completeness"]["selection"][
                "available_node_names"
            ],
        )
        self.assertIn(
            "semantic_label_policy_no_match",
            policy_mismatch["completeness"]["reasons"],
        )
        self.assertIn(
            "source_metric_not_found",
            no_source_metric["completeness"]["reasons"],
        )
        self.assertIn(
            "no_source_rows_in_window",
            no_source_rows["completeness"]["reasons"],
        )

    def test_daily_mean_and_pagination_are_compact(self):
        payload = self.query(aggregation="daily_mean", limit=1)

        self.assertEqual(payload["returned_count"], 1)
        self.assertTrue(payload["has_more"])
        self.assertEqual(payload["next_offset"], 1)
        self.assertEqual(payload["records"][0]["sample_count"], 1)

    def test_invalid_and_oversized_queries_do_not_return_partial_data(self):
        invalid = self.query(dataset="iterative", passed=False)
        limited_settings = get_settings(environ={
            "CSIT_TELEMETRY_QUERY_MAX_SOURCE_ROWS": "1",
        })
        limited = TelemetryQueryService(
            settings=limited_settings,
            trending_service=self.trending,
        ).timeseries_payload(
            self.data,
            STATUS,
            dataset="trending",
            series=[self.series_id],
            metric="cycles_per_packet",
            start_time="2026-08-01T00:00:00+00:00",
            end_time="2026-08-31T23:59:59+00:00",
        )

        self.assertEqual(invalid["error"], "validation_error")
        self.assertEqual(limited["error"], "query_too_large")
        self.assertEqual(limited["resource"], "source_rows")
        self.assertNotIn("records", limited)

    def test_repeated_query_uses_generation_cache(self):
        first = self.query()
        second = self.query()

        self.assertFalse(first["query_cache_hit"])
        self.assertTrue(second["query_cache_hit"])

    def test_locator_query_does_not_build_full_trending_index(self):
        class ExplodingTrendingService:
            def telemetry_source_matches(self, *args, **kwargs):
                raise AssertionError("full Trending index must not be used")

        source_data = self.data.copy(deep=False)
        telemetry_source = raw_telemetry_frame(source_data)
        locator = build_telemetry_locator(source_data, telemetry_source)
        service = TelemetryQueryService(
            settings=self.settings,
            trending_service=ExplodingTrendingService(),
        )

        payload = service.timeseries_payload(
            source_data,
            STATUS,
            telemetry_source=telemetry_source,
            telemetry_locator=locator,
            dataset="trending",
            series=[self.series_id],
            metric="cycles_per_packet",
            node_names=["p4-lookup"],
            testbed="10.0.0.1",
            start_time="2026-08-01T00:00:00+00:00",
            end_time="2026-08-31T23:59:59+00:00",
        )

        self.assertNotIn("error", payload)
        self.assertEqual(payload["row_count"], 2)

    def test_encoded_and_decoded_byte_budgets_return_no_partial_data(self):
        encoded_limited = TelemetryQueryService(
            settings=get_settings(environ={
                "CSIT_TIME_PERIOD": "200",
                "CSIT_TELEMETRY_QUERY_MAX_ENCODED_BYTES": "1",
            }),
        ).timeseries_payload(
            self.data,
            STATUS,
            dataset="trending",
            series=[self.series_id],
            metric="cycles_per_packet",
            start_time="2026-08-01T00:00:00+00:00",
            end_time="2026-08-31T23:59:59+00:00",
        )
        decoded_limited = TelemetryQueryService(
            settings=get_settings(environ={
                "CSIT_TIME_PERIOD": "200",
                "CSIT_TELEMETRY_QUERY_MAX_DECODED_BYTES": "8",
            }),
        ).timeseries_payload(
            self.data,
            STATUS,
            dataset="trending",
            series=[self.series_id],
            metric="cycles_per_packet",
            start_time="2026-08-01T00:00:00+00:00",
            end_time="2026-08-31T23:59:59+00:00",
        )

        self.assertEqual(encoded_limited["resource"], "encoded_bytes")
        self.assertEqual(decoded_limited["resource"], "decoded_bytes")
        self.assertNotIn("records", encoded_limited)
        self.assertNotIn("records", decoded_limited)

    def test_fixture_data_supports_targeted_cycles_query_without_s3(self):
        data = FixtureDataReader(
            data_spec_file="ignored"
        ).read_all_data()["trending"]
        trending = TrendingService()
        catalog = trending.catalog_payload(
            data,
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
        service = TelemetryQueryService(
            settings=self.settings,
            trending_service=trending,
        )

        payload = service.timeseries_payload(
            data,
            STATUS,
            dataset="trending",
            series=[catalog["records"][0]["series_id"]],
            metric="cycles_per_packet",
            node_names=["p4-lookup", "ip6-lookup"],
            start_time="2099-01-01T00:00:00+00:00",
            end_time="2099-01-31T23:59:59+00:00",
        )

        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(
            {record["node_name"]: record["value"] for record in payload["records"]},
            {"p4-lookup": 101, "ip6-lookup": 121},
        )

    def test_fixture_cache_sidecar_supports_catalog_then_timeseries(self):
        settings = get_settings(environ={
            "CSIT_DATA_MODE": "fixture",
            "CSIT_TIME_PERIOD": "200",
        })
        cache = DataCacheService(settings=settings)
        cache.load(started_by="startup")
        locator = cache.get_telemetry_locator("trending")
        catalog = telemetry_catalog_payload(
            locator,
            cache.status_snapshot(),
            filters={
                "dut": "vpp",
                "area": "ip4_tunnels",
                "test": "ethip4geneve",
                "infra": "2n-skx-100ge2p1e810cq-avf",
            },
        )
        payload = TelemetryQueryService(settings=settings).timeseries_payload(
            cache.get_parquet("trending"),
            cache.status_snapshot(),
            telemetry_source=cache.get_raw_telemetry("trending"),
            telemetry_locator=locator,
            dataset="trending",
            series=[catalog["records"][0]["series_id"]],
            metric="cycles_per_packet",
            node_names=["p4-lookup", "ip6-lookup"],
            start_time="2099-01-01T00:00:00+00:00",
            end_time="2099-01-31T23:59:59+00:00",
        )

        self.assertNotIn("telemetry", cache.get_parquet("trending").columns)
        self.assertEqual(payload["row_count"], 2)

    def test_legacy_gate_rejects_concurrent_work_instead_of_overlapping(self):
        entered = []

        def slow_callback():
            entered.append(True)
            time.sleep(1.2)
            return {"ok": True}

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(
                self.service.run_guarded_diagnostic,
                "telemetry_metrics", "trending", slow_callback,
            )
            while not entered:
                time.sleep(0.01)
            second = executor.submit(
                self.service.run_guarded_diagnostic,
                "telemetry_metrics", "trending", lambda: {"second": True},
            )
            second_result = second.result()
            first_result = first.result()

        self.assertEqual(first_result, {"ok": True})
        self.assertEqual(second_result["error"], "server_busy")


if __name__ == "__main__":
    unittest.main()
