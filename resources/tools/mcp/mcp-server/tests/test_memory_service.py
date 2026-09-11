import unittest

import pandas as pd

from dashboard.services.index_registry import DerivedIndexRegistry
from dashboard.services.memory import (
    compact_semantic_frame,
    dataframe_memory_bytes,
    estimated_python_heap_bytes,
)


class MemoryServiceTests(unittest.TestCase):
    def test_compact_semantic_frame_reduces_repeated_dimensions(self):
        data = pd.DataFrame({
            "test_type": ["mrr", "ndrpdr"] * 500,
            "value": list(range(1000)),
        })
        before = dataframe_memory_bytes(data)

        result = compact_semantic_frame(
            data,
            categorical_columns=("test_type",),
        )

        self.assertEqual(str(result["test_type"].dtype), "category")
        self.assertLess(dataframe_memory_bytes(result), before)

    def test_compact_semantic_frame_keeps_high_cardinality_text(self):
        data = pd.DataFrame({"series_id": [f"series-{item}" for item in range(100)]})

        compact_semantic_frame(data, categorical_columns=("series_id",))

        self.assertNotEqual(str(data["series_id"].dtype), "category")

    def test_heap_estimate_includes_nested_values(self):
        value = {"records": [{"hosts": ["host-a", "host-b"]}]}

        self.assertGreater(estimated_python_heap_bytes(value), 100)

    def test_registry_reports_and_clears_owned_indexes(self):
        registry = DerivedIndexRegistry()

        before = registry.memory_snapshot()
        registry.clear()
        after = registry.memory_snapshot()

        self.assertEqual(before["estimated_bytes"], 0)
        self.assertEqual(after["estimated_bytes"], 0)
        self.assertEqual(
            set(after["components"]),
            {"trending", "iterative", "coverage", "comparison", "statistics"},
        )


if __name__ == "__main__":
    unittest.main()
