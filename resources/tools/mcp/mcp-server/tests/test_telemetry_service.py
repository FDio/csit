import base64
import unittest
import zlib

import pandas as pd

from dashboard.services.telemetry import (
    decode_telemetry_cell,
    normalize_dataset_telemetry,
    parse_openmetrics,
    telemetry_anomalies_payload,
    telemetry_metric_values_payload,
    telemetry_metrics_payload,
    telemetry_trend_summary_payload,
)


STATUS = {
    "status": "ready",
    "last_success_at": "2026-06-05T09:30:00+00:00",
}


def encoded(text: str) -> str:
    return base64.b64encode(zlib.compress(text.encode())).decode()


def telemetry_text(value: float = 100.0, *, worker: str = "0") -> str:
    return (
        "# HELP csit_packets_total Packets observed\n"
        "# TYPE csit_packets_total counter\n"
        "# UNIT csit_packets_total packets\n"
        f"csit_packets_total{{worker=\"{worker}\",direction=\"rx\"}} {value} "
        "1760000000\n"
        "csit_latency_seconds{quantile=\"0.50\"} 0.001\n"
        "# EOF\n"
    )


def csit_telemetry_text(value: float = 42.0) -> str:
    return (
        "vpp.runtime.calls{hostname=host-a,hook=poll,rate=scalar,"
        f"node_name=ip4-input,state=active}} {value}\n"
    )


def make_source_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "job": ["job-a", "job-a", "job-a", "job-b"],
            "build": [1, 2, 3, 4],
            "start_time": [
                "2026-06-01T00:00:00+00:00",
                "2026-06-02T00:00:00+00:00",
                "2026-06-03T00:00:00+00:00",
                "2026-06-04T00:00:00+00:00",
            ],
            "test_type": ["mrr", "mrr", "mrr", "ndrpdr"],
            "dut_type": ["vpp", "vpp", "vpp", "dpdk"],
            "hosts": [
                ["2n-skx", "host-a"],
                ["2n-skx", "host-a"],
                ["3n-alt", "host-b"],
                ["3n-alt", "host-b"],
            ],
            "test_id": ["test-a", "test-a", "test-a", "test-b"],
            "passed": [True, True, False, True],
            "telemetry": [
                [encoded(telemetry_text(100.0))],
                [encoded(telemetry_text(130.0))],
                [encoded(telemetry_text(400.0, worker="1"))],
                [encoded(telemetry_text(80.0))],
            ],
        }
    )


class TelemetryDecodeParseTests(unittest.TestCase):
    def test_decodes_list_backed_base64_zlib_telemetry(self):
        decoded = decode_telemetry_cell([encoded(telemetry_text())])

        self.assertFalse(decoded.errors)
        self.assertIn("csit_packets_total", decoded.text)

    def test_decode_error_is_reported_without_raising(self):
        decoded = decode_telemetry_cell(["not-base64"])

        self.assertFalse(decoded.text)
        self.assertEqual(len(decoded.errors), 1)
        self.assertIn("decode[0]", decoded.errors[0])

    def test_parses_openmetrics_samples_and_metadata(self):
        parsed = parse_openmetrics(telemetry_text())

        self.assertFalse(parsed.errors)
        self.assertEqual(len(parsed.samples), 2)
        packet_sample = parsed.samples[0]
        self.assertEqual(packet_sample["metric_name"], "csit_packets_total")
        self.assertEqual(packet_sample["labels"]["direction"], "rx")
        self.assertEqual(packet_sample["label_key"], "direction=rx,worker=0")
        self.assertEqual(packet_sample["type"], "counter")
        self.assertEqual(packet_sample["unit"], "packets")
        self.assertEqual(packet_sample["help"], "Packets observed")
        self.assertEqual(packet_sample["value"], 100.0)
        self.assertEqual(packet_sample["timestamp"], "1760000000")

    def test_parses_csit_unquoted_label_values(self):
        parsed = parse_openmetrics(csit_telemetry_text())

        self.assertFalse(parsed.errors)
        self.assertEqual(len(parsed.samples), 1)
        sample = parsed.samples[0]
        self.assertEqual(sample["metric_name"], "vpp.runtime.calls")
        self.assertEqual(sample["labels"]["hostname"], "host-a")
        self.assertEqual(sample["labels"]["node_name"], "ip4-input")
        self.assertEqual(sample["label_key"], (
            "hook=poll,hostname=host-a,node_name=ip4-input,"
            "rate=scalar,state=active"
        ))
        self.assertEqual(sample["value"], 42.0)

    def test_parses_csit_single_quoted_label_values(self):
        parsed = parse_openmetrics(
            "vpp.runtime.clocks{hostname='sut1',hook='DUT1',rate='mrr',"
            "node_name='ip4-lookup',state='active',thread_name='worker,0'} "
            "46.6\n"
        )

        self.assertFalse(parsed.errors)
        sample = parsed.samples[0]
        self.assertEqual(sample["labels"]["hostname"], "sut1")
        self.assertEqual(sample["labels"]["hook"], "DUT1")
        self.assertEqual(sample["labels"]["rate"], "mrr")
        self.assertEqual(sample["labels"]["node_name"], "ip4-lookup")
        self.assertEqual(sample["labels"]["state"], "active")
        self.assertEqual(sample["labels"]["thread_name"], "worker,0")
        self.assertNotIn("'", sample["label_key"])

    def test_rejects_empty_and_malformed_label_values(self):
        empty = parse_openmetrics("metric{label=} 1\n")
        mismatched = parse_openmetrics('metric{label="value} 1\n')

        self.assertIn("must not be empty", empty.errors[0])
        self.assertTrue(mismatched.errors)


class TelemetryPayloadTests(unittest.TestCase):
    def test_normalizes_source_rows_and_builds_metric_dataframe(self):
        normalized, telemetry_data, telemetry_status = normalize_dataset_telemetry(
            "trending",
            make_source_data(),
        )

        self.assertIn("telemetry_metric_count", normalized.columns)
        self.assertIn("telemetry_decode_error", normalized.columns)
        self.assertIn("telemetry_parse_error", normalized.columns)
        self.assertEqual(int(normalized.loc[0, "telemetry_metric_count"]), 2)
        self.assertEqual(len(telemetry_data), 8)
        self.assertEqual(telemetry_data.loc[0, "source_dataset"], "trending")
        self.assertEqual(telemetry_data.loc[0, "hosts"], ["2n-skx", "host-a"])
        self.assertEqual(telemetry_status["sample_count"], 8)
        self.assertEqual(telemetry_status["metric_name_count"], 2)
        self.assertEqual(telemetry_status["status"], "ready")
        self.assertFalse(telemetry_status["truncated"])
        self.assertEqual(telemetry_status["decode_error_count"], 0)
        self.assertEqual(telemetry_status["parse_error_count"], 0)

    def test_reports_decode_and_parse_errors_separately(self):
        source = pd.DataFrame(
            {
                "telemetry": [
                    ["not-base64"],
                    [encoded("metric{label=} 1\n")],
                    [encoded(csit_telemetry_text())],
                ],
            }
        )

        normalized, telemetry_data, telemetry_status = (
            normalize_dataset_telemetry("trending", source)
        )

        self.assertIn("decode[0]", normalized.loc[0, "telemetry_decode_error"])
        self.assertIsNone(normalized.loc[0, "telemetry_parse_error"])
        self.assertIsNone(normalized.loc[1, "telemetry_decode_error"])
        self.assertIn(
            "label value must not be empty",
            normalized.loc[1, "telemetry_parse_error"],
        )
        self.assertEqual(len(telemetry_data), 1)
        self.assertEqual(telemetry_status["rows_with_errors"], 2)
        self.assertEqual(telemetry_status["rows_with_decode_errors"], 1)
        self.assertEqual(telemetry_status["rows_with_parse_errors"], 1)
        self.assertEqual(telemetry_status["decode_error_count"], 1)
        self.assertEqual(telemetry_status["parse_error_count"], 1)

    def test_telemetry_index_is_bounded_and_representative(self):
        normalized, telemetry_data, telemetry_status = normalize_dataset_telemetry(
            "trending",
            make_source_data(),
            max_source_rows=2,
            max_samples=2,
        )

        self.assertEqual(len(telemetry_data), 2)
        self.assertEqual(telemetry_status["status"], "partial")
        self.assertTrue(telemetry_status["truncated"])
        self.assertEqual(telemetry_status["source_row_count"], 4)
        self.assertEqual(telemetry_status["indexed_row_count"], 2)
        self.assertEqual(
            telemetry_status["limits"],
            {"max_source_rows": 2, "max_samples": 2},
        )
        self.assertEqual(
            int(normalized["telemetry_metric_count"].notna().sum()),
            2,
        )

    def test_metric_payload_filters_and_pages_samples(self):
        _normalized, telemetry_data, _status = normalize_dataset_telemetry(
            "trending",
            make_source_data(),
        )

        payload = telemetry_metrics_payload(
            dataset="trending",
            data=telemetry_data,
            status=STATUS,
            metric_name="csit_packets_total",
            hosts="2n-skx",
            limit=1,
            offset=0,
        )

        self.assertEqual(payload["dataset"], "trending")
        self.assertTrue(payload["telemetry"])
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(payload["returned_count"], 1)
        self.assertTrue(payload["has_more"])
        self.assertEqual(payload["next_offset"], 1)
        self.assertEqual(payload["records"][0]["metric_name"], "csit_packets_total")

    def test_metric_payload_marks_index_as_representative(self):
        _normalized, telemetry_data, telemetry_status = (
            normalize_dataset_telemetry(
                "trending", make_source_data(), max_source_rows=2
            )
        )
        status = {
            **STATUS,
            "telemetry": {"trending": telemetry_status},
        }

        payload = telemetry_metrics_payload(
            dataset="trending",
            data=telemetry_data,
            status=status,
            limit=1,
        )

        self.assertTrue(payload["index"]["representative"])
        self.assertEqual(payload["index"]["scope"], "representative_sample")
        self.assertEqual(payload["index"]["indexed_source_row_count"], 2)
        self.assertEqual(payload["index"]["source_row_count"], 4)

    def test_metric_value_summary_groups_by_hosts(self):
        _normalized, telemetry_data, _status = normalize_dataset_telemetry(
            "trending",
            make_source_data(),
        )

        payload = telemetry_metric_values_payload(
            dataset="trending",
            data=telemetry_data,
            status=STATUS,
            metric_name="csit_packets_total",
            group_by="hosts",
            limit=10,
        )

        records = {record["group_key"]: record for record in payload["records"]}
        self.assertEqual(payload["analysis"], "telemetry_metric_values")
        self.assertEqual(records["2n-skx,host-a"]["value"]["mean"], 115)
        self.assertEqual(records["3n-alt,host-b"]["sample_count"], 2)

    def test_trend_summary_and_anomalies_are_compact(self):
        _normalized, telemetry_data, _status = normalize_dataset_telemetry(
            "trending",
            make_source_data(),
        )

        trend = telemetry_trend_summary_payload(
            dataset="trending",
            data=telemetry_data,
            status=STATUS,
            metric_name="csit_packets_total",
            group_by="metric_name",
            recent_count=1,
            baseline_count=2,
            limit=10,
        )
        anomalies = telemetry_anomalies_payload(
            dataset="trending",
            data=telemetry_data,
            status=STATUS,
            metric_name="csit_packets_total",
            group_by="metric_name",
            threshold=1.0,
            limit=10,
        )

        self.assertEqual(trend["analysis"], "telemetry_trend_summary")
        self.assertEqual(trend["summary"]["method"], "recent_vs_baseline")
        self.assertEqual(anomalies["analysis"], "telemetry_anomalies")
        self.assertEqual(anomalies["summary"]["method"], "z_score")
        self.assertTrue(anomalies["records"])

    def test_validation_error_for_missing_group_column(self):
        _normalized, telemetry_data, _status = normalize_dataset_telemetry(
            "trending",
            make_source_data(),
        )

        payload = telemetry_metric_values_payload(
            dataset="trending",
            data=telemetry_data,
            status=STATUS,
            metric_name="csit_packets_total",
            group_by="missing",
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["details"]["errors"][0]["field"], "group_by")


if __name__ == "__main__":
    unittest.main()
