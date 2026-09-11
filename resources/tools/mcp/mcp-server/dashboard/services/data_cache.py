"""Data cache service for CSIT parquet data."""

import asyncio
import hashlib
import inspect
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
import shutil
import tempfile
from time import perf_counter
from typing import Any, Callable, Mapping
from threading import RLock
from uuid import uuid4

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from yaml import YAMLError, safe_load

from ..settings import AppSettings
from .memory import dataframe_mapping_memory
from .observability import cgroup_memory_status, log_event
from .telemetry import (
    empty_telemetry_data,
    empty_telemetry_status,
    failed_telemetry_status,
    indexing_telemetry_status,
    normalize_dataset_telemetry,
)
from .telemetry_locator import (
    build_telemetry_locator,
    index_raw_telemetry_frame,
    raw_telemetry_frame,
)


# Cache generations are treated as immutable. Pandas copy-on-write keeps query
# projections cheap while preventing accidental mutation of shared buffers.
pd.options.mode.copy_on_write = True


DATASET_KEYS = ("statistics", "trending", "iterative", "coverage")
REQUIRED_DATASETS = ("statistics", "trending")
READY_STATUSES = ("ready", "degraded")
TEXT_COLUMNS = (
    "test_id", "job", "release", "dut_type", "dut_version", "tg_type",
    "test_type",
)
TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}
REFRESH_HISTORY_LIMIT = 10
SNAPSHOT_FORMAT_VERSION = 2


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
            data_reader_cls: type | None = None,
            *,
            allow_refresh_worker: bool = True,
        ) -> None:
        self._settings = settings
        self._data_reader_cls = data_reader_cls
        self._allow_refresh_worker = allow_refresh_worker
        self._data: dict[str, pd.DataFrame] = self._empty_data()
        self._raw_telemetry: dict[str, pd.DataFrame] = (
            self._empty_raw_telemetry()
        )
        self._telemetry_locators: dict[str, pd.DataFrame] = (
            self._empty_telemetry_locators()
        )
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
        self._snapshot_restored_at: datetime | None = None
        self._snapshot_error: str | None = None
        self._snapshot_generation_id: str | None = None
        self._last_refresh_skip_reason: str | None = None
        self._memory_reporters: dict[str, Callable[[], Mapping[str, Any]]] = {}
        self._generation_listeners: list[Callable[[], None]] = []
        self._owned_memory_cache: dict[str, Any] | None = None
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

    def register_memory_reporter(
            self,
            name: str,
            reporter: Callable[[], Mapping[str, Any]],
        ) -> None:
        """Register additive memory accounting for a cache-adjacent service."""

        with self._lock:
            self._memory_reporters[str(name)] = reporter

    def register_generation_listener(self, listener: Callable[[], None]) -> None:
        """Register a callback which releases state tied to an old generation."""

        with self._lock:
            self._generation_listeners.append(listener)

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

    @property
    def snapshot_enabled(self) -> bool:
        """Return true when a persistent cache snapshot path is configured."""

        return bool(self._settings.cache_snapshot_path)

    def should_refresh_after_restore(self) -> bool:
        """Return whether a restored snapshot needs an immediate remote refresh."""

        maximum_age = getattr(
            self._settings, "snapshot_refresh_max_age_seconds", 0
        )
        if maximum_age <= 0:
            return True
        with self._lock:
            age = self._cache_age_seconds_locked()
            if age is None or age > maximum_age:
                return True
            self._last_refresh_skip_reason = "snapshot_within_freshness_window"
            self._log_refresh_skipped_locked(
                started_by="startup",
                reason=self._last_refresh_skip_reason,
            )
            return False

    @staticmethod
    def _empty_data() -> dict[str, pd.DataFrame]:
        return {key: pd.DataFrame() for key in DATASET_KEYS}

    @staticmethod
    def _empty_telemetry_data() -> dict[str, pd.DataFrame]:
        return empty_telemetry_data(DATASET_KEYS)

    @staticmethod
    def _empty_raw_telemetry() -> dict[str, pd.DataFrame]:
        return {
            key: pd.DataFrame(columns=["_source_row", "telemetry"])
            for key in DATASET_KEYS
        }

    @staticmethod
    def _empty_telemetry_locators() -> dict[str, pd.DataFrame]:
        return {key: pd.DataFrame() for key in DATASET_KEYS}

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
        if self._has_success_locked() and not self._refresh_has_headroom_locked():
            self._last_refresh_skip_reason = "insufficient_memory_headroom"
            self._log_refresh_skipped_locked(
                started_by=started_by,
                reason=self._last_refresh_skip_reason,
            )
            return False

        self._is_loading = True
        if not self._has_success_locked():
            self._status = "loading"
        self._last_attempt_at = self._utcnow()
        self._last_refresh_started_by = started_by
        self._current_refresh_started_by = started_by
        self._last_error = None
        self._last_refresh_skip_reason = None
        self._load_duration_seconds = None
        self._log_refresh_started_locked(started_by=started_by)
        return True

    def _load_started(self) -> Mapping[str, pd.DataFrame]:
        start = perf_counter()

        try:
            self._raise_if_invalid_configuration()
            if self._uses_refresh_worker():
                self._load_from_refresh_worker(load_started_at=start)
                return self._data
            self._load_in_process(load_started_at=start)
        except Exception as err:
            logging.exception("CSIT parquet data refresh failed.")
            self._finish_failed_load(err, perf_counter() - start)

        return self._data

    def _load_in_process(self, *, load_started_at: float) -> None:
        """Read and publish data in the current process."""

        data_reader_cls = self._resolve_data_reader_cls()
        data_reader = data_reader_cls(
            data_spec_file=self._settings.data_spec_file,
        )
        if self._supports_staged_reads(data_reader):
            self._load_required_then_optional(
                data_reader,
                load_started_at=load_started_at,
            )
        else:
            loaded_data = data_reader.read_all_data(
                days=self.effective_time_period()
            )
            self._finish_load(loaded_data, load_started_at=load_started_at)

    def _uses_refresh_worker(self) -> bool:
        """Return true for production S3 refreshes backed by snapshots."""

        return (
            self._allow_refresh_worker and
            self._data_reader_cls is None and
            self._settings.data_mode == "s3" and
            self.snapshot_enabled
        )

    def _load_from_refresh_worker(self, *, load_started_at: float) -> None:
        """Build a snapshot in a disposable process, then publish it."""

        from .refresh_worker import run_cache_refresh_worker

        result = run_cache_refresh_worker(
            self._settings,
            timeout_seconds=self._settings.refresh_worker_timeout_seconds,
        )
        if result.get("status") != "ready":
            raise RuntimeError(
                result.get("message") or
                "Cache refresh worker did not produce a ready generation."
            )

        # Release optional indexes before mapping the replacement generation.
        self._notify_generation_changed()
        snapshot_path = Path(self._settings.cache_snapshot_path)
        self._restore_snapshot_generation(snapshot_path)
        self._complete_restored_telemetry()
        with self._lock:
            self._load_duration_seconds = round(
                perf_counter() - load_started_at,
                3,
            )
            self._is_loading = False
            self._append_refresh_history_locked()
            self._log_refresh_completed_locked()
            self._current_refresh_started_by = None
        log_event(
            "data_refresh_worker_published",
            worker_pid=result.get("worker_pid"),
            worker_duration_seconds=result.get("duration_seconds"),
            generation_id=self._snapshot_generation_id,
            row_counts=self._row_counts(self._data),
        )

    @staticmethod
    def _supports_staged_reads(data_reader: Any) -> bool:
        """Return true when a reader can select dataset types."""

        try:
            parameters = inspect.signature(
                data_reader.read_all_data
            ).parameters
        except (TypeError, ValueError):
            return False
        return "data_types" in parameters

    def _load_required_then_optional(
            self,
            data_reader: Any,
            *,
            load_started_at: float,
        ) -> None:
        """Publish required datasets before loading optional datasets."""

        configured_datasets = self._configured_datasets()
        required_loaded = data_reader.read_all_data(
            days=self.effective_time_period(),
            data_types=REQUIRED_DATASETS,
        )
        required_data, required_raw, required_locators = (
            self._normalize_loaded_data(required_loaded)
        )
        if self._missing_required(required_data):
            self._finish_prepared_load(
                required_data,
                raw_telemetry=required_raw,
                telemetry_locators=required_locators,
                configured_datasets=configured_datasets,
                normalized_at=self._utcnow(),
                load_started_at=load_started_at,
            )
            return

        with self._lock:
            publish_required = not self._has_success_locked()
        if publish_required:
            self._publish_required_data(
                required_data,
                raw_telemetry=required_raw,
                telemetry_locators=required_locators,
                configured_datasets=configured_datasets,
            )

        optional_keys = tuple(
            key for key in DATASET_KEYS if key not in REQUIRED_DATASETS
        )
        optional_loaded = data_reader.read_all_data(
            days=self.effective_time_period(),
            data_types=optional_keys,
        )
        optional_data, optional_raw, optional_locators = (
            self._normalize_loaded_data(optional_loaded)
        )
        normalized_data = {
            key: (
                required_data[key]
                if key in REQUIRED_DATASETS else optional_data[key]
            )
            for key in DATASET_KEYS
        }
        raw_telemetry = {
            key: (
                required_raw[key]
                if key in REQUIRED_DATASETS else optional_raw[key]
            )
            for key in DATASET_KEYS
        }
        telemetry_locators = {
            key: (
                required_locators[key]
                if key in REQUIRED_DATASETS else optional_locators[key]
            )
            for key in DATASET_KEYS
        }
        self._finish_prepared_load(
            normalized_data,
            raw_telemetry=raw_telemetry,
            telemetry_locators=telemetry_locators,
            configured_datasets=configured_datasets,
            normalized_at=self._utcnow(),
            load_started_at=load_started_at,
        )

    def _publish_required_data(
            self,
            data: Mapping[str, pd.DataFrame],
            *,
            raw_telemetry: Mapping[str, pd.DataFrame],
            telemetry_locators: Mapping[str, pd.DataFrame],
            configured_datasets: set[str],
        ) -> None:
        """Make required data ready while optional datasets continue loading."""

        normalized_at = self._utcnow()
        telemetry_status = self._indexing_status(data, raw_telemetry)
        dataset_status = self._build_dataset_status(
            data,
            configured_datasets=configured_datasets,
            normalized_at=normalized_at,
            telemetry_status=telemetry_status,
        )
        with self._lock:
            self._data = dict(data)
            self._raw_telemetry = dict(raw_telemetry)
            self._telemetry_locators = dict(telemetry_locators)
            self._telemetry_data = self._empty_telemetry_data()
            self._telemetry_status = telemetry_status
            self._dataset_status = dataset_status
            self._last_success_at = normalized_at
            self._last_error = "Optional datasets are still loading."
            self._status = "degraded"
            self._owned_memory_cache = None
        self._notify_generation_changed()
        log_event(
            "data_cache_required_published",
            status="degraded",
            row_counts=self._row_counts(data),
            optional_datasets_loading=True,
        )

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

    def restore_snapshot(self) -> bool:
        """Publish the last complete local cache generation when available."""

        if not self.snapshot_enabled:
            return False
        snapshot_path = Path(self._settings.cache_snapshot_path)
        backup_path = snapshot_path.with_name(f".{snapshot_path.name}-old")
        errors: list[str] = []
        for candidate in (snapshot_path, backup_path):
            if not (candidate / "manifest.json").is_file():
                continue
            try:
                self._restore_snapshot_generation(candidate)
                self._complete_restored_telemetry(preserve_snapshot_status=True)
                return True
            except Exception as err:  # A bad generation must not block startup.
                logging.exception(
                    "CSIT cache snapshot restore failed for %s.", candidate
                )
                errors.append(f"{candidate}: {err!r}")
                log_event(
                    "data_snapshot_restore_failed",
                    path=str(candidate),
                    error=repr(err),
                )
        if errors:
            with self._lock:
                self._snapshot_error = "; ".join(errors)
        return False

    def _restore_snapshot_generation(self, snapshot_path: Path) -> None:
        """Restore and publish one validated snapshot generation."""

        manifest = json.loads(
            (snapshot_path / "manifest.json").read_text(encoding="utf-8")
        )
        format_version = manifest.get("format_version")
        if format_version not in (1, SNAPSHOT_FORMAT_VERSION):
            raise ValueError("Unsupported cache snapshot format version.")
        if format_version == SNAPSHOT_FORMAT_VERSION:
            self._validate_snapshot_files(snapshot_path, manifest)

        restored = self._empty_data()
        raw_telemetry = self._empty_raw_telemetry()
        locators = self._empty_telemetry_locators()
        for key in DATASET_KEYS:
            dataset_path = snapshot_path / f"{key}.parquet"
            if dataset_path.is_file():
                restored[key] = self._read_snapshot_frame(dataset_path)
            raw_path = snapshot_path / f"telemetry-{key}.parquet"
            if raw_path.is_file():
                raw_telemetry[key] = index_raw_telemetry_frame(
                    self._read_snapshot_frame(raw_path, preserve_arrow=True)
                )
            locator_path = snapshot_path / f"telemetry-locator-{key}.parquet"
            if locator_path.is_file():
                locators[key] = self._read_snapshot_frame(locator_path)

        if format_version == 1:
            restored, raw_telemetry, locators = self._normalize_loaded_data(
                restored
            )
        else:
            restored = {
                key: self._normalize_dataframe(frame.reset_index(drop=True))
                for key, frame in restored.items()
            }
            for key in DATASET_KEYS:
                if (
                    key == "trending" and locators[key].empty and
                    not raw_telemetry[key].empty
                ):
                    locators[key] = build_telemetry_locator(
                        restored[key], raw_telemetry[key]
                    )

        missing_required = self._missing_required(restored)
        if missing_required:
            raise ValueError(
                "Snapshot is missing required datasets: " +
                ", ".join(missing_required)
            )
        generated_at = datetime.fromisoformat(manifest["generated_at"])
        telemetry_status = self._indexing_status(restored, raw_telemetry)
        dataset_status = self._build_dataset_status(
            restored,
            configured_datasets=set(manifest.get(
                "configured_datasets", DATASET_KEYS
            )),
            normalized_at=generated_at,
            telemetry_status=telemetry_status,
        )
        with self._lock:
            self._data = restored
            self._raw_telemetry = raw_telemetry
            self._telemetry_locators = locators
            self._telemetry_data = self._empty_telemetry_data()
            self._telemetry_status = telemetry_status
            self._dataset_status = dataset_status
            self._last_success_at = generated_at
            self._snapshot_restored_at = self._utcnow()
            self._snapshot_error = None
            self._snapshot_generation_id = str(
                manifest.get("generation_id") or manifest["generated_at"]
            )
            self._last_error = (
                "Serving the last local cache snapshot while S3 refresh "
                "runs in the background."
            )
            self._status = "degraded"
            self._owned_memory_cache = None
        self._notify_generation_changed()
        log_event(
            "data_snapshot_restored",
            path=str(snapshot_path),
            format_version=format_version,
            generation_id=self._snapshot_generation_id,
            generated_at=manifest["generated_at"],
            row_counts=self._row_counts(restored),
        )

    def _complete_restored_telemetry(
            self,
            *,
            preserve_snapshot_status: bool = False,
        ) -> None:
        """Finish optional telemetry indexing for a published snapshot."""

        with self._lock:
            data = dict(self._data)
            raw_telemetry = dict(self._raw_telemetry)
            normalized_at = self._last_success_at or self._utcnow()
            configured = {
                key for key, details in self._dataset_status.items()
                if details.get("configured")
            }
        data, telemetry_data, telemetry_status = self._index_telemetry(
            data,
            raw_telemetry=raw_telemetry,
            configured_datasets=configured,
            normalized_at=normalized_at,
        )
        dataset_status = self._build_dataset_status(
            data,
            configured_datasets=configured,
            normalized_at=normalized_at,
            telemetry_status=telemetry_status,
        )
        missing_optional = self._missing_enabled_optional(dataset_status)
        with self._lock:
            self._data = data
            self._telemetry_data = telemetry_data
            self._telemetry_status = telemetry_status
            self._dataset_status = dataset_status
            self._owned_memory_cache = None
            if preserve_snapshot_status:
                pass
            elif missing_optional:
                self._status = "degraded"
                self._last_error = (
                    "Optional datasets unavailable: " +
                    ", ".join(missing_optional)
                )
            else:
                self._status = "ready"
                self._last_error = None
        self._notify_generation_changed()

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

    def get_raw_telemetry(self, dataset: str) -> pd.DataFrame:
        """Return the private raw-telemetry sidecar for targeted decoding."""

        self.ensure_ready()
        if dataset not in self._raw_telemetry:
            raise DatasetNotFoundError(f"Unknown telemetry dataset: {dataset}")
        return self._raw_telemetry[dataset]

    def get_telemetry_locator(self, dataset: str) -> pd.DataFrame:
        """Return the compact semantic source-row locator for telemetry."""

        self.ensure_ready()
        if dataset not in self._telemetry_locators:
            raise DatasetNotFoundError(f"Unknown telemetry dataset: {dataset}")
        return self._telemetry_locators[dataset]

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
                "last_refresh_skip_reason": self._last_refresh_skip_reason,
                "load_duration_seconds": self._load_duration_seconds,
                "row_counts": self._row_counts(self._data),
                "datasets": self._dataset_status,
                "telemetry": self._telemetry_status,
                "telemetry_source": {
                    key: {
                        "raw_row_count": len(self._raw_telemetry[key]),
                        "locator_row_count": len(
                            self._telemetry_locators[key]
                        ),
                    }
                    for key in DATASET_KEYS
                },
                "configuration": self._settings.configuration_status(),
                "refresh_history": [
                    dict(entry) for entry in self._refresh_history
                ],
                "snapshot": {
                    "enabled": self.snapshot_enabled,
                    "path": self._settings.cache_snapshot_path or None,
                    "generation_id": self._snapshot_generation_id,
                    "restored_at": self._format_datetime(
                        self._snapshot_restored_at
                    ),
                    "error": self._snapshot_error,
                },
                "memory": self._memory_snapshot_locked(),
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
        normalized_data, raw_telemetry, telemetry_locators = (
            self._normalize_loaded_data(loaded_data)
        )
        self._finish_prepared_load(
            normalized_data,
            raw_telemetry=raw_telemetry,
            telemetry_locators=telemetry_locators,
            configured_datasets=self._configured_datasets(),
            normalized_at=self._utcnow(),
            load_started_at=load_started_at,
        )

    def _finish_prepared_load(
            self,
            normalized_data: dict[str, pd.DataFrame],
            *,
            raw_telemetry: dict[str, pd.DataFrame],
            telemetry_locators: dict[str, pd.DataFrame],
            configured_datasets: set[str],
            normalized_at: datetime,
            load_started_at: float,
        ) -> None:
        """Publish normalized cache data and finish optional indexing."""

        telemetry_data = self._empty_telemetry_data()
        telemetry_status = self._indexing_status(
            normalized_data,
            raw_telemetry,
        )
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
                    self._raw_telemetry = raw_telemetry
                    self._telemetry_locators = telemetry_locators
                    self._telemetry_data = telemetry_data
                    self._telemetry_status = telemetry_status
                    self._dataset_status = dataset_status
                    self._owned_memory_cache = None
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
                self._raw_telemetry = raw_telemetry
                self._telemetry_locators = telemetry_locators
                self._telemetry_data = telemetry_data
                self._telemetry_status = telemetry_status
                self._dataset_status = dataset_status
                self._owned_memory_cache = None
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
        self._notify_generation_changed()
        self._persist_snapshot(
            normalized_data,
            raw_telemetry=raw_telemetry,
            telemetry_locators=telemetry_locators,
            configured_datasets=configured_datasets,
            generated_at=normalized_at,
        )
        normalized_data, telemetry_data, telemetry_status = (
            self._index_telemetry(
                normalized_data,
                raw_telemetry=raw_telemetry,
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
            self._raw_telemetry = raw_telemetry
            self._telemetry_locators = telemetry_locators
            self._telemetry_data = telemetry_data
            self._telemetry_status = telemetry_status
            self._dataset_status = dataset_status
            self._owned_memory_cache = None
            self._load_duration_seconds = round(
                perf_counter() - load_started_at,
                3,
            )
            self._is_loading = False
            self._append_refresh_history_locked()
            self._log_refresh_completed_locked()
            self._current_refresh_started_by = None

        self._notify_generation_changed()
        self._log_availability()

    def _persist_snapshot(
            self,
            data: Mapping[str, pd.DataFrame],
            *,
            raw_telemetry: Mapping[str, pd.DataFrame],
            telemetry_locators: Mapping[str, pd.DataFrame],
            configured_datasets: set[str],
            generated_at: datetime,
        ) -> None:
        if not self.snapshot_enabled:
            return
        snapshot_path = Path(self._settings.cache_snapshot_path)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = Path(tempfile.mkdtemp(
            prefix=f".{snapshot_path.name}-",
            dir=snapshot_path.parent,
        ))
        backup_path = snapshot_path.with_name(f".{snapshot_path.name}-old")
        try:
            files: dict[str, dict[str, Any]] = {}
            for key in DATASET_KEYS:
                for filename, frame in (
                    (f"{key}.parquet", data.get(key, pd.DataFrame())),
                    (
                        f"telemetry-{key}.parquet",
                        raw_telemetry.get(key, pd.DataFrame()),
                    ),
                    (
                        f"telemetry-locator-{key}.parquet",
                        telemetry_locators.get(key, pd.DataFrame()),
                    ),
                ):
                    if frame.empty and not len(frame.columns):
                        continue
                    file_path = temporary_path / filename
                    self._write_snapshot_frame(frame, file_path)
                    parquet_file = pq.ParquetFile(file_path)
                    if parquet_file.metadata.num_rows != len(frame):
                        raise ValueError(
                            f"Snapshot round-trip row mismatch for {filename}."
                        )
                    self._validate_snapshot_readable(parquet_file)
                    files[filename] = {
                        "row_count": len(frame),
                        "sha256": self._file_sha256(file_path),
                        "schema_sha256": self._schema_sha256(
                            parquet_file.schema_arrow
                        ),
                    }
            generation_id = uuid4().hex
            manifest = {
                "format_version": SNAPSHOT_FORMAT_VERSION,
                "generation_id": generation_id,
                "generated_at": generated_at.isoformat(),
                "effective_time_period": self.effective_time_period(),
                "configured_datasets": sorted(configured_datasets),
                "row_counts": self._row_counts(data),
                "files": files,
            }
            (temporary_path / "manifest.json").write_text(
                json.dumps(manifest, indent=2),
                encoding="utf-8",
            )
            self._validate_snapshot_files(temporary_path, manifest)
            if backup_path.exists():
                shutil.rmtree(backup_path)
            if snapshot_path.exists():
                snapshot_path.replace(backup_path)
            temporary_path.replace(snapshot_path)
            with self._lock:
                self._snapshot_generation_id = generation_id
                self._snapshot_error = None
            log_event(
                "data_snapshot_persisted",
                path=str(snapshot_path),
                format_version=SNAPSHOT_FORMAT_VERSION,
                generation_id=generation_id,
                generated_at=generated_at.isoformat(),
                row_counts=self._row_counts(data),
                raw_telemetry_rows={
                    key: len(raw_telemetry.get(key, pd.DataFrame()))
                    for key in DATASET_KEYS
                },
            )
        except Exception as err:  # Snapshot persistence is non-fatal.
            logging.exception("CSIT cache snapshot persistence failed.")
            try:
                if not snapshot_path.exists() and backup_path.exists():
                    backup_path.replace(snapshot_path)
            except OSError:
                logging.exception("CSIT cache snapshot rollback failed.")
            with self._lock:
                self._snapshot_error = repr(err)
            log_event(
                "data_snapshot_persist_failed",
                path=str(snapshot_path),
                error=repr(err),
            )
        finally:
            if temporary_path.exists():
                shutil.rmtree(temporary_path)

    @staticmethod
    def _write_snapshot_frame(data: pd.DataFrame, path: Path) -> None:
        """Write Arrow-native parquet without fragile Pandas dtype metadata."""

        table = pa.Table.from_pandas(data, preserve_index=False)
        table = table.replace_schema_metadata(None)
        pq.write_table(table, path, row_group_size=1024)

    @staticmethod
    def _read_snapshot_frame(
            path: Path,
            *,
            preserve_arrow: bool = True,
        ) -> pd.DataFrame:
        """Read parquet while ignoring extension dtype metadata from v1 files."""

        options = {"types_mapper": pd.ArrowDtype} if preserve_arrow else {}
        return pq.read_table(path, memory_map=True).to_pandas(
            ignore_metadata=True,
            **options,
        )

    @staticmethod
    def _file_sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _schema_sha256(schema: pa.Schema) -> str:
        return hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()

    def _validate_snapshot_files(
            self,
            snapshot_path: Path,
            manifest: Mapping[str, Any],
        ) -> None:
        for filename, details in manifest.get("files", {}).items():
            path = snapshot_path / filename
            if not path.is_file():
                raise ValueError(f"Snapshot file is missing: {filename}")
            if self._file_sha256(path) != details.get("sha256"):
                raise ValueError(f"Snapshot checksum mismatch: {filename}")
            metadata = pq.ParquetFile(path).metadata
            if metadata.num_rows != int(details.get("row_count", -1)):
                raise ValueError(f"Snapshot row-count mismatch: {filename}")
            expected_schema = details.get("schema_sha256")
            if expected_schema:
                actual_schema = self._schema_sha256(
                    pq.ParquetFile(path).schema_arrow
                )
                if actual_schema != expected_schema:
                    raise ValueError(
                        f"Snapshot schema checksum mismatch: {filename}"
                    )

    @staticmethod
    def _validate_snapshot_readable(parquet_file: pq.ParquetFile) -> None:
        """Round-trip bounded row groups without materializing huge sidecars."""

        if parquet_file.metadata.num_rows == 0:
            return
        row_groups = {0, parquet_file.num_row_groups - 1}
        for row_group in row_groups:
            parquet_file.read_row_group(row_group).to_pandas(
                ignore_metadata=True
            )

    def _finish_failed_load(self, err: Exception, duration: float) -> None:
        with self._lock:
            self._last_error = repr(err)
            self._status = "degraded" if self._has_success_locked() else "failed"
            self._load_duration_seconds = round(duration, 3)
            self._is_loading = False
            self._append_refresh_history_locked()
            self._log_refresh_completed_locked()
            self._current_refresh_started_by = None

    def _normalize_loaded_data(
            self,
            loaded_data: Mapping[str, pd.DataFrame]
        ) -> tuple[
            dict[str, pd.DataFrame],
            dict[str, pd.DataFrame],
            dict[str, pd.DataFrame],
        ]:
        data = self._empty_data()
        raw_telemetry = self._empty_raw_telemetry()
        locators = self._empty_telemetry_locators()

        for key, value in loaded_data.items():
            if key not in data:
                continue
            if not isinstance(value, pd.DataFrame):
                continue
            value.reset_index(drop=True, inplace=True)
            raw_telemetry[key] = raw_telemetry_frame(value)
            normalized = self._normalize_dataframe(value)
            data[key] = normalized
            if key == "trending":
                locators[key] = build_telemetry_locator(
                    normalized,
                    raw_telemetry[key],
                )

        return data, raw_telemetry, locators

    def _normalize_data(
            self,
            loaded_data: Mapping[str, pd.DataFrame]
        ) -> dict[str, pd.DataFrame]:
        """Compatibility wrapper returning public result data only."""

        data, _raw_telemetry, _locators = self._normalize_loaded_data(
            loaded_data
        )
        return data

    @staticmethod
    def _indexing_status(
            data: Mapping[str, pd.DataFrame],
            raw_telemetry: Mapping[str, pd.DataFrame],
        ) -> dict[str, dict[str, Any]]:
        del data
        return indexing_telemetry_status(raw_telemetry)

    def _index_telemetry(
            self,
            data: Mapping[str, pd.DataFrame],
            *,
            raw_telemetry: Mapping[str, pd.DataFrame],
            configured_datasets: set[str],
            normalized_at: datetime
        ) -> tuple[
            dict[str, pd.DataFrame],
            dict[str, pd.DataFrame],
            dict[str, dict[str, Any]],
        ]:
        indexed_data = dict(data)
        telemetry_data = self._empty_telemetry_data()
        telemetry_status = self._indexing_status(data, raw_telemetry)
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
            telemetry_source_data = raw_telemetry.get(key, pd.DataFrame())
            try:
                normalized, telemetry, telemetry_info = (
                    normalize_dataset_telemetry(
                        key,
                        source_data,
                        telemetry_source=telemetry_source_data,
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
                    telemetry_source_data,
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
            indexed_data[key] = normalized.drop(
                columns=["telemetry"], errors="ignore"
            )
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
                self._owned_memory_cache = None

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
                timestamps,
                index=data.index,
                dtype=pd.ArrowDtype(pa.timestamp("us", tz="UTC")),
            )
        if "build" in data.columns:
            data["build"] = pd.to_numeric(
                data["build"],
                errors="coerce",
            ).astype("Int64")
        if "passed" in data.columns:
            data["passed"] = data["passed"].map(
                self._normalize_bool_value
            ).astype("boolean")
        if "hosts" in data.columns:
            hosts = [self._normalize_hosts_value(value) for value in data["hosts"]]
            if all(value is None or isinstance(value, list) for value in hosts):
                data["hosts"] = pd.Series(
                    hosts,
                    index=data.index,
                    dtype=pd.ArrowDtype(pa.list_(pa.string())),
                )
            else:
                data["hosts"] = pd.Series(hosts, index=data.index, dtype=object)

        for column in TEXT_COLUMNS:
            if column in data.columns:
                data[column] = data[column].astype("string[pyarrow]")
        for column in data.columns:
            if column.startswith("result_"):
                if column.endswith(("_unit", "_hdrh")):
                    data[column] = data[column].astype("string[pyarrow]")
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

    def _owned_memory_locked(self) -> dict[str, Any]:
        if self._owned_memory_cache is not None:
            return self._owned_memory_cache
        result_data = dataframe_mapping_memory(self._data)
        raw_telemetry = dataframe_mapping_memory(self._raw_telemetry)
        telemetry_locators = dataframe_mapping_memory(self._telemetry_locators)
        telemetry_index = dataframe_mapping_memory(self._telemetry_data)
        total = sum(
            item["total_bytes"]
            for item in (
                result_data, raw_telemetry, telemetry_locators, telemetry_index
            )
        )
        self._owned_memory_cache = {
            "estimated_bytes": total,
            "result_data": result_data,
            "raw_telemetry": raw_telemetry,
            "telemetry_locators": telemetry_locators,
            "telemetry_index": telemetry_index,
        }
        return self._owned_memory_cache

    def _memory_snapshot_locked(self) -> dict[str, Any]:
        reporters: dict[str, Any] = {}
        for name, reporter in self._memory_reporters.items():
            try:
                reporters[name] = dict(reporter())
            except Exception as err:  # Memory reporting must not affect readiness.
                reporters[name] = {"error": repr(err)}
        return {
            "cgroup": cgroup_memory_status(),
            "cache": self._owned_memory_locked(),
            "services": reporters,
        }

    def _refresh_has_headroom_locked(self) -> bool:
        memory = cgroup_memory_status()
        current = memory.get("current_bytes")
        maximum = memory.get("max_bytes")
        if current is None or maximum in (None, 0):
            return True
        cache_bytes = self._owned_memory_locked()["estimated_bytes"]
        projected = int(current) + max(cache_bytes, 64 * 1024 * 1024)
        limit_percent = getattr(
            self._settings, "refresh_memory_limit_percent", 85
        )
        return projected <= int(maximum * (limit_percent / 100.0))

    def _notify_generation_changed(self) -> None:
        with self._lock:
            listeners = tuple(self._generation_listeners)
        for listener in listeners:
            try:
                listener()
            except Exception:
                logging.exception("Cache generation listener failed.")

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
            memory=self._memory_snapshot_locked(),
        )

    def _log_refresh_skipped_locked(self, *, started_by: str, reason: str) -> None:
        log_event(
            "data_refresh_skipped",
            started_by=started_by,
            reason=reason,
            status=self._status,
            last_success_at=self._format_datetime(self._last_success_at),
            row_counts=self._row_counts(self._data),
            memory=self._memory_snapshot_locked(),
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
            memory=self._memory_snapshot_locked(),
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
