"""Catalog and semantic series helpers for CSIT iterative data."""

from __future__ import annotations

import hashlib
import json
import math
import re
import threading
from typing import Any

import pandas as pd

from .result_series import (
    DUT_ORDER,
    LOGICAL_TEST_TYPES,
    PREFERRED_DUTS,
    TEST_TYPE_ORDER,
    area_label,
    dataframe_records,
    hosts_value,
    integer_value,
    is_passed,
    natural_key,
    parse_result_dimensions,
    semantic_metrics,
    text_value,
)
from .memory import compact_semantic_frame, dataframe_memory_bytes
from .serialization import records_from_dataframe, validation_error_payload


DEFAULT_ITERATIVE_LIMIT = 1000
MAX_ITERATIVE_LIMIT = 10000
CATALOG_DIMENSIONS = (
    "release",
    "dut",
    "dut_version",
    "area",
    "test",
    "infra",
    "testbed",
    "framesize",
    "cores",
    "test_type",
)
ALL_DIMENSIONS = {"testbed", "framesize", "cores", "test_type"}

_POINT_COLUMNS = (
    "series_id",
    "name",
    "release",
    "dut",
    "dut_version",
    "area",
    "area_label",
    "test",
    "infra",
    "testbed",
    "framesize",
    "cores",
    "test_type",
    "dut_type",
    "tg_type",
    "test_id",
    "start_time",
    "job",
    "build",
    "hosts",
    "throughput_value",
    "throughput_unit",
    "bandwidth_value",
    "bandwidth_unit",
    "latency_value",
    "latency_unit",
)
_SERIES_COLUMNS = _POINT_COLUMNS[:13]


class IterativeService:
    """Build and cache a semantic index for one iterative cache publication."""

    def __init__(self) -> None:
        self._cache_key: tuple[int, Any, int] | None = None
        self._points = pd.DataFrame(columns=_POINT_COLUMNS)
        self._catalog = pd.DataFrame(columns=_SERIES_COLUMNS)
        self._series = pd.DataFrame(columns=_SERIES_COLUMNS)
        self._unclassified_row_count = 0
        self._memory_bytes = 0
        self._lock = threading.Lock()

    def catalog_payload(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            *,
            release: Any = None,
            dut: Any = None,
            dut_version: Any = None,
            area: Any = None,
            test: Any = None,
            infra: Any = None,
            testbed: Any = None,
            framesize: Any = None,
            cores: Any = None,
            test_type: Any = None,
            select_defaults: Any = False,
            offset: Any = 0,
            limit: Any = DEFAULT_ITERATIVE_LIMIT,
        ) -> dict[str, Any]:
        """Return cascading filters and matching logical test definitions."""

        self._ensure_index(data, status)
        parsed_limit, limit_error = _parse_integer(
            "limit", limit, default=DEFAULT_ITERATIVE_LIMIT, minimum=1,
            maximum=MAX_ITERATIVE_LIMIT,
        )
        parsed_offset, offset_error = _parse_integer(
            "offset", offset, default=0, minimum=0,
        )
        parsed_defaults, defaults_error = _parse_bool(select_defaults)
        requested = {
            "release": _selection("release", release),
            "dut": _selection("dut", dut),
            "dut_version": _selection("dut_version", dut_version),
            "area": _selection("area", area),
            "test": _selection("test", test),
            "infra": _selection("infra", infra),
            "testbed": _selection("testbed", testbed),
            "framesize": _selection("framesize", framesize),
            "cores": _selection("cores", cores),
            "test_type": _selection("test_type", test_type),
        }
        errors = [
            error for error in (limit_error, offset_error, defaults_error)
            if error is not None
        ]
        filtered = self._catalog
        options: dict[str, list[str]] = {}
        selected: dict[str, str | None] = {}

        for dimension in CATALOG_DIMENSIONS:
            available = _available_values(filtered, dimension)
            options[dimension] = available
            value = requested[dimension]
            supports_all = dimension in ALL_DIMENSIONS
            if supports_all and value == "all":
                selected[dimension] = "all"
                continue
            if value is None and parsed_defaults:
                value = (
                    "all" if supports_all
                    else _default_value(dimension, available)
                )
            elif value is not None and value not in available:
                if parsed_defaults:
                    value = (
                        "all" if supports_all
                        else _default_value(dimension, available)
                    )
                else:
                    errors.append({
                        "field": dimension,
                        "message": (
                            f"{dimension} must be one of the values available "
                            "after the preceding iterative filters."
                        ),
                        "value": requested[dimension],
                        "available": available,
                    })
                    value = None
            selected[dimension] = value
            if value is not None and value != "all":
                filtered = filtered.loc[
                    filtered[dimension].astype("string") == value
                ]

        filters = {
            **selected,
            "select_defaults": parsed_defaults,
            "offset": parsed_offset,
            "limit": parsed_limit,
        }
        if errors:
            return validation_error_payload(errors, filters)

        matching_series = (
            filtered.drop_duplicates(subset="series_id", keep="first")
            .sort_values(["name", "series_id"], kind="stable")
            .reset_index(drop=True)
        )
        returned = matching_series.iloc[
            parsed_offset:parsed_offset + parsed_limit
        ]
        payload = _paged_payload(
            dataset="iterative_catalog",
            source_count=len(self._series),
            available_count=len(matching_series),
            returned=returned,
            filters=filters,
            status=status,
        )
        payload["filter_options"] = options
        payload["option_labels"] = {
            "area": {
                value: area_label(value)
                for value in options.get("area", [])
            }
        }
        payload["unclassified_row_count"] = self._unclassified_row_count
        return payload

    def series_payload(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            *,
            series: Any,
            offset: Any = 0,
            limit: Any = DEFAULT_ITERATIVE_LIMIT,
        ) -> dict[str, Any]:
        """Return paginated semantic samples for selected series IDs."""

        self._ensure_index(data, status)
        parsed_limit, limit_error = _parse_integer(
            "limit", limit, default=DEFAULT_ITERATIVE_LIMIT, minimum=1,
            maximum=MAX_ITERATIVE_LIMIT,
        )
        parsed_offset, offset_error = _parse_integer(
            "offset", offset, default=0, minimum=0,
        )
        parsed_series, series_error = _parse_series(series)
        filters = {
            "series": parsed_series,
            "offset": parsed_offset,
            "limit": parsed_limit,
        }
        errors = [
            error for error in (limit_error, offset_error, series_error)
            if error is not None
        ]
        if errors:
            return validation_error_payload(errors, filters)

        known_ids = set(self._series["series_id"].astype(str))
        requested_ids = list(dict.fromkeys(parsed_series))
        unknown = [value for value in requested_ids if value not in known_ids]
        selected_ids = [value for value in requested_ids if value in known_ids]
        selected_series = self._series.loc[
            self._series["series_id"].isin(selected_ids)
        ].sort_values(["name", "series_id"], kind="stable")
        filtered = self._points.loc[
            self._points["series_id"].isin(selected_ids)
        ].copy()
        if not filtered.empty:
            filtered["_start_time"] = pd.to_datetime(
                filtered["start_time"], errors="coerce", utc=True,
            )
            filtered = filtered.sort_values(
                ["_start_time", "name", "series_id"],
                kind="stable",
                na_position="last",
            ).drop(columns="_start_time")
        returned = filtered.iloc[parsed_offset:parsed_offset + parsed_limit]
        payload = _paged_payload(
            dataset="iterative_series",
            source_count=len(self._points),
            available_count=len(filtered),
            returned=returned,
            filters=filters,
            status=status,
        )
        payload["series"] = records_from_dataframe(selected_series)
        payload["unknown_series"] = unknown
        return payload

    def _ensure_index(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
        ) -> None:
        cache_key = (id(data), status.get("last_success_at"), len(data))
        if self._cache_key == cache_key:
            return
        with self._lock:
            if self._cache_key == cache_key:
                return
            points, unclassified = _build_points(data)
            self._points = compact_semantic_frame(
                points,
                categorical_columns=(
                    "series_id", "name", "release", "dut", "dut_version",
                    "area", "area_label", "test", "infra", "testbed",
                    "framesize", "cores", "test_type", "dut_type", "tg_type",
                    "test_id", "job", "throughput_unit", "bandwidth_unit",
                    "latency_unit",
                ),
            )
            self._catalog = (
                self._points.loc[:, list(_SERIES_COLUMNS)]
                .drop_duplicates(keep="first")
                .reset_index(drop=True)
            )
            self._series = (
                self._catalog
                .drop_duplicates(subset="series_id", keep="first")
                .sort_values(["name", "series_id"], kind="stable")
                .reset_index(drop=True)
            )
            self._unclassified_row_count = unclassified
            self._memory_bytes = sum(map(dataframe_memory_bytes, (
                self._points, self._catalog, self._series,
            )))
            self._cache_key = cache_key

    def clear(self) -> None:
        with self._lock:
            self._cache_key = None
            self._points = pd.DataFrame(columns=_POINT_COLUMNS)
            self._catalog = pd.DataFrame(columns=_SERIES_COLUMNS)
            self._series = pd.DataFrame(columns=_SERIES_COLUMNS)
            self._unclassified_row_count = 0
            self._memory_bytes = 0

    def memory_usage_bytes(self) -> int:
        with self._lock:
            return self._memory_bytes


def _build_points(data: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    points: list[dict[str, Any]] = []
    unclassified = 0
    for row in dataframe_records(data):
        if not is_passed(row.get("passed")):
            continue
        dimensions = parse_result_dimensions(row)
        release = text_value(row.get("release"))
        dut_version = text_value(row.get("dut_version"))
        logical_types = LOGICAL_TEST_TYPES.get(
            text_value(row.get("test_type")) or "", ()
        )
        if dimensions is None or not release or not dut_version or not logical_types:
            unclassified += 1
            continue
        produced = False
        for logical_type in logical_types:
            point = _point_from_row(
                row,
                dimensions,
                release=release,
                dut_version=dut_version,
                logical_type=logical_type,
            )
            if point is not None:
                points.append(point)
                produced = True
        if not produced:
            unclassified += 1
    return pd.DataFrame(points, columns=_POINT_COLUMNS), unclassified


def _point_from_row(
        row: dict[str, Any],
        dimensions: dict[str, str],
        *,
        release: str,
        dut_version: str,
        logical_type: str,
    ) -> dict[str, Any] | None:
    metrics = semantic_metrics(row, logical_type)
    for metric in ("throughput", "bandwidth", "latency"):
        key = f"{metric}_value"
        value = metrics[key]
        if value is not None and (not math.isfinite(value) or value < 0):
            metrics[key] = None
    if not any(
            metrics[f"{metric}_value"] is not None
            for metric in ("throughput", "bandwidth", "latency")
        ):
        return None
    identity = {
        "release": release,
        "dut_version": dut_version,
        **{
            key: dimensions[key]
            for key in ("dut", "area", "test", "infra", "framesize", "cores")
        },
        "test_type": logical_type,
    }
    series_id = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:24]
    name = "-".join((
        dimensions["dut"],
        dimensions["infra"],
        dimensions["area"],
        dimensions["framesize"],
        dimensions["cores"],
        dimensions["test"],
        logical_type,
    ))
    return {
        "series_id": series_id,
        "name": name,
        "release": release,
        "dut": dimensions["dut"],
        "dut_version": dut_version,
        **{
            key: dimensions[key]
            for key in (
                "area", "area_label", "test", "infra", "testbed",
                "framesize", "cores",
            )
        },
        "test_type": logical_type,
        "dut_type": text_value(row.get("dut_type")),
        "tg_type": text_value(row.get("tg_type")),
        "test_id": text_value(row.get("test_id")),
        "start_time": text_value(row.get("start_time")),
        "job": text_value(row.get("job")),
        "build": integer_value(row.get("build")),
        "hosts": hosts_value(row.get("hosts")),
        **metrics,
    }


def _paged_payload(
        *,
        dataset: str,
        source_count: int,
        available_count: int,
        returned: pd.DataFrame,
        filters: dict[str, Any],
        status: dict[str, Any],
    ) -> dict[str, Any]:
    offset = filters["offset"]
    returned_count = len(returned)
    has_more = offset + returned_count < available_count
    return {
        "schema_version": 1,
        "dataset": dataset,
        "total_row_count": source_count,
        "row_count": available_count,
        "returned_count": returned_count,
        "limit": filters["limit"],
        "offset": offset,
        "has_more": has_more,
        "next_offset": offset + returned_count if has_more else None,
        "freshness": status.get("last_success_at"),
        "data_status": status.get("status"),
        "filters": filters,
        "columns": list(returned.columns),
        "records": records_from_dataframe(returned),
    }


def _parse_integer(
        field: str,
        value: Any,
        *,
        default: int,
        minimum: int,
        maximum: int | None = None,
    ) -> tuple[int, dict[str, Any] | None]:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default, {
            "field": field,
            "message": f"{field} must be an integer.",
            "value": value,
        }
    if parsed < minimum or (maximum is not None and parsed > maximum):
        message = f"{field} must be at least {minimum}."
        if maximum is not None:
            message = f"{field} must be between {minimum} and {maximum}."
        return parsed, {"field": field, "message": message, "value": value}
    return parsed, None


def _parse_bool(value: Any) -> tuple[bool, dict[str, Any] | None]:
    if isinstance(value, bool):
        return value, None
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True, None
    if normalized in {"0", "false", "no", "n"}:
        return False, None
    return False, {
        "field": "select_defaults",
        "message": "select_defaults must be boolean-compatible.",
        "value": value,
    }


def _parse_series(value: Any) -> tuple[list[str], dict[str, Any] | None]:
    if value is None:
        return [], None
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, (list, tuple)):
        return [], {
            "field": "series",
            "message": "series must be a list of series identifiers.",
            "value": value,
        }
    normalized = [str(item).strip() for item in values if str(item).strip()]
    return list(dict.fromkeys(normalized)), None


def _selection(dimension: str, value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if dimension == "framesize" and re.fullmatch(r"\d+b", normalized):
        normalized = f"{normalized[:-1]}B"
    return normalized or None


def _default_value(dimension: str, available: list[str]) -> str | None:
    if not available:
        return None
    if dimension == "dut":
        return next(
            (value for value in PREFERRED_DUTS if value in available),
            available[0],
        )
    if dimension in {"release", "dut_version"}:
        return available[-1]
    return available[0]


def _available_values(data: pd.DataFrame, column: str) -> list[str]:
    if data.empty or column not in data.columns:
        return []
    values = {
        value for value in data[column].dropna().astype(str)
        if value
    }
    if column == "dut":
        return [value for value in DUT_ORDER if value in values]
    if column == "test_type":
        return [value for value in TEST_TYPE_ORDER if value in values]
    return sorted(values, key=natural_key)
