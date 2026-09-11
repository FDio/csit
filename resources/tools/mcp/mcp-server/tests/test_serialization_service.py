import json
import unittest

import numpy as np
import pandas as pd

from dashboard.services.data_cache import (
    DatasetNotFoundError,
    DataUnavailableError,
)
from dashboard.services.serialization import (
    cache_error_payload,
    json_safe_value,
    parquet_payload,
    safe_json_dumps,
    validation_error_payload,
)


class DummyDataCache:
    def status_snapshot(self):
        return {
            "status": "loading",
            "ready": False,
        }


class ArrowLikeValue:
    def __init__(self, value):
        self.value = value

    def as_py(self):
        return self.value


class SerializationServiceTests(unittest.TestCase):
    def test_json_safe_value_handles_common_dataframe_scalars(self):
        timestamp = pd.Timestamp("2026-06-05T10:00:00Z")

        self.assertEqual(json_safe_value(timestamp), timestamp.isoformat())
        self.assertIsNone(json_safe_value(pd.NA))
        self.assertEqual(json_safe_value(np.int64(7)), 7)
        self.assertEqual(json_safe_value(np.array([1, 2])), [1, 2])
        self.assertEqual(json_safe_value(ArrowLikeValue(["a", "b"])), ["a", "b"])
        self.assertEqual(
            json_safe_value({"answer": np.float64(42.5), 3: pd.NA}),
            {"answer": 42.5, "3": None},
        )

    def test_parquet_payload_serializes_named_dataset_records(self):
        data = pd.DataFrame(
            {
                "job": ["job-a"],
                "start_time": [pd.Timestamp("2026-06-05T10:00:00Z")],
                "hosts": [["2n-skx", "host-a"]],
            }
        )

        payload = parquet_payload("statistics", data)

        self.assertEqual(payload["query"], "statistics")
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["total_row_count"], 1)
        self.assertEqual(payload["returned_count"], 1)
        self.assertFalse(payload["has_more"])
        self.assertFalse(payload["truncated"])
        self.assertEqual(payload["records"][0]["job"], "job-a")
        self.assertEqual(payload["records"][0]["hosts"], ["2n-skx", "host-a"])

    def test_parquet_payload_serializes_all_datasets(self):
        payload = parquet_payload(
            "all",
            {
                "statistics": pd.DataFrame({"job": ["job-a"]}),
                "trending": pd.DataFrame({"test_id": ["test-a", "test-b"]}),
            },
        )

        self.assertEqual(payload["query"], "all")
        self.assertEqual(payload["datasets"]["statistics"]["row_count"], 1)
        self.assertEqual(payload["datasets"]["trending"]["row_count"], 2)
        self.assertFalse(payload["datasets"]["trending"]["has_more"])

    def test_parquet_payload_caps_named_dataset_preview(self):
        payload = parquet_payload(
            "statistics",
            pd.DataFrame({"job": ["job-a", "job-b", "job-c"]}),
            preview_limit=2,
        )

        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(payload["total_row_count"], 3)
        self.assertEqual(payload["returned_count"], 2)
        self.assertTrue(payload["has_more"])
        self.assertTrue(payload["truncated"])
        self.assertEqual(
            [record["job"] for record in payload["records"]],
            ["job-a", "job-b"],
        )

    def test_parquet_preview_omits_raw_telemetry(self):
        payload = parquet_payload(
            "trending",
            pd.DataFrame({
                "test_id": ["test-a"],
                "telemetry": [["private-blob"]],
            }),
        )

        self.assertEqual(payload["omitted_columns"], ["telemetry"])
        self.assertNotIn("telemetry", payload["records"][0])

    def test_parquet_payload_caps_all_dataset_previews(self):
        payload = parquet_payload(
            "all",
            {
                "statistics": pd.DataFrame({"job": ["job-a", "job-b"]}),
                "trending": pd.DataFrame({"test_id": ["a", "b", "c"]}),
            },
            preview_limit=1,
        )

        self.assertEqual(payload["datasets"]["statistics"]["returned_count"], 1)
        self.assertEqual(payload["datasets"]["trending"]["returned_count"], 1)
        self.assertTrue(payload["datasets"]["statistics"]["has_more"])
        self.assertTrue(payload["datasets"]["trending"]["truncated"])

    def test_validation_error_payload_preserves_shape(self):
        payload = validation_error_payload(
            [{"field": "limit", "message": "bad"}],
            {"limit": 0},
        )

        self.assertEqual(payload["error"], "validation_error")
        self.assertEqual(payload["message"], "Invalid MCP tool arguments.")
        self.assertEqual(payload["details"]["errors"][0]["field"], "limit")
        self.assertEqual(payload["filters"], {"limit": 0})

    def test_cache_error_payload_preserves_error_types(self):
        missing_payload = cache_error_payload(
            DatasetNotFoundError("missing"),
            DummyDataCache(),
        )
        unavailable_payload = cache_error_payload(
            DataUnavailableError("not ready"),
            DummyDataCache(),
        )

        self.assertEqual(missing_payload["error"], "dataset_not_found")
        self.assertEqual(unavailable_payload["error"], "data_unavailable")
        self.assertEqual(unavailable_payload["data"]["status"], "loading")

    def test_safe_json_dumps_returns_response_too_large_payload(self):
        with self.assertLogs("csit_mcp.observability", level="INFO") as logs:
            text = safe_json_dumps(
                {
                    "dataset": "iterative",
                    "row_count": 1,
                    "returned_count": 1,
                    "records": [{"payload": "x" * 200}],
                },
                max_bytes=100,
                suggestions=["Use a smaller limit."],
            )
        payload = json.loads(text)
        event = json.loads(logs.records[0].getMessage())

        self.assertEqual(payload["error"], "response_too_large")
        self.assertGreater(payload["estimated_bytes"], payload["max_bytes"])
        self.assertEqual(payload["context"]["dataset"], "iterative")
        self.assertEqual(payload["suggestions"], ["Use a smaller limit."])
        self.assertEqual(event["event"], "response_too_large")
        self.assertEqual(event["context"]["dataset"], "iterative")
        self.assertEqual(event["suggestions_count"], 1)
        self.assertNotIn("records", logs.output[0])


if __name__ == "__main__":
    unittest.main()
