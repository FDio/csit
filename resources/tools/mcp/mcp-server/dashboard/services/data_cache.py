"""Data cache service for CSIT parquet data."""

import asyncio
import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import Any, Mapping
from threading import RLock

import pandas as pd
from yaml import YAMLError, safe_load

from ..settings import AppSettings
from .observability import log_event
from .telemetry import (
    empty_telemetry_data,
    empty_telemetry_status,
    failed_telemetry_status,
    indexing_telemetry_status,
    normalize_dataset_telemetry,
)


DATASET_KEYS = ("statistics", "trending", "iterative", "coverage")
REQUIRED_DATASETS = ("statistics", "trending")
READY_STATUSES = ("ready", "degraded")
TEXT_COLUMNS = ("test_id", "job", "release", "dut_type", "test_type")
TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}
REFRESH_HISTORY_LIMIT = 10


class DataCacheError(RuntimeError):
    """Base exception for cache access errors."""


class DataUnavailableError(DataCacheError):
    """Raised when cached CSIT data is not ready to serve."""


class DatasetNotFoundError(DataCacheError):
    """Raised when a requested cached dataset does not exist."""


class DataCacheService:
    """Own loading and access to cached CSIT dataframes."""

    def __init__(
            self,
            settings: AppSettings,
            data_reader_cls: type | None = None
        ) -> None:
        self._settings = settings
        self._data_reader_cls = data_reader_cls
        self._data: dict[str, pd.DataFrame] = self._empty_data()
        self._telemetry_data: dict[str, pd.DataFrame] = self._empty_telemetry_data()
        self._status = "starting"
        self._last_attempt_at: datetime | None = None
        self._last_success_at: datetime | None = None
        self._last_error: str | None = None
        self._last_refresh_started_by: str | None = None
        self._current_refresh_started_by: str | None = None
        self._load_duration_seconds: float | None = None
        self._refresh_history: list[dict[str, Any]] = []
        self._is_loading = False
        self._refresh_task: asyncio.Task | None = None
        self._telemetry_status = self._empty_telemetry_status()
        self._dataset_status = self._build_dataset_status(
            self._data,
            configured_datasets=set(DATASET_KEYS),
            normalized_at=None,
            telemetry_status=self._telemetry_status,
        )
        self._lock = RLock()

    @property
    def data(self) -> Mapping[str, pd.DataFrame]:
        """Return cached dataframes keyed by dataset name."""

        return self._data

    @property
    def telemetry_data(self) -> Mapping[str, pd.DataFrame]:
        """Return parsed OpenMetrics telemetry data keyed by source dataset."""

        return self._telemetry_data

    @property
    def status(self) -> str:
        """Return current data loading status."""

        with self._lock:
            return self._status

    @property
    def is_loading(self) -> bool:
        """Return true if a data load is currently running."""

        with self._lock:
            return self._is_loading

    @property
    def is_serving_ready(self) -> bool:
        """Return true if required datasets are available to serve."""

        with self._lock:
            return (
                self._status in READY_STATUSES and
                not self._missing_required(self._data)
            )

    @property
    def refresh_interval_seconds(self) -> int:
        """Return the configured scheduled refresh interval in seconds."""

        return self._settings.refresh_interval_seconds

    @staticmethod
    def _empty_data() -> dict[str, pd.DataFrame]:
        return {key: pd.DataFrame() for key in DATASET_KEYS}

    @staticmethod
    def _empty_telemetry_data() -> dict[str, pd.DataFrame]:
        return empty_telemetry_data(DATASET_KEYS)

    @staticmethod
    def _empty_telemetry_status() -> dict[str, dict[str, Any]]:
        return empty_telemetry_status(DATASET_KEYS)

    def effective_time_period(self) -> int:
        """Return the configured time period capped at the maximum."""

        return self._settings.effective_time_period()

    def load(self, started_by: str = "manual") -> Mapping[str, pd.DataFrame]:
        """Load all configured parquet data into memory."""

        if not self._begin_load(started_by=started_by):
            return self._data

        return self._load_started()

    def start_refresh(self, started_by: str = "manual") -> bool:
        """Start a background cache refresh if one is not already running."""

        with self._lock:
            if self._refresh_task and not self._refresh_task.done():
                self._log_refresh_skipped_locked(
                    started_by=started_by,
                    reason="already_running",
                )
                return False
            if not self._begin_load_locked(started_by=started_by):
                return False
            self._refresh_task = asyncio.create_task(self._run_refresh())
            return True

    async def shutdown(self) -> None:
        """Cancel an in-flight background refresh during application shutdown."""

        task = self._refresh_task
        if task is None or task.done():
            return

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    async def _run_refresh(self) -> None:
        try:
            await asyncio.to_thread(self._load_started)
        finally:
            with self._lock:
                self._refresh_task = None

    def _begin_load(self, *, started_by: str) -> bool:
        with self._lock:
            return self._begin_load_locked(started_by=started_by)

    def _begin_load_locked(self, *, started_by: str) -> bool:
        if self._is_loading:
            self._log_refresh_skipped_locked(
                started_by=started_by,
                reason="already_running",
            )
            return False

        self._is_loading = True
        self._status = "loading"
        self._last_attempt_at = self._utcnow()
        self._last_refresh_started_by = started_by
        self._current_refresh_started_by = started_by
        self._last_error = None
        self._load_duration_seconds = None
        self._log_refresh_started_locked(started_by=started_by)
        return True

    def _load_started(self) -> Mapping[str, pd.DataFrame]:
        start = perf_counter()

        try:
            self._raise_if_invalid_configuration()
            data_reader_cls = self._resolve_data_reader_cls()
            loaded_data = data_reader_cls(
                data_spec_file=self._settings.data_spec_file,
            ).read_all_data(days=self.effective_time_period())
            self._finish_load(loaded_data, load_started_at=start)
        except Exception as err:
            logging.exception("CSIT parquet data refresh failed.")
            self._finish_failed_load(err, perf_counter() - start)

        return self._data

    def _resolve_data_reader_cls(self) -> type:
        if self._data_reader_cls is not None:
            return self._data_reader_cls

        if self._settings.data_mode == "s3":
            from ..data.data import Data
            return Data
        if self._settings.data_mode == "fixture":
            from ..data.fixture_data import FixtureDataReader
            return FixtureDataReader

        raise ValueError(
            "Unsupported CSIT_DATA_MODE "
            f"{self._settings.data_mode!r}. Expected 's3' or 'fixture'."
        )

    def get_parquet(self, query: str = "all") -> Mapping[str, pd.DataFrame] | pd.DataFrame:
        """Return cached parquet data for a dataset or the full cache.

        Dataframes are normalized once at the cache boundary after loading.
        """

        self.ensure_ready()

        if query == "all":
            return self._data

        if query not in self._data:
            raise DatasetNotFoundError(f"Unknown parquet dataset: {query}")

        return self._data[query]

    def get_telemetry(self, dataset: str) -> pd.DataFrame:
        """Return parsed OpenMetrics telemetry for a cached source dataset."""

        self.ensure_ready()

        if dataset not in self._telemetry_data:
            raise DatasetNotFoundError(f"Unknown telemetry dataset: {dataset}")

        telemetry_status = self._telemetry_status.get(dataset, {})
        if telemetry_status.get("status") == "indexing":
            raise DataUnavailableError(
                f"Telemetry for dataset {dataset!r} is still being indexed."
            )
        if telemetry_status.get("status") == "failed":
            raise DataUnavailableError(
                f"Telemetry indexing failed for dataset {dataset!r}: "
                f"{telemetry_status.get('error')}"
            )

        return self._telemetry_data[dataset]

    def ensure_ready(self) -> None:
        """Raise if data is not ready to serve."""

        if not self.is_serving_ready:
            raise DataUnavailableError(
                f"CSIT data is not ready. Current status: {self.status}"
            )

    def status_snapshot(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of cache status."""

        with self._lock:
            return {
                "status": self._status,
                "ready": (
                    self._status in READY_STATUSES and
                    not self._missing_required(self._data)
                ),
                "last_attempt_at": self._format_datetime(self._last_attempt_at),
                "last_success_at": self._format_datetime(self._last_success_at),
                "cache_age_seconds": self._cache_age_seconds_locked(),
                "last_error": self._last_error,
                "last_refresh_started_by": self._last_refresh_started_by,
                "load_duration_seconds": self._load_duration_seconds,
                "row_counts": self._row_counts(self._data),
                "datasets": self._dataset_status,
                "telemetry": self._telemetry_status,
                "configuration": self._settings.configuration_status(),
                "refresh_history": [
                    dict(entry) for entry in self._refresh_history
                ],
            }

    def _raise_if_invalid_configuration(self) -> None:
        if not self._settings.validation_errors:
            return

        details = "; ".join(
            (
                f"{error['field']}={error['value']!r}: "
                f"{error['message']}"
            )
            for error in self._settings.validation_errors
        )
        raise ValueError(f"Invalid CSIT configuration: {details}")

    def _finish_load(
            self,
            loaded_data: Mapping[str, pd.DataFrame],
            *,
            load_started_at: float
        ) -> None:
        normalized_at = self._utcnow()
        configured_datasets = self._configured_datasets()
        normalized_data = self._normalize_data(loaded_data)
        telemetry_data = self._empty_telemetry_data()
        telemetry_status = indexing_telemetry_status(normalized_data)
        dataset_status = self._build_dataset_status(
            normalized_data,
            configured_datasets=configured_datasets,
            normalized_at=normalized_at,
            telemetry_status=telemetry_status,
        )
        missing_required = self._missing_required(normalized_data)
        missing_optional = self._missing_enabled_optional(dataset_status)

        with self._lock:
            if missing_required:
                self._last_error = (
                    "Required datasets unavailable: " +
                    ", ".join(missing_required)
                )
                self._status = "degraded" if self._has_success_locked() else "failed"
                if not self._has_success_locked():
                    self._data = normalized_data
                    self._telemetry_data = telemetry_data
                    self._telemetry_status = telemetry_status
                    self._dataset_status = dataset_status
                self._load_duration_seconds = round(
                    perf_counter() - load_started_at,
                    3,
                )
                self._is_loading = False
                self._append_refresh_history_locked()
                self._log_refresh_completed_locked()
                self._current_refresh_started_by = None
            else:
                # Publish normalized result data before telemetry expansion. This
                # keeps readiness independent from optional telemetry indexing.
                self._data = normalized_data
                self._telemetry_data = telemetry_data
                self._telemetry_status = telemetry_status
                self._dataset_status = dataset_status
                self._last_success_at = normalized_at
                if missing_optional:
                    self._last_error = (
                        "Optional datasets unavailable: " +
                        ", ".join(missing_optional)
                    )
                    self._status = "degraded"
                else:
                    self._last_error = None
                    self._status = "ready"

        if missing_required:
            self._log_availability()
            return

        log_event(
            "data_cache_published",
            status=self.status,
            row_counts=self._row_counts(normalized_data),
            telemetry_indexing=True,
        )
        normalized_data, telemetry_data, telemetry_status = (
            self._index_telemetry(
                normalized_data,
                configured_datasets=configured_datasets,
                normalized_at=normalized_at,
            )
        )
        dataset_status = self._build_dataset_status(
            normalized_data,
            configured_datasets=configured_datasets,
            normalized_at=normalized_at,
            telemetry_status=telemetry_status,
        )

        with self._lock:
            self._data = normalized_data
            self._telemetry_data = telemetry_data
            self._telemetry_status = telemetry_status
            self._dataset_status = dataset_status
            self._load_duration_seconds = round(
                perf_counter() - load_started_at,
                3,
            )
            self._is_loading = False
            self._append_refresh_history_locked()
            self._log_refresh_completed_locked()
            self._current_refresh_started_by = None

        self._log_availability()

    def _finish_failed_load(self, err: Exception, duration: float) -> None:
        with self._lock:
            self._last_error = repr(err)
            self._status = "degraded" if self._has_success_locked() else "failed"
            self._load_duration_seconds = round(duration, 3)
            self._is_loading = False
            self._append_refresh_history_locked()
            self._log_refresh_completed_locked()
            self._current_refresh_started_by = None

    def _normalize_data(
            self,
            loaded_data: Mapping[str, pd.DataFrame]
        ) -> dict[str, pd.DataFrame]:
        data = self._empty_data()

        for key, value in loaded_data.items():
            if key not in data:
                continue
            normalized = (
                self._normalize_dataframe(value.copy(deep=True))
                if isinstance(value, pd.DataFrame)
                else pd.DataFrame()
            )
            data[key] = normalized

        return data

    def _index_telemetry(
            self,
            data: Mapping[str, pd.DataFrame],
            *,
            configured_datasets: set[str],
            normalized_at: datetime
        ) -> tuple[
            dict[str, pd.DataFrame],
            dict[str, pd.DataFrame],
            dict[str, dict[str, Any]],
        ]:
        indexed_data = dict(data)
        telemetry_data = self._empty_telemetry_data()
        telemetry_status = indexing_telemetry_status(data)
        log_event(
            "telemetry_index_started",
            datasets={
                key: status.get("source_row_count", 0)
                for key, status in telemetry_status.items()
            },
            max_source_rows=self._settings.telemetry_max_source_rows,
            max_samples=self._settings.telemetry_max_samples,
        )

        for key in DATASET_KEYS:
            source_data = data.get(key, pd.DataFrame())
            try:
                normalized, telemetry, telemetry_info = (
                    normalize_dataset_telemetry(
                        key,
                        source_data,
                        max_source_rows=(
                            self._settings.telemetry_max_source_rows
                        ),
                        max_samples=self._settings.telemetry_max_samples,
                    )
                )
            except Exception as err:  # Telemetry must never fail result data.
                logging.exception(
                    "OpenMetrics telemetry indexing failed for %s.",
                    key,
                )
                normalized = source_data
                telemetry = pd.DataFrame()
                telemetry_info = failed_telemetry_status(
                    source_data,
                    err,
                    max_source_rows=self._settings.telemetry_max_source_rows,
                    max_samples=self._settings.telemetry_max_samples,
                )

            log_event(
                "telemetry_index_completed",
                dataset=key,
                status=telemetry_info.get("status"),
                source_row_count=telemetry_info.get("source_row_count", 0),
                indexed_row_count=telemetry_info.get("indexed_row_count", 0),
                sample_count=telemetry_info.get("sample_count", 0),
                rows_with_errors=telemetry_info.get("rows_with_errors", 0),
                decode_error_count=telemetry_info.get(
                    "decode_error_count",
                    0,
                ),
                parse_error_count=telemetry_info.get(
                    "parse_error_count",
                    0,
                ),
                truncated=telemetry_info.get("truncated", False),
                error=telemetry_info.get("error"),
            )
            indexed_data[key] = normalized
            telemetry_data[key] = telemetry
            telemetry_status[key] = telemetry_info
            dataset_status = self._build_dataset_status(
                indexed_data,
                configured_datasets=configured_datasets,
                normalized_at=normalized_at,
                telemetry_status=telemetry_status,
            )
            with self._lock:
                self._data = dict(indexed_data)
                self._telemetry_data = dict(telemetry_data)
                self._telemetry_status = {
                    name: dict(status)
                    for name, status in telemetry_status.items()
                }
                self._dataset_status = dataset_status

        return indexed_data, telemetry_data, telemetry_status

    def _normalize_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        if data.empty:
            return data

        if "start_time" in data.columns:
            timestamps = pd.to_datetime(
                data["start_time"],
                errors="coerce",
                utc=True,
            )
            data["start_time"] = pd.Series(
                [
                    None if pd.isna(value) else value.isoformat()
                    for value in timestamps
                ],
                index=data.index,
                dtype=object,
            )
        if "build" in data.columns:
            data["build"] = pd.to_numeric(
                data["build"],
                errors="coerce",
            ).astype("Int64")
        if "passed" in data.columns:
            data["passed"] = pd.Series(
                [
                    self._normalize_bool_value(value)
                    for value in data["passed"]
                ],
                index=data.index,
                dtype="boolean",
            )
        if "hosts" in data.columns:
            data["hosts"] = pd.Series(
                [
                    self._normalize_hosts_value(value)
                    for value in data["hosts"]
                ],
                index=data.index,
                dtype=object,
            )

        for column in TEXT_COLUMNS:
            if column in data.columns:
                data[column] = pd.Series(
                    [
                        None if self._is_missing_scalar(value) else str(value)
                        for value in data[column]
                    ],
                    index=data.index,
                    dtype=object,
                )
        for column in data.columns:
            if column.startswith("result_"):
                if column.endswith("_unit"):
                    data[column] = pd.Series(
                        [
                            None
                            if self._is_missing_scalar(value)
                            else str(value)
                            for value in data[column]
                        ],
                        index=data.index,
                        dtype=object,
                    )
                else:
                    data[column] = pd.to_numeric(data[column], errors="coerce")

        return data

    def _build_dataset_status(
            self,
            data: Mapping[str, pd.DataFrame],
            *,
            configured_datasets: set[str],
            normalized_at: datetime | None,
            telemetry_status: Mapping[str, Mapping[str, Any]]
        ) -> dict[str, dict[str, Any]]:
        normalized_at_value = self._format_datetime(normalized_at)
        return {
            key: self._dataset_status_entry(
                key,
                data.get(key, pd.DataFrame()),
                configured_datasets=configured_datasets,
                normalized_at=normalized_at_value,
                telemetry_info=telemetry_status.get(key, {}),
            )
            for key in DATASET_KEYS
        }

    def _dataset_status_entry(
            self,
            key: str,
            data: pd.DataFrame,
            *,
            configured_datasets: set[str],
            normalized_at: str | None,
            telemetry_info: Mapping[str, Any]
        ) -> dict[str, Any]:
        required = key in REQUIRED_DATASETS
        enabled = required or self._is_optional_dataset_enabled(key)
        configured = key in configured_datasets
        row_count = len(data)
        if row_count > 0:
            status = "loaded"
        elif not configured:
            status = "not_configured"
        elif not enabled:
            status = "disabled"
        else:
            status = "empty"

        return {
            "status": status,
            "required": required,
            "enabled": enabled,
            "configured": configured,
            "row_count": row_count,
            "columns": list(data.columns),
            "normalized_at": normalized_at if row_count > 0 else None,
            "telemetry": dict(telemetry_info),
        }

    def _configured_datasets(self) -> set[str]:
        try:
            with open(self._settings.data_spec_file, encoding="utf-8") as spec_file:
                data_spec = safe_load(spec_file) or []
        except (OSError, YAMLError):
            return set(DATASET_KEYS)

        configured = {
            item.get("data_type")
            for item in data_spec
            if isinstance(item, dict) and item.get("data_type") in DATASET_KEYS
        }
        return configured or set(DATASET_KEYS)

    def _is_optional_dataset_enabled(self, key: str) -> bool:
        if key == "iterative":
            return self._settings.start_report
        if key == "coverage":
            return self._settings.start_coverage
        return True

    def _has_success_locked(self) -> bool:
        return (
            self._last_success_at is not None and
            not self._missing_required(self._data)
        )

    def _missing_required(
            self,
            data: Mapping[str, pd.DataFrame]
        ) -> list[str]:
        return [key for key in REQUIRED_DATASETS if data.get(key, pd.DataFrame()).empty]

    def _missing_enabled_optional(
            self,
            dataset_status: Mapping[str, Mapping[str, Any]]
        ) -> list[str]:
        return [
            key for key, status in dataset_status.items()
            if (
                key not in REQUIRED_DATASETS and
                status["enabled"] and
                status["configured"] and
                status["status"] == "empty"
            )
        ]

    def _row_counts(self, data: Mapping[str, pd.DataFrame]) -> dict[str, int]:
        return {
            key: len(data.get(key, pd.DataFrame()))
            for key in DATASET_KEYS
        }

    def _append_refresh_history_locked(self) -> None:
        completed_at = self._utcnow()
        entry = {
            "started_at": self._format_datetime(self._last_attempt_at),
            "completed_at": self._format_datetime(completed_at),
            "duration_seconds": self._load_duration_seconds,
            "started_by": (
                self._current_refresh_started_by or
                self._last_refresh_started_by
            ),
            "status": self._status,
            "error": self._last_error,
            "row_counts": self._row_counts(self._data),
        }
        self._refresh_history.append(entry)
        if len(self._refresh_history) > REFRESH_HISTORY_LIMIT:
            self._refresh_history = self._refresh_history[-REFRESH_HISTORY_LIMIT:]

    def _log_refresh_started_locked(self, *, started_by: str) -> None:
        log_event(
            "data_refresh_started",
            started_by=started_by,
            status=self._status,
            last_success_at=self._format_datetime(self._last_success_at),
            row_counts=self._row_counts(self._data),
        )

    def _log_refresh_skipped_locked(self, *, started_by: str, reason: str) -> None:
        log_event(
            "data_refresh_skipped",
            started_by=started_by,
            reason=reason,
            status=self._status,
            last_success_at=self._format_datetime(self._last_success_at),
            row_counts=self._row_counts(self._data),
        )

    def _log_refresh_completed_locked(self) -> None:
        log_event(
            "data_refresh_completed",
            started_by=(
                self._current_refresh_started_by or
                self._last_refresh_started_by
            ),
            status=self._status,
            duration_seconds=self._load_duration_seconds,
            row_counts=self._row_counts(self._data),
            error=self._last_error,
            cache_age_seconds=self._cache_age_seconds_locked(),
        )

    def _cache_age_seconds_locked(self) -> float | None:
        if self._last_success_at is None:
            return None
        return round(
            max(0.0, (self._utcnow() - self._last_success_at).total_seconds()),
            3,
        )

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(tz=UTC)

    @staticmethod
    def _format_datetime(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @classmethod
    def _normalize_bool_value(cls, value: Any) -> Any:
        if cls._is_missing_scalar(value):
            return pd.NA
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            if value == 1:
                return True
            if value == 0:
                return False

        normalized = str(value).strip().lower()
        if normalized in TRUE_VALUES:
            return True
        if normalized in FALSE_VALUES:
            return False
        return pd.NA

    @classmethod
    def _normalize_hosts_value(cls, value: Any) -> str | list[str] | None:
        value = cls._python_value(value)
        if cls._is_missing_scalar(value):
            return None
        if isinstance(value, (list, tuple, set)):
            return [
                str(item)
                for item in value
                if not cls._is_missing_scalar(item)
            ]
        return str(value)

    @classmethod
    def _python_value(cls, value: Any) -> Any:
        if hasattr(value, "as_py"):
            try:
                value = value.as_py()
            except (TypeError, ValueError):
                pass

        if not isinstance(value, (str, bytes)) and hasattr(value, "tolist"):
            try:
                listed = value.tolist()
            except (TypeError, ValueError):
                listed = value
            if listed is not value:
                return cls._python_value(listed)

        return value

    @staticmethod
    def _is_missing_scalar(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, (list, tuple, set, dict)):
            return False
        try:
            return bool(pd.isna(value))
        except (TypeError, ValueError):
            return False

    def _log_availability(self) -> None:
        err_msg = "MCP not loaded, no data available."
        logging.info("\n\nLoading data:\n" + "-" * 26 + "\n")

        if self._settings.start_failures:
            logging.info(self._settings.news_title)
            if self._data["statistics"].empty or self._data["trending"].empty:
                logging.error(err_msg)
        if self._settings.start_statistics:
            logging.info(self._settings.stats_title)
            if self._data["statistics"].empty or self._data["trending"].empty:
                logging.error(err_msg)
        if self._settings.start_trending:
            logging.info(self._settings.trend_title)
            if self._data["trending"].empty:
                logging.error(err_msg)
        if self._settings.start_report:
            logging.info(self._settings.report_title)
            if self._data["iterative"].empty:
                logging.error(err_msg)
        if self._settings.start_coverage:
            logging.info(self._settings.coverage_title)
            if self._data["coverage"].empty:
                logging.error(err_msg)
