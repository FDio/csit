"""Read small local fixture datasets for CSIT MCP development."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd


DATASET_KEYS = ("statistics", "trending", "iterative", "coverage")
TIME_FILTERED_DATASETS = ("statistics", "trending")


class FixtureDataReader:
    """Load local JSON records using the same interface as the S3 reader."""

    def __init__(
            self,
            data_spec_file: str,
            fixture_dir: str | Path | None = None
        ) -> None:
        self._data_spec_file = data_spec_file
        self._fixture_dir = (
            Path(fixture_dir)
            if fixture_dir is not None
            else Path(__file__).with_name("fixtures")
        )

    def read_all_data(self, days: int | None = None) -> dict[str, pd.DataFrame]:
        """Return fixture dataframes keyed by CSIT dataset name."""

        data = {
            dataset: self._read_dataset(dataset)
            for dataset in DATASET_KEYS
        }
        if days:
            for dataset in TIME_FILTERED_DATASETS:
                data[dataset] = self._filter_by_days(data[dataset], days)
        return data

    def _read_dataset(self, dataset: str) -> pd.DataFrame:
        fixture_path = self._fixture_dir / f"{dataset}.json"
        try:
            with fixture_path.open(encoding="utf-8") as fixture_file:
                records = json.load(fixture_file)
        except OSError as err:
            raise RuntimeError(
                f"Unable to read fixture dataset '{dataset}' from "
                f"{fixture_path}."
            ) from err
        except json.JSONDecodeError as err:
            raise RuntimeError(
                f"Invalid JSON fixture dataset '{dataset}' in {fixture_path}."
            ) from err

        if not isinstance(records, list):
            raise RuntimeError(
                f"Fixture dataset '{dataset}' must contain a JSON list."
            )
        if not all(isinstance(record, dict) for record in records):
            raise RuntimeError(
                f"Fixture dataset '{dataset}' must contain JSON objects."
            )
        return pd.DataFrame(records)

    @staticmethod
    def _filter_by_days(data: pd.DataFrame, days: int) -> pd.DataFrame:
        if data.empty or "start_time" not in data.columns:
            return data

        timestamps = pd.to_datetime(data["start_time"], errors="coerce", utc=True)
        cutoff = datetime.now(tz=UTC) - timedelta(days=days)
        return data.loc[timestamps >= cutoff].reset_index(drop=True)
