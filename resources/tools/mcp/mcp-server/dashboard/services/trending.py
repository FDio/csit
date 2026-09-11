"""Catalog and semantic time-series helpers for CSIT trending data."""

from __future__ import annotations

import re
import threading
from typing import Any

import pandas as pd

from .result_series import (
    DUT_ORDER,
    LOGICAL_TEST_TYPES,
    PREFERRED_DUTS,
    TEST_TYPE_ORDER,
    area_label as _area_label,
    dataframe_records,
    hosts_value as _hosts,
    integer_value as _integer,
    is_passed as _is_passed,
    natural_key as _natural_key,
    parse_result_dimensions as _parse_dimensions,
    semantic_metrics,
    series_id_for_dimensions,
    text_value as _text,
)
from .memory import compact_semantic_frame, dataframe_memory_bytes
from .serialization import records_from_dataframe, validation_error_payload
from .trending_analysis import analyze_trending_points


DEFAULT_TRENDING_LIMIT = 1000
MAX_TRENDING_LIMIT = 10000
CATALOG_DIMENSIONS = (
    "dut",
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
    "dut",
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
    "dut_version",
    "hosts",
    "throughput_value",
    "throughput_unit",
    "bandwidth_value",
    "bandwidth_unit",
    "latency_value",
    "latency_unit",
    "throughput_analysis",
    "bandwidth_analysis",
    "latency_analysis",
    "_source_row",
)
_SERIES_COLUMNS = _POINT_COLUMNS[:11]


class TrendingService:
    """Build and cache a semantic index for one published trending cache."""

    def __init__(self) -> None:
        self._cache_key: tuple[int, Any, int] | None = None
        self._points = pd.DataFrame(columns=_POINT_COLUMNS)
        self._catalog = pd.DataFrame(columns=_SERIES_COLUMNS)
        self._series = pd.DataFrame(columns=_SERIES_COLUMNS)
        self._unclassified_row_count = 0
        self._trend_analysis: dict[str, Any] = {}
        self._memory_bytes = 0
        self._lock = threading.Lock()

    def catalog_payload(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            *,
            dut: Any = None,
            area: Any = None,
            test: Any = None,
            infra: Any = None,
            testbed: Any = None,
            framesize: Any = None,
            cores: Any = None,
            test_type: Any = None,
            select_defaults: Any = False,
            offset: Any = 0,
            limit: Any = DEFAULT_TRENDING_LIMIT,
        ) -> dict[str, Any]:
        """Return filter options and matching logical series definitions."""

        self._ensure_index(data, status)
        parsed_limit, limit_error = _parse_integer(
            "limit", limit, default=DEFAULT_TRENDING_LIMIT, minimum=1,
            maximum=MAX_TRENDING_LIMIT,
        )
        parsed_offset, offset_error = _parse_integer(
            "offset", offset, default=0, minimum=0,
        )
        parsed_defaults, defaults_error = _parse_bool(select_defaults)
        requested = {
            "dut": _selection("dut", dut),
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
                            "after the preceding trending filters."
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
            dataset="trending_catalog",
            source_count=len(self._series),
            available_count=len(matching_series),
            returned=returned,
            filters=filters,
            status=status,
        )
        payload["filter_options"] = options
        payload["option_labels"] = {
            "area": {
                value: _area_label(value)
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
            limit: Any = DEFAULT_TRENDING_LIMIT,
        ) -> dict[str, Any]:
        """Return paged semantic points for selected logical series IDs."""

        self._ensure_index(data, status)
        parsed_limit, limit_error = _parse_integer(
            "limit", limit, default=DEFAULT_TRENDING_LIMIT, minimum=1,
            maximum=MAX_TRENDING_LIMIT,
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
        public_returned = _public_analysis_frame(returned).drop(
            columns=["_source_row"], errors="ignore"
        )
        payload = _paged_payload(
            dataset="trending_series",
            source_count=len(self._points),
            available_count=len(filtered),
            returned=public_returned,
            filters=filters,
            status=status,
        )
        payload["series"] = records_from_dataframe(selected_series)
        payload["unknown_series"] = unknown
        payload["trend_analysis"] = _selected_trend_analysis(
            self._trend_analysis,
            filtered,
            selected_ids,
        )
        return payload

    def telemetry_source_matches(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            *,
            series: list[str],
            testbed: str | None,
            start_time: pd.Timestamp,
            end_time: pd.Timestamp,
        ) -> dict[str, Any]:
        """Resolve selected semantic series to authoritative source rows."""

        self._ensure_index(data, status)
        requested = list(dict.fromkeys(str(value) for value in series))
        known = set(self._series["series_id"].astype(str))
        selected = [value for value in requested if value in known]
        unknown = [value for value in requested if value not in known]
        matches = self._points.loc[
            self._points["series_id"].isin(selected)
        ].copy()
        if testbed is not None:
            matches = matches.loc[
                matches["testbed"].astype("string") == str(testbed)
            ]
        available_times = pd.to_datetime(
            matches["start_time"], errors="coerce", utc=True
        )
        available_start = (
            available_times.min().isoformat()
            if not available_times.dropna().empty else None
        )
        available_end = (
            available_times.max().isoformat()
            if not available_times.dropna().empty else None
        )
        matches = matches.loc[
            available_times.between(start_time, end_time, inclusive="both")
        ]
        return {
            "matches": matches.loc[:, [
                "_source_row", "series_id", "name", "test_type"
            ]].drop_duplicates(),
            "series": records_from_dataframe(
                self._series.loc[self._series["series_id"].isin(selected)]
            ),
            "unknown_series": unknown,
            "available_start_time": available_start,
            "available_end_time": available_end,
        }

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
            points, trend_analysis = analyze_trending_points(points)
            points = _compact_analysis_columns(points)
            self._points = compact_semantic_frame(
                points,
                categorical_columns=(
                    "series_id", "name", "dut", "area", "area_label",
                    "test", "infra", "testbed", "framesize", "cores",
                    "test_type", "dut_type", "tg_type", "test_id", "job",
                    "dut_version", "throughput_unit", "bandwidth_unit",
                    "latency_unit", "throughput_classification",
                    "bandwidth_classification", "latency_classification",
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
            self._trend_analysis = trend_analysis
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
            self._trend_analysis = {}
            self._memory_bytes = 0

    def memory_usage_bytes(self) -> int:
        with self._lock:
            return self._memory_bytes


def _build_points(data: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    points: list[dict[str, Any]] = []
    unclassified = 0
    for source_row, row in enumerate(dataframe_records(data)):
        if not _is_passed(row.get("passed")):
            continue
        dimensions = _parse_dimensions(row)
        if dimensions is None:
            unclassified += 1
            continue
        source_test_type = _text(row.get("test_type"))
        logical_types = LOGICAL_TEST_TYPES.get(source_test_type or "", ())
        if not logical_types:
            unclassified += 1
            continue
        produced = False
        for logical_type in logical_types:
            point = _point_from_row(
                row, dimensions, logical_type, source_row=source_row
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
        logical_type: str,
        *,
        source_row: Any,
    ) -> dict[str, Any] | None:
    metrics = semantic_metrics(row, logical_type)
    has_value = any(
        metrics[f"{metric}_value"] is not None
        for metric in ("throughput", "bandwidth", "latency")
    )
    if not has_value:
        return None
    series_id = series_id_for_dimensions(dimensions, logical_type)
    name = "-".join((
        dimensions["dut"],
        dimensions["infra"],
        dimensions["area"],
        dimensions["framesize"],
        dimensions["cores"],
        dimensions["test"],
    ))
    return {
        "series_id": series_id,
        "name": name,
        **{key: dimensions[key] for key in _SERIES_COLUMNS if key in dimensions},
        "test_type": logical_type,
        "dut_type": _text(row.get("dut_type")),
        "tg_type": _text(row.get("tg_type")),
        "test_id": _text(row.get("test_id")),
        "start_time": _text(row.get("start_time")),
        "job": _text(row.get("job")),
        "build": _integer(row.get("build")),
        "dut_version": _text(row.get("dut_version")),
        "hosts": _hosts(row.get("hosts")),
        **metrics,
        "_source_row": source_row,
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


def _selected_trend_analysis(
        analysis: dict[str, Any],
        points: pd.DataFrame,
        selected_ids: list[str],
    ) -> dict[str, Any]:
    selected = set(selected_ids)
    classified: set[tuple[str, str, str | None]] = set()
    for row in points.to_dict(orient="records"):
        series_id = str(row.get("series_id"))
        for metric in ("throughput", "bandwidth", "latency"):
            if pd.isna(row.get(f"{metric}_trend")):
                continue
            classified.add((
                series_id,
                metric,
                _text(row.get(f"{metric}_unit")),
            ))
    errors = [
        error for error in analysis.get("errors", [])
        if str(error.get("series_id")) in selected
    ]
    return {
        "engine": analysis.get("engine", "jumpavg"),
        "version": analysis.get("version"),
        "classified_series_metrics": len(classified),
        "skipped_series_metrics": len(errors),
        "errors": errors,
    }


def _compact_analysis_columns(points: pd.DataFrame) -> pd.DataFrame:
    """Store analysis as primitive columns instead of retained dictionaries."""

    for metric in ("throughput", "bandwidth", "latency"):
        source = f"{metric}_analysis"
        values = points[source] if source in points.columns else pd.Series(
            [None] * len(points), index=points.index
        )
        points[f"{metric}_trend"] = pd.to_numeric(
            values.map(
                lambda value: value.get("trend")
                if isinstance(value, dict) else None
            ),
            errors="coerce",
        )
        points[f"{metric}_stdev"] = pd.to_numeric(
            values.map(
                lambda value: value.get("stdev")
                if isinstance(value, dict) else None
            ),
            errors="coerce",
        )
        points[f"{metric}_classification"] = values.map(
            lambda value: value.get("classification")
            if isinstance(value, dict) else None
        )
    return points.drop(
        columns=[
            f"{metric}_analysis"
            for metric in ("throughput", "bandwidth", "latency")
        ],
        errors="ignore",
    )


def _public_analysis_frame(points: pd.DataFrame) -> pd.DataFrame:
    """Recreate compatible analysis dictionaries for the bounded response page."""

    public = points.copy(deep=False)
    for metric in ("throughput", "bandwidth", "latency"):
        trend_values = public.get(
            f"{metric}_trend", pd.Series(index=public.index, dtype=float)
        )
        stdev_values = public.get(
            f"{metric}_stdev", pd.Series(index=public.index, dtype=float)
        )
        classifications = public.get(
            f"{metric}_classification",
            pd.Series(index=public.index, dtype="object"),
        )
        public[f"{metric}_analysis"] = [
            None if pd.isna(trend) else {
                "trend": float(trend),
                "stdev": None if pd.isna(stdev) else float(stdev),
                "classification": (
                    None if pd.isna(classification) else str(classification)
                ),
            }
            for trend, stdev, classification in zip(
                trend_values, stdev_values, classifications, strict=True
            )
        ]
    public = public.drop(
        columns=[
            f"{metric}_{field}"
            for metric in ("throughput", "bandwidth", "latency")
            for field in ("trend", "stdev", "classification")
        ],
        errors="ignore",
    )
    return public.loc[:, [
        column for column in _POINT_COLUMNS if column in public.columns
    ]]


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
        return next((value for value in PREFERRED_DUTS if value in available), available[0])
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
    return sorted(values, key=_natural_key)
