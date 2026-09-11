"""Catalog and semantic time-series helpers for CSIT trending data."""

from __future__ import annotations

import hashlib
import json
import re
import threading
from typing import Any

import pandas as pd

from ..utils.constants import Constants
from .serialization import records_from_dataframe, validation_error_payload
from .statistics import parse_job_dimensions
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
TEST_TYPE_ORDER = ("hoststack", "mrr", "ndr", "pdr", "soak")
DUT_ORDER = ("dpdk", "trex", "vpp")
PREFERRED_DUTS = ("vpp", "dpdk", "trex")

_TOPOLOGY_PREFIX = re.compile(r"^\d+n\d+l[a-z]*$")
_FRAME_SIZE = re.compile(r"^(?:\d+b|imix|jumbo)$")
_CORE_COUNT = re.compile(r"^\d+c$")
_NATURAL_PART = re.compile(r"(\d+)")

_METRIC_COLUMNS = {
    "mrr": {
        "throughput": (
            "result_receive_rate_rate_avg",
            "result_receive_rate_rate_unit",
        ),
        "bandwidth": (
            "result_receive_rate_bandwidth_avg",
            "result_receive_rate_bandwidth_unit",
        ),
    },
    "ndr": {
        "throughput": (
            "result_ndr_lower_rate_value",
            "result_ndr_lower_rate_unit",
        ),
        "bandwidth": (
            "result_ndr_lower_bandwidth_value",
            "result_ndr_lower_bandwidth_unit",
        ),
    },
    "pdr": {
        "throughput": (
            "result_pdr_lower_rate_value",
            "result_pdr_lower_rate_unit",
        ),
        "bandwidth": (
            "result_pdr_lower_bandwidth_value",
            "result_pdr_lower_bandwidth_unit",
        ),
        "latency": (
            "result_latency_forward_pdr_50_avg",
            "result_latency_forward_pdr_50_unit",
        ),
    },
    "soak": {
        "throughput": (
            "result_critical_rate_lower_rate_value",
            "result_critical_rate_lower_rate_unit",
        ),
        "bandwidth": (
            "result_critical_rate_lower_bandwidth_value",
            "result_critical_rate_lower_bandwidth_unit",
        ),
    },
    "hoststack": {
        "throughput": ("result_rate_value", "result_rate_unit"),
        "bandwidth": ("result_bandwidth_value", "result_bandwidth_unit"),
        "latency": ("result_latency_value", "result_latency_unit"),
    },
}

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
        payload = _paged_payload(
            dataset="trending_series",
            source_count=len(self._points),
            available_count=len(filtered),
            returned=returned,
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
            self._points = points
            self._catalog = (
                points.loc[:, list(_SERIES_COLUMNS)]
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
            self._cache_key = cache_key


def _build_points(data: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    points: list[dict[str, Any]] = []
    unclassified = 0
    for row in data.to_dict(orient="records"):
        if not _is_passed(row.get("passed")):
            continue
        dimensions = _parse_dimensions(row)
        if dimensions is None:
            unclassified += 1
            continue
        source_test_type = _text(row.get("test_type"))
        logical_types = {
            "ndrpdr": ("ndr", "pdr"),
            "ndr": ("ndr",),
            "pdr": ("pdr",),
            "mrr": ("mrr",),
            "soak": ("soak",),
            "hoststack": ("hoststack",),
        }.get(source_test_type or "", ())
        if not logical_types:
            unclassified += 1
            continue
        produced = False
        for logical_type in logical_types:
            point = _point_from_row(row, dimensions, logical_type)
            if point is not None:
                points.append(point)
                produced = True
        if not produced:
            unclassified += 1
    return pd.DataFrame(points, columns=_POINT_COLUMNS), unclassified


def _parse_dimensions(row: dict[str, Any]) -> dict[str, str] | None:
    test_id = _text(row.get("test_id"))
    dut = _text(row.get("dut_type"))
    job = _text(row.get("job"))
    if not test_id or not dut or not job or dut not in DUT_ORDER:
        return None
    parts = test_id.split(".")
    if len(parts) < 5:
        return None
    area = "dpdk" if dut == "dpdk" else parts[3].strip().lower()
    identity_tokens = [token for token in parts[4].lower().split("-") if token]
    if identity_tokens and _TOPOLOGY_PREFIX.fullmatch(identity_tokens[0]):
        identity_tokens.pop(0)
    if not identity_tokens:
        return None
    nic = identity_tokens.pop(0)
    driver, _remaining = _consume_driver(identity_tokens)
    final_tokens = [token for token in parts[-1].lower().split("-") if token]
    framesize = final_tokens.pop(0) if final_tokens else None
    if not framesize or not _FRAME_SIZE.fullmatch(framesize):
        return None
    framesize = framesize[:-1] + "B" if framesize.endswith("b") else framesize
    cores = (
        final_tokens.pop(0)
        if final_tokens and _CORE_COUNT.fullmatch(final_tokens[0])
        else "0c"
    )
    _final_driver, final_tokens = _consume_driver(final_tokens)
    if final_tokens and final_tokens[-1] in {"mrr", "ndrpdr", "soak"}:
        final_tokens.pop()
    test = "-".join(final_tokens)
    topology = parse_job_dimensions(job).get("testbed")
    hosts = _hosts(row.get("hosts"))
    testbed = _text(hosts[0]) if hosts else None
    if not test or not topology or not testbed:
        return None
    infra = f"{topology}-{nic}-{driver}"
    return {
        "dut": dut,
        "area": area,
        "area_label": _area_label(area),
        "test": test,
        "infra": infra,
        "testbed": testbed,
        "framesize": framesize,
        "cores": cores,
        "nic": nic,
        "driver": driver,
    }


def _consume_driver(tokens: list[str]) -> tuple[str, list[str]]:
    remaining = list(tokens)
    for driver in sorted(Constants.DRIVERS, key=len, reverse=True):
        driver_tokens = driver.split("-")
        if remaining[:len(driver_tokens)] == driver_tokens:
            return driver, remaining[len(driver_tokens):]
    return "dpdk", remaining


def _point_from_row(
        row: dict[str, Any],
        dimensions: dict[str, str],
        logical_type: str,
    ) -> dict[str, Any] | None:
    metrics: dict[str, Any] = {}
    has_value = False
    for metric in ("throughput", "bandwidth", "latency"):
        columns = _METRIC_COLUMNS[logical_type].get(metric)
        value = _numeric(row.get(columns[0])) if columns else None
        unit = _text(row.get(columns[1])) if columns else None
        metrics[f"{metric}_value"] = value
        metrics[f"{metric}_unit"] = unit
        has_value = has_value or value is not None
    if not has_value:
        return None
    identity = {
        key: dimensions[key]
        for key in (
            "dut", "area", "test", "infra", "framesize", "cores"
        )
    }
    identity["test_type"] = logical_type
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
            if not isinstance(row.get(f"{metric}_analysis"), dict):
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


def _natural_key(value: str) -> tuple[Any, ...]:
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in _NATURAL_PART.split(value)
    )


def _area_label(area: str) -> str:
    label = Constants.LABELS.get(area)
    if label:
        return label
    return area.replace("_", " ").replace("ip4", "IPv4").replace(
        "ip6", "IPv6"
    ).title().replace("Ipv4", "IPv4").replace("Ipv6", "IPv6")


def _text(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    normalized = str(value).strip().lower()
    return normalized or None


def _is_passed(value: Any) -> bool:
    """Return whether a normalized source row represents a passing test."""

    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except (TypeError, ValueError):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _numeric(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if pd.notna(parsed) else None


def _integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _hosts(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        return [normalized] if normalized else None
    if not isinstance(value, (list, tuple, set)) and hasattr(value, "tolist"):
        try:
            value = value.tolist()
        except (TypeError, ValueError):
            return None
    if isinstance(value, (list, tuple, set)):
        hosts = [str(item).strip() for item in value if str(item).strip()]
        return list(dict.fromkeys(hosts)) or None
    normalized = str(value).strip()
    return [normalized] if normalized else None
