import tempfile
import unittest
from pathlib import Path

from yaml import safe_load

from dashboard.services.result_metadata import (
    DEFAULT_COMPARABLE_DIMENSIONS,
    ResultMetadataService,
)


DATA_SPEC_FILE = (
    Path(__file__).resolve().parents[1] / "dashboard" / "data" / "data.yaml"
)


class ResultMetadataServiceTests(unittest.TestCase):
    def test_loads_metadata_for_known_result_column(self):
        metadata = ResultMetadataService().metadata_for_column(
            "result_receive_rate_rate_avg"
        )

        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["display_name"], "MRR receive rate average")
        self.assertEqual(metadata["unit_column"], "result_receive_rate_rate_unit")
        self.assertEqual(metadata["preferred_direction"], "higher")
        self.assertEqual(
            metadata["comparable_dimensions"],
            DEFAULT_COMPARABLE_DIMENSIONS,
        )

    def test_returns_no_metadata_for_non_result_or_unknown_columns(self):
        service = ResultMetadataService()

        self.assertIsNone(service.metadata_for_column("job"))
        self.assertIsNone(service.metadata_for_column("result_unknown_value"))

    def test_all_metadata_keys_are_configured_result_columns(self):
        data_spec = safe_load(DATA_SPEC_FILE.read_text(encoding="utf-8"))
        configured_result_columns = {
            column
            for entry in data_spec
            for column in entry.get("columns", [])
            if column.startswith("result_")
        }

        metadata_columns = set(ResultMetadataService().all_metadata())

        self.assertTrue(metadata_columns)
        self.assertTrue(metadata_columns <= configured_result_columns)

    def test_normalizes_invalid_entries_and_defaults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_file = Path(temp_dir) / "result_metadata.yaml"
            metadata_file.write_text(
                """
default_comparable_dimensions:
  - hosts
results:
  result_valid:
    display_name: Valid Result
    unit: percent
    scale: not-a-number
    preferred_direction: sideways
    description: Example.
  job:
    display_name: Not a result column.
  result_invalid:
    - not
    - a
    - mapping
""",
                encoding="utf-8",
            )

            service = ResultMetadataService(metadata_file)
            metadata = service.metadata_for_column("result_valid")

        self.assertEqual(metadata["display_name"], "Valid Result")
        self.assertEqual(metadata["unit"], "percent")
        self.assertEqual(metadata["scale"], 1)
        self.assertEqual(metadata["preferred_direction"], "neutral")
        self.assertEqual(metadata["comparable_dimensions"], ["hosts"])
        self.assertIsNone(service.metadata_for_column("job"))
        self.assertIsNone(service.metadata_for_column("result_invalid"))


if __name__ == "__main__":
    unittest.main()
