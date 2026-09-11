from concurrent.futures import ThreadPoolExecutor
import time
import unittest
from unittest.mock import patch

from dashboard.services.query_guard import QueryAdmissionController
from dashboard.settings import get_settings


class QueryAdmissionControllerTests(unittest.TestCase):
    def setUp(self):
        self.controller = QueryAdmissionController(get_settings(environ={
            "CSIT_QUERY_MAX_CONCURRENT": "1",
            "CSIT_QUERY_QUEUE_TIMEOUT_SECONDS": "1",
            "CSIT_QUERY_HEAVY_ROW_THRESHOLD": "1",
            "CSIT_QUERY_MEMORY_SOFT_LIMIT_PERCENT": "75",
        }))

    @patch(
        "dashboard.services.query_guard.cgroup_memory_status",
        return_value={
            "current_bytes": 10,
            "max_bytes": 100,
            "used_percent": 10.0,
        },
    )
    def test_overlapping_heavy_query_is_rejected(self, _memory):
        entered = []

        def slow_query():
            entered.append(True)
            time.sleep(1.2)
            return {"ok": True}

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(
                self.controller.run,
                tool="trending",
                dataset="trending",
                row_count=187_000,
                callback=slow_query,
            )
            while not entered:
                time.sleep(0.01)
            second = executor.submit(
                self.controller.run,
                tool="trending",
                dataset="trending",
                row_count=187_000,
                callback=lambda: {"second": True},
            )

        self.assertEqual(first.result(), {"ok": True})
        self.assertEqual(second.result()["error"], "server_busy")
        self.assertEqual(second.result()["reason"], "concurrency_limit")

    @patch(
        "dashboard.services.query_guard.cgroup_memory_status",
        return_value={
            "current_bytes": 90,
            "max_bytes": 100,
            "used_percent": 90.0,
        },
    )
    def test_memory_pressure_rejects_before_callback(self, _memory):
        called = []
        payload = self.controller.run(
            tool="telemetry_timeseries",
            dataset="trending",
            row_count=187_000,
            callback=lambda: called.append(True) or {"ok": True},
        )

        self.assertEqual(payload["error"], "server_busy")
        self.assertEqual(payload["reason"], "memory_pressure")
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
