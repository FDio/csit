"""Cascading filters and tabular presentation helpers for Coverage data."""

from __future__ import annotations

import math
import re
import threading
from typing import Any
from urllib.parse import quote

import pandas as pd
from hdrh.histogram import HdrHistogram

from .result_series import (
    DUT_ORDER,
    area_label,
    consume_driver,
    integer_value,
    is_passed,
    natural_key,
    text_value,
)
from .serialization import records_from_dataframe, validation_error_payload
from .statistics import parse_job_dimensions


DEFAULT_COVERAGE_LIMIT = 1000
MAX_COVERAGE_LIMIT = 10000
COVERAGE_DIMENSIONS = ("release", "dut", "dut_version", "area", "infra")
PDR_LEVELS = (10, 50, 90)
PERCENTILES = (50, 90, 99)

_TOPOLOGY_PREFIX = re.compile(r"^\d+n\d+l[a-z]*$")
_FRAME_SIZE = re.compile(r"^(?:\d+b|imix|jumbo)$")
_CORE_COUNT = re.compile(r"^\d+c$")
_RATE_SCALE = 1_000_000.0
_BANDWIDTH_SCALE = 1_000_000_000.0

_LATENCY_FIELDS = tuple(
    f"latency_{direction}_pdr_{pdr}_p{percentile}"
    for direction in ("forward", "reverse")
    for pdr in PDR_LEVELS
    for percentile in PERCENTILES
)
_ROW_COLUMNS = (
    "release",
    "dut",
    "dut_version",
    "area",
    "area_label",
    "infra",
    "nic",
    "driver",
    "suite",
    "accordion_title",
    "test_name",
    "test",
    "framesize",
    "cores",
    "job",
    "build",
    "test_id",
    "source_url",
    "throughput_unit",
    "throughput_ndr",
    "throughput_ndr_gbps",
    "throughput_pdr",
    "throughput_pdr_gbps",
    *_LATENCY_FIELDS,
)


class CoverageService:
    """Build and cache semantic Coverage rows for one cache publication."""

    def __init__(self) -> None:
        self._cache_key: tuple[int, Any, int] | None = None
        self._rows = pd.DataFrame(columns=_ROW_COLUMNS)
        self._unclassified_row_count = 0
        self._histogram_decode_error_count = 0
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
            infra: Any = None,
        ) -> dict[str, Any]:
        """Return normalized cascading options without selecting defaults."""

        self._ensure_index(data, status)
        requested = {
            "release": _selection(release),
            "dut": _selection(dut),
            "dut_version": _selection(dut_version),
            "area": _selection(area),
            "infra": _selection(infra),
        }
        selected: dict[str, str | None] = {}
        options: dict[str, list[dict[str, str]]] = {
            dimension: [] for dimension in COVERAGE_DIMENSIONS
        }
        filtered = self._rows
        cascade_open = True
        for dimension in COVERAGE_DIMENSIONS:
            if not cascade_open:
                selected[dimension] = None
                continue
            available = _available_values(filtered, dimension)
            options[dimension] = [
                {
                    "value": value,
                    "label": area_label(value) if dimension == "area" else value,
                }
                for value in available
            ]
            value = requested[dimension]
            if value is None or value not in available:
                selected[dimension] = None
                cascade_open = False
                continue
            selected[dimension] = value
            filtered = filtered.loc[
                filtered[dimension].astype("string") == value
            ]

        complete = all(selected.get(field) for field in COVERAGE_DIMENSIONS)
        return {
            "schema_version": 1,
            "dataset": "coverage_catalog",
            "total_row_count": len(self._rows),
            "row_count": len(filtered) if complete else 0,
            "freshness": status.get("last_success_at"),
            "data_status": status.get("status"),
            "filters": selected,
            "filter_options": options,
            "complete": complete,
            "unclassified_row_count": self._unclassified_row_count,
            "histogram_decode_error_count": self._histogram_decode_error_count,
        }

    def tables_payload(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            *,
            release: Any,
            dut: Any,
            dut_version: Any,
            area: Any,
            infra: Any,
            offset: Any = 0,
            limit: Any = DEFAULT_COVERAGE_LIMIT,
        ) -> dict[str, Any]:
        """Return paginated Coverage table rows for a complete selection."""

        self._ensure_index(data, status)
        parsed_offset, offset_error = _parse_integer(
            "offset", offset, default=0, minimum=0,
        )
        parsed_limit, limit_error = _parse_integer(
            "limit",
            limit,
            default=DEFAULT_COVERAGE_LIMIT,
            minimum=1,
            maximum=MAX_COVERAGE_LIMIT,
        )
        filters = {
            "release": _selection(release),
            "dut": _selection(dut),
            "dut_version": _selection(dut_version),
            "area": _selection(area),
            "infra": _selection(infra),
            "offset": parsed_offset,
            "limit": parsed_limit,
        }
        errors = [
            error for error in (offset_error, limit_error) if error is not None
        ]
        filtered = self._rows
        for dimension in COVERAGE_DIMENSIONS:
            value = filters[dimension]
            if value is None:
                errors.append({
                    "field": dimension,
                    "message": f"{dimension} is required.",
                    "value": value,
                })
                continue
            available = _available_values(filtered, dimension)
            if value not in available:
                errors.append({
                    "field": dimension,
                    "message": (
                        f"{dimension} must be one of the values available "
                        "after the preceding coverage filters."
                    ),
                    "value": value,
                    "available": available,
                })
                continue
            filtered = filtered.loc[
                filtered[dimension].astype("string") == value
            ]
        if errors:
            return validation_error_payload(errors, filters)

        filtered = _sort_rows(filtered)
        returned = filtered.iloc[parsed_offset:parsed_offset + parsed_limit]
        returned_count = len(returned)
        has_more = parsed_offset + returned_count < len(filtered)
        payload = {
            "schema_version": 1,
            "dataset": "coverage_tables",
            "total_row_count": len(self._rows),
            "row_count": len(filtered),
            "returned_count": returned_count,
            "limit": parsed_limit,
            "offset": parsed_offset,
            "has_more": has_more,
            "next_offset": (
                parsed_offset + returned_count if has_more else None
            ),
            "freshness": status.get("last_success_at"),
            "data_status": status.get("status"),
            "filters": filters,
            "columns": list(returned.columns),
            "records": records_from_dataframe(returned),
            "has_forward_latency": _has_latency(filtered, "forward"),
            "has_reverse_latency": _has_latency(filtered, "reverse"),
            "unclassified_row_count": self._unclassified_row_count,
            "histogram_decode_error_count": self._histogram_decode_error_count,
        }
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
            rows, unclassified, decode_errors = _build_rows(data)
            self._rows = rows
            self._unclassified_row_count = unclassified
            self._histogram_decode_error_count = decode_errors
            self._cache_key = cache_key


def _build_rows(data: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    rows: list[dict[str, Any]] = []
    unclassified = 0
    decode_errors = 0
    for source in data.to_dict(orient="records"):
        if not is_passed(source.get("passed")):
            continue
        dimensions = _parse_dimensions(source)
        release = text_value(source.get("release"))
        dut_version = text_value(source.get("dut_version"))
        job = text_value(source.get("job"))
        build = integer_value(source.get("build"))
        test_id = text_value(source.get("test_id"))
        if (
                dimensions is None or not release or not dut_version or
                not job or build is None or not test_id
            ):
            unclassified += 1
            continue
        latency, errors = _latency_values(source)
        decode_errors += errors
        rows.append({
            "release": release,
            "dut": dimensions["dut"],
            "dut_version": dut_version,
            "area": dimensions["area"],
            "area_label": dimensions["area_label"],
            "infra": dimensions["infra"],
            "nic": dimensions["nic"],
            "driver": dimensions["driver"],
            "suite": dimensions["suite"],
            "accordion_title": dimensions["accordion_title"],
            "test_name": dimensions["test_name"],
            "test": dimensions["test"],
            "framesize": dimensions["framesize"],
            "cores": dimensions["cores"],
            "job": job,
            "build": build,
            "test_id": test_id,
            "source_url": _source_url(job, build, test_id),
            "throughput_unit": text_value(
                source.get("result_pdr_lower_rate_unit")
                or source.get("result_ndr_lower_rate_unit")
            ),
            "throughput_ndr": _scaled(
                source.get("result_ndr_lower_rate_value"), _RATE_SCALE,
            ),
            "throughput_ndr_gbps": _scaled(
                source.get("result_ndr_lower_bandwidth_value"),
                _BANDWIDTH_SCALE,
            ),
            "throughput_pdr": _scaled(
                source.get("result_pdr_lower_rate_value"), _RATE_SCALE,
            ),
            "throughput_pdr_gbps": _scaled(
                source.get("result_pdr_lower_bandwidth_value"),
                _BANDWIDTH_SCALE,
            ),
            **latency,
        })
    return pd.DataFrame(rows, columns=_ROW_COLUMNS), unclassified, decode_errors


def _parse_dimensions(row: dict[str, Any]) -> dict[str, str | None] | None:
    test_id = text_value(row.get("test_id"))
    dut = text_value(row.get("dut_type"))
    job = text_value(row.get("job"))
    if not test_id or not dut or not job or dut not in DUT_ORDER:
        return None
    parts = test_id.split(".")
    if len(parts) < 6:
        return None
    area = "dpdk" if dut == "dpdk" else parts[3].strip().lower()
    suite_tokens = [token for token in parts[-2].lower().split("-") if token]
    if suite_tokens and _TOPOLOGY_PREFIX.fullmatch(suite_tokens[0]):
        suite_tokens.pop(0)
    if not suite_tokens:
        return None
    nic = suite_tokens.pop(0)
    driver, suite_tail = consume_driver(suite_tokens)
    suite_tail = _strip_test_type(suite_tail)
    suite = "-".join([nic, *([driver] if driver != "dpdk" else []), *suite_tail])

    final_tokens = [token for token in parts[-1].lower().split("-") if token]
    if not final_tokens:
        return None
    frame_token = final_tokens.pop(0)
    if not _FRAME_SIZE.fullmatch(frame_token):
        return None
    framesize = frame_token[:-1] + "B" if frame_token.endswith("b") else frame_token
    cores = (
        final_tokens.pop(0)
        if final_tokens and _CORE_COUNT.fullmatch(final_tokens[0])
        else None
    )
    _case_driver, final_tokens = consume_driver(final_tokens)
    final_tokens = _strip_test_type(final_tokens)
    test = "-".join(final_tokens)
    topology = parse_job_dimensions(job).get("testbed")
    if not test or not topology:
        return None
    infra = f"{topology}-{nic}-{driver}"
    test_name = "-".join((framesize, cores or "", test))
    return {
        "dut": dut,
        "area": area,
        "area_label": area_label(area),
        "infra": infra,
        "nic": nic,
        "driver": driver,
        "suite": suite,
        "accordion_title": f"{nic}-{driver}-{test}",
        "test_name": test_name,
        "test": test,
        "framesize": framesize,
        "cores": cores,
    }


def _strip_test_type(tokens: list[str]) -> list[str]:
    stripped = list(tokens)
    if stripped and stripped[-1] in {"mrr", "ndrpdr", "soak"}:
        stripped.pop()
    return stripped


def _latency_values(source: dict[str, Any]) -> tuple[dict[str, int | None], int]:
    values: dict[str, int | None] = {}
    errors = 0
    for direction in ("forward", "reverse"):
        for pdr in PDR_LEVELS:
            column = f"result_latency_{direction}_pdr_{pdr}_hdrh"
            histogram, invalid = _decode_histogram(source.get(column))
            errors += int(invalid)
            for percentile in PERCENTILES:
                key = f"latency_{direction}_pdr_{pdr}_p{percentile}"
                values[key] = (
                    int(histogram.get_value_at_percentile(percentile))
                    if histogram is not None
                    else None
                )
    return values, errors


def _decode_histogram(value: Any) -> tuple[HdrHistogram | None, bool]:
    if value is None:
        return None, False
    try:
        if pd.isna(value):
            return None, False
    except (TypeError, ValueError):
        pass
    encoded = str(value).strip()
    if not encoded:
        return None, False
    try:
        return HdrHistogram.decode(encoded.encode("ascii")), False
    except (TypeError, ValueError, UnicodeError):
        return None, True
    except Exception:
        return None, True


def _scaled(value: Any, divisor: float) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return round(number / divisor, 2)


def _source_url(job: str, build: int, test_id: str) -> str:
    test_path = "/".join(quote(part, safe="-_") for part in test_id.split("."))
    return (
        "https://logs.fd.io/vex-yul-rot-jenkins-1/"
        f"{quote(job, safe='-_')}/{build}/{test_path}.info.json.gz"
    )


def _selection(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    return normalized or None


def _available_values(data: pd.DataFrame, column: str) -> list[str]:
    if data.empty or column not in data.columns:
        return []
    values = {
        value for value in data[column].dropna().astype(str) if value
    }
    if column == "dut":
        return [value for value in DUT_ORDER if value in values]
    return sorted(values, key=natural_key)


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


def _sort_rows(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data.copy()
    ordered = data.copy()
    ordered["_group_key"] = ordered["accordion_title"].map(natural_key)
    ordered["_test_key"] = ordered["test_name"].map(natural_key)
    ordered = ordered.sort_values(
        ["_group_key", "_test_key", "job", "build"], kind="stable",
    )
    return ordered.drop(columns=["_group_key", "_test_key"])


def _has_latency(data: pd.DataFrame, direction: str) -> bool:
    columns = [
        column for column in _LATENCY_FIELDS
        if column.startswith(f"latency_{direction}_")
    ]
    return bool(columns) and any(data[column].notna().any() for column in columns)
