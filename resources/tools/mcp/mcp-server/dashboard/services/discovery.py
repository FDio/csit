"""Discovery helpers for CSIT MCP datasets and schema metadata."""

from collections import Counter
from typing import Any

import pandas as pd
from yaml import YAMLError, safe_load

from .data_cache import (
    DATASET_KEYS,
    REQUIRED_DATASETS,
    DataCacheError,
    DataCacheService,
)
from .query import MAX_TOOL_LIMIT
from .serialization import (
    cache_error_payload,
    json_safe_value,
    validation_error_payload,
)
from .result_metadata import ResultMetadataService
from ..settings import AppSettings


DEFAULT_VALUES_LIMIT = 100
DIMENSION_COLUMNS = {
    "build",
    "dut_type",
    "dut_version",
    "hosts",
    "job",
    "passed",
    "release",
    "start_time",
    "test_id",
    "test_type",
    "tg_type",
}
TELEMETRY_COLUMNS = {
    "telemetry",
    "telemetry_metric_count",
    "telemetry_decode_error",
    "telemetry_parse_error",
}


class DiscoveryService:
    """Build small metadata payloads for MCP discovery tools."""

    def __init__(
            self,
            data_cache: DataCacheService,
            settings: AppSettings,
            result_metadata: ResultMetadataService | None = None
        ) -> None:
        self._data_cache = data_cache
        self._settings = settings
        self._data_spec = self._load_data_spec(settings.data_spec_file)
        self._result_metadata = result_metadata or ResultMetadataService()

    def datasets_payload(self) -> dict[str, Any]:
        """Return configured and cached dataset summaries."""

        status = self._data_cache.status_snapshot()
        dataset_status = status.get("datasets", {})
        return {
            "schema_version": 1,
            "data_status": status["status"],
            "ready": status["ready"],
            "freshness": status["last_success_at"],
            "datasets": [
                self._dataset_payload(name, status, dataset_status.get(name, {}))
                for name in DATASET_KEYS
            ],
        }

    def columns_payload(self, dataset: str) -> dict[str, Any]:
        """Return configured and cached column metadata for one dataset."""

        validation_error = self._validate_dataset(dataset)
        if validation_error is not None:
            return validation_error

        status = self._data_cache.status_snapshot()
        configured_columns = self._configured_columns(dataset)
        data = self._cached_dataset_if_ready(dataset)
        cached_columns = list(data.columns) if data is not None else []
        columns = [
            self._column_payload(
                column,
                configured_columns=configured_columns,
                data=data,
            )
            for column in sorted(set(configured_columns) | set(cached_columns))
        ]
        return {
            "schema_version": 1,
            "dataset": dataset,
            "data_status": status["status"],
            "ready": status["ready"],
            "freshness": status["last_success_at"],
            "configured": bool(self._entries_for_dataset(dataset)),
            "row_count": len(data) if data is not None else None,
            "column_count": len(columns),
            "columns": columns,
        }

    def values_payload(
            self,
            dataset: str,
            column: str,
            limit: int = DEFAULT_VALUES_LIMIT
        ) -> dict[str, Any]:
        """Return common values for a loaded cached dataset column."""

        dataset_error = self._validate_dataset(dataset)
        if dataset_error is not None:
            return dataset_error
        parsed_limit, limit_error = self._parse_limit(limit)
        filters = {
            "dataset": dataset,
            "column": column,
            "limit": parsed_limit,
        }
        if limit_error is not None:
            return validation_error_payload([limit_error], filters)

        try:
            data = self._data_cache.get_parquet(query=dataset)
        except DataCacheError as err:
            configured_columns = self._configured_columns(dataset)
            if configured_columns and column not in configured_columns:
                return validation_error_payload(
                    [self._missing_column_error(dataset, column)],
                    filters,
                )
            return cache_error_payload(err, self._data_cache)

        if column not in data.columns:
            return validation_error_payload(
                [self._missing_column_error(dataset, column)],
                filters,
            )

        status = self._data_cache.status_snapshot()
        values = self._common_values(data[column], parsed_limit)
        return {
            "schema_version": 1,
            "dataset": dataset,
            "column": column,
            "limit": parsed_limit,
            "row_count": len(data),
            "returned_count": len(values),
            "data_status": status["status"],
            "freshness": status["last_success_at"],
            "values": values,
        }

    def schema_payload(self, dataset: str) -> dict[str, Any]:
        """Return configured schema metadata for one dataset."""

        validation_error = self._validate_dataset(dataset)
        if validation_error is not None:
            return validation_error

        entries = self._entries_for_dataset(dataset)
        configured_columns = self._configured_columns(dataset)
        result_columns = self._result_columns(configured_columns)
        return {
            "schema_version": 1,
            "dataset": dataset,
            "configured": bool(entries),
            "entry_count": len(entries),
            "configured_columns": configured_columns,
            "result_columns": result_columns,
            "result_metadata": self._result_metadata.metadata_for_columns(
                result_columns,
            ),
            "schemas": [
                self._schema_entry_payload(entry)
                for entry in entries
            ],
        }

    @staticmethod
    def _load_data_spec(data_spec_file: str) -> list[dict[str, Any]]:
        try:
            with open(data_spec_file, encoding="utf-8") as spec_file:
                data_spec = safe_load(spec_file) or []
        except (OSError, YAMLError):
            return []

        return [
            item for item in data_spec
            if isinstance(item, dict)
        ]

    def _dataset_payload(
            self,
            name: str,
            status: dict[str, Any],
            dataset_status: dict[str, Any]
        ) -> dict[str, Any]:
        entries = self._entries_for_dataset(name)
        configured_columns = self._configured_columns(name)
        return {
            "name": name,
            "row_count": status.get("row_counts", {}).get(name, 0),
            "status": dataset_status.get("status"),
            "required": dataset_status.get("required", name in REQUIRED_DATASETS),
            "enabled": dataset_status.get("enabled", self._dataset_enabled(name)),
            "configured": bool(entries) if not dataset_status else dataset_status.get("configured"),
            "normalized_at": dataset_status.get("normalized_at"),
            "telemetry": dataset_status.get(
                "telemetry",
                status.get("telemetry", {}).get(name, {}),
            ),
            "column_count": len(configured_columns),
            "result_columns": self._result_columns(configured_columns),
            "partitions": [
                {
                    "partition": entry.get("partition"),
                    "partition_name": entry.get("partition_name"),
                    "release": entry.get("release"),
                    "schema": entry.get("schema"),
                    "path": entry.get("path"),
                }
                for entry in entries
            ],
        }

    def _column_payload(
            self,
            column: str,
            *,
            configured_columns: list[str],
            data: pd.DataFrame | None
        ) -> dict[str, Any]:
        configured = column in configured_columns
        cached = data is not None and column in data.columns
        payload = {
            "name": column,
            "configured": configured,
            "cached": cached,
            "dtype": None,
            "non_null_count": None,
            "null_count": None,
            "result_column": column.startswith("result_"),
            "dimension_column": column in DIMENSION_COLUMNS,
            "telemetry_column": column in TELEMETRY_COLUMNS,
            "list_valued": False,
            "metadata": self._result_metadata.metadata_for_column(column),
        }
        if not cached:
            return payload

        series = data[column]
        payload["dtype"] = str(series.dtype)
        payload["non_null_count"] = int(series.notna().sum())
        payload["null_count"] = int(series.isna().sum())
        payload["list_valued"] = self._series_contains_list_values(series)
        return payload

    def _cached_dataset_if_ready(self, dataset: str) -> pd.DataFrame | None:
        try:
            return self._data_cache.get_parquet(query=dataset)
        except DataCacheError:
            return None

    def _entries_for_dataset(self, dataset: str) -> list[dict[str, Any]]:
        return [
            entry for entry in self._data_spec
            if entry.get("data_type") == dataset
        ]

    def _dataset_enabled(self, dataset: str) -> bool:
        if dataset in REQUIRED_DATASETS:
            return True
        if dataset == "iterative":
            return self._settings.start_report
        if dataset == "coverage":
            return self._settings.start_coverage
        return True

    def _configured_columns(self, dataset: str) -> list[str]:
        columns = {
            column
            for entry in self._entries_for_dataset(dataset)
            for column in entry.get("columns", [])
        }
        return sorted(columns)

    def _schema_entry_payload(self, entry: dict[str, Any]) -> dict[str, Any]:
        columns = list(entry.get("columns", []))
        result_columns = self._result_columns(columns)
        return {
            "data_type": entry.get("data_type"),
            "partition": entry.get("partition"),
            "partition_name": entry.get("partition_name"),
            "release": entry.get("release"),
            "schema": entry.get("schema"),
            "path": entry.get("path"),
            "columns": columns,
            "result_columns": result_columns,
            "result_metadata": self._result_metadata.metadata_for_columns(
                result_columns,
            ),
        }

    def _validate_dataset(self, dataset: str) -> dict[str, Any] | None:
        if dataset in DATASET_KEYS:
            return None
        return validation_error_payload(
            [{
                "field": "dataset",
                "message": (
                    "dataset must be one of: " +
                    ", ".join(DATASET_KEYS)
                ),
                "value": dataset,
            }],
            {"dataset": dataset},
        )

    @staticmethod
    def _parse_limit(limit: Any) -> tuple[int, dict[str, Any] | None]:
        if isinstance(limit, bool):
            return DEFAULT_VALUES_LIMIT, _limit_error(limit)
        if isinstance(limit, float) and not limit.is_integer():
            return DEFAULT_VALUES_LIMIT, _limit_error(limit)
        try:
            parsed = int(limit)
        except (TypeError, ValueError):
            return DEFAULT_VALUES_LIMIT, _limit_error(limit)
        if parsed < 1 or parsed > MAX_TOOL_LIMIT:
            return DEFAULT_VALUES_LIMIT, _limit_error(limit)
        return parsed, None

    @staticmethod
    def _missing_column_error(dataset: str, column: str) -> dict[str, Any]:
        return {
            "field": "column",
            "message": (
                f"column '{column}' is not available in dataset '{dataset}'."
            ),
            "value": column,
        }

    @classmethod
    def _common_values(cls, series: pd.Series, limit: int) -> list[dict[str, Any]]:
        counter: Counter[str] = Counter()
        values_by_key: dict[str, Any] = {}
        for value in series:
            key = cls._value_key(value)
            counter[key] += 1
            values_by_key.setdefault(key, json_safe_value(value))

        return [
            {
                "key": key,
                "value": values_by_key[key],
                "count": count,
            }
            for key, count in counter.most_common(limit)
        ]

    @classmethod
    def _value_key(cls, value: Any) -> str:
        safe_value = json_safe_value(value)
        if safe_value is None:
            return ""
        if isinstance(safe_value, list):
            return ",".join(sorted(str(item) for item in safe_value))
        return str(safe_value)

    @classmethod
    def _series_contains_list_values(cls, series: pd.Series) -> bool:
        if str(series.dtype).startswith("list<"):
            return True
        return any(
            isinstance(json_safe_value(value), list)
            for value in series.head(100)
        )

    @staticmethod
    def _result_columns(columns: list[str]) -> list[str]:
        return sorted(
            column for column in columns
            if column.startswith("result_")
        )


def _limit_error(value: Any) -> dict[str, Any]:
    return {
        "field": "limit",
        "message": f"limit must be an integer between 1 and {MAX_TOOL_LIMIT}.",
        "value": value,
    }
