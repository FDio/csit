import base64
import os
import unittest
import zlib

from dashboard.services.telemetry_worker import (
    decode_telemetry_rows,
    run_telemetry_decode_worker,
)


def encoded_metric(value=42):
    text = (
        "vpp.runtime.clocks{hostname=host-a,hook=poll,rate=scalar,"
        f"node_name=p4-lookup,state=active}} {value}\n"
    )
    return base64.b64encode(zlib.compress(text.encode())).decode()


class TelemetryWorkerTests(unittest.TestCase):
    def test_decode_rows_returns_selected_metric_samples(self):
        result = decode_telemetry_rows(
            [(7, [encoded_metric()])],
            metric_names=("vpp.runtime.clocks",),
            max_decoded_bytes=100_000,
            max_samples=10,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["rows"][0]["source_row"], 7)
        self.assertEqual(result["rows"][0]["samples"][0]["value"], 42)

    def test_worker_runs_in_a_separate_process(self):
        result = run_telemetry_decode_worker(
            [(1, [encoded_metric(55)])],
            metric_names=("vpp.runtime.clocks",),
            max_decoded_bytes=100_000,
            max_samples=10,
            timeout_seconds=10,
            memory_limit_bytes=0,
        )

        self.assertEqual(result["status"], "ok")
        self.assertNotEqual(result["worker_pid"], os.getpid())
        self.assertEqual(result["rows"][0]["samples"][0]["value"], 55)

    def test_worker_reports_decoded_byte_limit(self):
        result = decode_telemetry_rows(
            [(1, [encoded_metric()])],
            metric_names=("vpp.runtime.clocks",),
            max_decoded_bytes=1,
            max_samples=10,
        )

        self.assertEqual(result["status"], "limit_exceeded")
        self.assertEqual(result["resource"], "decoded_bytes")

    def test_worker_is_terminated_when_deadline_expires(self):
        result = run_telemetry_decode_worker(
            [(1, [encoded_metric()])],
            metric_names=("vpp.runtime.clocks",),
            max_decoded_bytes=100_000,
            max_samples=10,
            timeout_seconds=0.001,
            memory_limit_bytes=0,
        )

        self.assertEqual(result["status"], "timeout")
        self.assertIsNotNone(result["worker_pid"])


if __name__ == "__main__":
    unittest.main()
