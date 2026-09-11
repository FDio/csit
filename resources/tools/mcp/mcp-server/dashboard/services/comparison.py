"""Iterative-data comparison catalog, summaries, and raw rows."""

from __future__ import annotations

import math
import re
import threading
from typing import Any

import pandas as pd

from .result_series import (
    DUT_ORDER,
    LOGICAL_TEST_TYPES,
    dataframe_records,
    is_passed,
    natural_key,
    parse_result_dimensions,
    semantic_metrics,
    text_value,
)
from .memory import compact_semantic_frame, dataframe_memory_bytes
from .serialization import json_safe_value, validation_error_payload


DEFAULT_COMPARISON_LIMIT = 1000
MAX_COMPARISON_LIMIT = 10000
REFERENCE_DIMENSIONS = (
    "release",
    "dut",
    "dut_version",
    "infra",
    "framesize",
    "cores",
    "test_type",
)
COMPARISON_PARAMETERS = (
    "dut_version",
    "infra",
    "framesize",
    "cores",
    "test_type",
)
PARAMETER_LABELS = {
    "dut_version": "DUT Version",
    "infra": "Infrastructure",
    "framesize": "Framesize",
    "cores": "Number of cores",
    "test_type": "Test Type",
}
RAW_EXPORT_COLUMNS = (
    "job",
    "build",
    "dut_type",
    "dut_version",
    "tg_type",
    "hosts",
    "start_time",
    "passed",
    "test_id",
    "test_type",
    "release",
    "result_pdr_lower_rate_unit",
    "result_pdr_lower_rate_value",
    "result_ndr_lower_rate_unit",
    "result_ndr_lower_rate_value",
    "result_pdr_lower_bandwidth_unit",
    "result_pdr_lower_bandwidth_value",
    "result_ndr_lower_bandwidth_unit",
    "result_ndr_lower_bandwidth_value",
)

_POINT_COLUMNS = (
    "source_index",
    "release",
    "dut",
    "dut_version",
    "area",
    "test",
    "infra",
    "framesize",
    "cores",
    "test_type",
    "value",
    "unit",
    "passed",
)
_GIT_SUFFIX = re.compile(r"-g[0-9a-f]+$", re.IGNORECASE)


class ComparisonService:
    """Build a cached semantic comparison index for Iterative data."""

    def __init__(self) -> None:
        self._cache_key: tuple[int, Any, int] | None = None
        self._points = pd.DataFrame(columns=_POINT_COLUMNS)
        self._source_data = pd.DataFrame(columns=RAW_EXPORT_COLUMNS)
        self._unclassified_row_count = 0
        self._memory_bytes = 0
        self._lock = threading.Lock()

    def catalog_payload(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            **requested_values: Any,
        ) -> dict[str, Any]:
        """Return reference cascades and meaningful comparison choices."""

        self._ensure_index(data, status)
        requested = {
            dimension: _selection(dimension, requested_values.get(dimension))
            for dimension in REFERENCE_DIMENSIONS
        }
        requested_parameter = _selection(
            "parameter", requested_values.get("parameter")
        )
        requested_value = _selection("value", requested_values.get("value"))
        analysis_points = _analysis_points(self._points)
        selected: dict[str, str | None] = {}
        options: dict[str, list[dict[str, str]]] = {
            dimension: [] for dimension in REFERENCE_DIMENSIONS
        }
        filtered = analysis_points
        cascade_open = True
        for dimension in REFERENCE_DIMENSIONS:
            if not cascade_open:
                selected[dimension] = None
                continue
            available = _available_values(filtered, dimension)
            options[dimension] = _option_records(available, dimension)
            value = requested[dimension]
            if value is None or value not in available:
                selected[dimension] = None
                cascade_open = False
                continue
            selected[dimension] = value
            filtered = filtered.loc[
                filtered[dimension].astype("string") == value
            ]

        reference_complete = all(
            selected.get(dimension) for dimension in REFERENCE_DIMENSIONS
        )
        parameter_options: list[dict[str, str]] = []
        value_options: list[dict[str, str]] = []
        parameter = None
        value = None
        if reference_complete:
            reference = _filter_reference(analysis_points, selected)
            for candidate_parameter in COMPARISON_PARAMETERS:
                candidates = _meaningful_candidates(
                    analysis_points,
                    reference,
                    selected,
                    candidate_parameter,
                )
                if candidates:
                    parameter_options.append({
                        "value": candidate_parameter,
                        "label": PARAMETER_LABELS[candidate_parameter],
                    })
            available_parameters = {
                item["value"] for item in parameter_options
            }
            if requested_parameter in available_parameters:
                parameter = requested_parameter
                candidates = _meaningful_candidates(
                    analysis_points, reference, selected, parameter,
                )
                value_options = [
                    {"value": candidate, "label": _candidate_label(parameter, candidate)}
                    for candidate in candidates
                ]
                available_values = {item["value"] for item in value_options}
                if requested_value in available_values:
                    value = requested_value

        filters = {
            **selected,
            "parameter": parameter,
            "value": value,
        }
        options["parameter"] = parameter_options
        options["value"] = value_options
        complete = reference_complete and parameter is not None and value is not None
        matching_test_count = 0
        matching_row_count = 0
        if complete:
            selection = _comparison_selection(
                analysis_points, selected, parameter, value
            )
            matching_test_count = len(selection["pair_keys"])
            matching_row_count = len(selection["reference"]) + len(
                selection["compared"]
            )
        return {
            "schema_version": 1,
            "dataset": "comparison_catalog",
            "total_row_count": len(self._source_data),
            "row_count": matching_row_count,
            "freshness": status.get("last_success_at"),
            "data_status": status.get("status"),
            "filters": filters,
            "filter_options": options,
            "complete": complete,
            "matching_test_count": matching_test_count,
            "unclassified_row_count": self._unclassified_row_count,
        }

    def table_payload(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            *,
            remove_extreme_outliers: Any = False,
            offset: Any = 0,
            limit: Any = DEFAULT_COMPARISON_LIMIT,
            **requested_values: Any,
        ) -> dict[str, Any]:
        """Return paginated summary rows for one complete comparison."""

        self._ensure_index(data, status)
        parsed_offset, offset_error = _parse_integer(
            "offset", offset, default=0, minimum=0,
        )
        parsed_limit, limit_error = _parse_integer(
            "limit", limit, default=DEFAULT_COMPARISON_LIMIT,
            minimum=1, maximum=MAX_COMPARISON_LIMIT,
        )
        remove_outliers, outlier_error = _parse_bool(
            "remove_extreme_outliers", remove_extreme_outliers
        )
        catalog = self.catalog_payload(data, status, **requested_values)
        filters = {
            **(catalog.get("filters") or {}),
            "remove_extreme_outliers": remove_outliers,
            "offset": parsed_offset,
            "limit": parsed_limit,
        }
        errors = [
            error for error in (offset_error, limit_error, outlier_error)
            if error is not None
        ]
        if not catalog.get("complete"):
            errors.append({
                "field": "filters",
                "message": "A complete, meaningful comparison selection is required.",
                "value": catalog.get("filters"),
            })
        if errors:
            return validation_error_payload(errors, filters)

        selected = {key: filters[key] for key in REFERENCE_DIMENSIONS}
        parameter = str(filters["parameter"])
        value = str(filters["value"])
        selection = _comparison_selection(
            _analysis_points(self._points), selected, parameter, value
        )
        records = _summary_records(
            selection["reference"],
            selection["compared"],
            parameter=parameter,
            remove_outliers=remove_outliers,
        )
        reference_label = _reference_label(parameter, selected)
        compared_label = _candidate_label(parameter, value)
        units = sorted(
            {str(record["unit"]) for record in records if record.get("unit")},
            key=natural_key,
        )
        returned = records[parsed_offset:parsed_offset + parsed_limit]
        payload = _paged_payload(
            "comparison_table",
            records,
            returned,
            filters,
            status,
        )
        payload.update({
            "reference_label": reference_label,
            "compared_label": compared_label,
            "unit": "|".join(units),
            "title_dimensions": _title_dimensions(selected, parameter, value),
        })
        return payload

    def data_payload(
            self,
            data: pd.DataFrame,
            status: dict[str, Any],
            *,
            offset: Any = 0,
            limit: Any = DEFAULT_COMPARISON_LIMIT,
            **requested_values: Any,
        ) -> dict[str, Any]:
        """Return paginated source rows contributing to one comparison."""

        self._ensure_index(data, status)
        parsed_offset, offset_error = _parse_integer(
            "offset", offset, default=0, minimum=0,
        )
        parsed_limit, limit_error = _parse_integer(
            "limit", limit, default=DEFAULT_COMPARISON_LIMIT,
            minimum=1, maximum=MAX_COMPARISON_LIMIT,
        )
        catalog = self.catalog_payload(data, status, **requested_values)
        filters = {
            **(catalog.get("filters") or {}),
            "offset": parsed_offset,
            "limit": parsed_limit,
        }
        errors = [
            error for error in (offset_error, limit_error) if error is not None
        ]
        if not catalog.get("complete"):
            errors.append({
                "field": "filters",
                "message": "A complete, meaningful comparison selection is required.",
                "value": catalog.get("filters"),
            })
        if errors:
            return validation_error_payload(errors, filters)

        selected = {key: filters[key] for key in REFERENCE_DIMENSIONS}
        parameter = str(filters["parameter"])
        value = str(filters["value"])
        selection = _comparison_selection(
            _analysis_points(self._points), selected, parameter, value
        )
        raw_records = _raw_records(
            self._points,
            self._source_data,
            selected,
            parameter,
            value,
            selection["identity_keys"],
        )
        returned = raw_records[parsed_offset:parsed_offset + parsed_limit]
        return _paged_payload(
            "comparison_data",
            raw_records,
            returned,
            filters,
            status,
        )

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
            points, source_data, unclassified = _build_index(data)
            self._points = compact_semantic_frame(
                points,
                categorical_columns=(
                    "release", "dut", "dut_version", "area", "test",
                    "infra", "framesize", "cores", "test_type", "unit",
                ),
            )
            self._source_data = source_data
            self._unclassified_row_count = unclassified
            self._memory_bytes = (
                dataframe_memory_bytes(self._points) +
                dataframe_memory_bytes(self._source_data)
            )
            self._cache_key = cache_key

    def clear(self) -> None:
        with self._lock:
            self._cache_key = None
            self._points = pd.DataFrame(columns=_POINT_COLUMNS)
            self._source_data = pd.DataFrame(columns=RAW_EXPORT_COLUMNS)
            self._unclassified_row_count = 0
            self._memory_bytes = 0

    def memory_usage_bytes(self) -> int:
        with self._lock:
            return self._memory_bytes


def normalize_dut_version(value: Any) -> str | None:
    """Remove architecture and commit suffixes from a DUT version."""

    normalized = text_value(value)
    if not normalized:
        return None
    normalized = _GIT_SUFFIX.sub("", normalized)
    match = re.fullmatch(r"(.+-release)(?:-.+)?", normalized)
    return match.group(1) if match else normalized


def _build_index(
        data: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    points: list[dict[str, Any]] = []
    source_columns = [
        column for column in RAW_EXPORT_COLUMNS if column in data.columns
    ]
    source_data = data.loc[:, source_columns].copy(deep=False)
    unclassified = 0
    for source_index, source in enumerate(dataframe_records(data)):
        dimensions = parse_result_dimensions(source)
        release = text_value(source.get("release"))
        dut_version = normalize_dut_version(source.get("dut_version"))
        source_type = text_value(source.get("test_type")) or ""
        logical_types = LOGICAL_TEST_TYPES.get(source_type, ())
        if dimensions is None or not release or not dut_version or not logical_types:
            unclassified += 1
            continue
        passed = is_passed(source.get("passed"))
        for logical_type in logical_types:
            metrics = semantic_metrics(source, logical_type)
            value, unit = _normalized_measurement(
                metrics.get("throughput_value"), metrics.get("throughput_unit")
            )
            points.append(_point(
                source_index, release, dut_version, dimensions,
                logical_type, value, unit, passed,
            ))
            if logical_type in {"pdr", "hoststack"}:
                latency, latency_unit = _normalized_measurement(
                    metrics.get("latency_value"), metrics.get("latency_unit")
                )
                points.append(_point(
                    source_index, release, dut_version, dimensions,
                    "latency", latency, latency_unit, passed,
                ))
    return pd.DataFrame(points, columns=_POINT_COLUMNS), source_data, unclassified


def _point(
        source_index: int,
        release: str,
        dut_version: str,
        dimensions: dict[str, str],
        test_type: str,
        value: float | None,
        unit: str | None,
        passed: bool,
    ) -> dict[str, Any]:
    return {
        "source_index": source_index,
        "release": release,
        "dut": dimensions["dut"],
        "dut_version": dut_version,
        "area": dimensions["area"],
        "test": dimensions["test"],
        "infra": dimensions["infra"],
        "framesize": dimensions["framesize"],
        "cores": dimensions["cores"],
        "test_type": test_type,
        "value": value,
        "unit": unit,
        "passed": passed,
    }


def _normalized_measurement(value: Any, unit: Any) -> tuple[float | None, str | None]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = None
    if number is not None and not math.isfinite(number):
        number = None
    normalized_unit = text_value(unit)
    if normalized_unit == "pps":
        return (number / 1_000_000.0 if number is not None else None), "MPPS"
    if normalized_unit == "us":
        return number, "us"
    if normalized_unit:
        return number, normalized_unit.upper()
    return number, None


def _analysis_points(points: pd.DataFrame) -> pd.DataFrame:
    if points.empty:
        return points.copy()
    values = pd.to_numeric(points["value"], errors="coerce")
    return points.loc[
        points["passed"].eq(True) & values.notna() & points["unit"].notna()
    ].copy()


def _filter_reference(
        points: pd.DataFrame,
        selected: dict[str, str | None],
    ) -> pd.DataFrame:
    filtered = points
    for dimension in REFERENCE_DIMENSIONS:
        filtered = filtered.loc[
            filtered[dimension].astype("string") == selected[dimension]
        ]
    return filtered.copy()


def _meaningful_candidates(
        points: pd.DataFrame,
        reference: pd.DataFrame,
        selected: dict[str, str | None],
        parameter: str,
    ) -> list[str]:
    candidates = _filter_common(points, selected, parameter)
    reference_keys = set(_pair_keys(reference, parameter, include_unit=True))
    values = _parameter_values(candidates, parameter)
    reference_value = _reference_parameter_value(parameter, selected)
    meaningful = []
    for candidate in values:
        if candidate == reference_value:
            continue
        candidate_rows = _filter_candidate(candidates, parameter, candidate)
        if reference_keys.intersection(
                _pair_keys(candidate_rows, parameter, include_unit=True)
            ):
            meaningful.append(candidate)
    return sorted(meaningful, key=natural_key)


def _comparison_selection(
        points: pd.DataFrame,
        selected: dict[str, str | None],
        parameter: str,
        value: str,
    ) -> dict[str, Any]:
    reference = _filter_reference(points, selected)
    compared = _filter_candidate(
        _filter_common(points, selected, parameter), parameter, value
    )
    pair_keys = set(_pair_keys(reference, parameter, include_unit=True)).intersection(
        _pair_keys(compared, parameter, include_unit=True)
    )
    reference = _with_pair_key(reference, parameter, include_unit=True)
    compared = _with_pair_key(compared, parameter, include_unit=True)
    reference = reference.loc[reference["_pair_key"].isin(pair_keys)]
    compared = compared.loc[compared["_pair_key"].isin(pair_keys)]
    identity_keys = {
        key[:-1] for key in pair_keys
    }
    return {
        "reference": reference,
        "compared": compared,
        "pair_keys": pair_keys,
        "identity_keys": identity_keys,
    }


def _filter_common(
        points: pd.DataFrame,
        selected: dict[str, str | None],
        parameter: str,
    ) -> pd.DataFrame:
    filtered = points
    for dimension in REFERENCE_DIMENSIONS:
        if dimension == parameter or (
                parameter == "dut_version" and dimension == "release"
            ):
            continue
        filtered = filtered.loc[
            filtered[dimension].astype("string") == selected[dimension]
        ]
    return filtered.copy()


def _filter_candidate(
        points: pd.DataFrame,
        parameter: str,
        value: str,
    ) -> pd.DataFrame:
    if parameter == "dut_version":
        release, version = _split_version_candidate(value)
        return points.loc[
            points["release"].astype("string").eq(release) &
            points["dut_version"].astype("string").eq(version)
        ].copy()
    return points.loc[points[parameter].astype("string") == value].copy()


def _pair_dimensions(parameter: str) -> tuple[str, ...]:
    dimensions = list(REFERENCE_DIMENSIONS)
    dimensions.extend(("area", "test"))
    excluded = {parameter}
    if parameter == "dut_version":
        excluded.add("release")
    return tuple(dimension for dimension in dimensions if dimension not in excluded)


def _pair_keys(
        points: pd.DataFrame,
        parameter: str,
        *,
        include_unit: bool,
    ) -> list[tuple[str, ...]]:
    dimensions = list(_pair_dimensions(parameter))
    if include_unit:
        dimensions.append("unit")
    return [
        tuple(str(row.get(dimension) or "") for dimension in dimensions)
        for row in points.to_dict(orient="records")
    ]


def _with_pair_key(
        points: pd.DataFrame,
        parameter: str,
        *,
        include_unit: bool,
    ) -> pd.DataFrame:
    result = points.copy()
    result["_pair_key"] = _pair_keys(result, parameter, include_unit=include_unit)
    return result


def _summary_records(
        reference: pd.DataFrame,
        compared: pd.DataFrame,
        *,
        parameter: str,
        remove_outliers: bool,
    ) -> list[dict[str, Any]]:
    records = []
    reference_groups = {
        key: group for key, group in reference.groupby("_pair_key", sort=False)
    }
    compared_groups = {
        key: group for key, group in compared.groupby("_pair_key", sort=False)
    }
    for key in sorted(reference_groups, key=lambda item: natural_key("|".join(item))):
        if key not in compared_groups:
            continue
        reference_group = reference_groups[key]
        compared_group = compared_groups[key]
        reference_values, reference_removed = _prepared_values(
            reference_group["value"], remove_outliers
        )
        compared_values, compared_removed = _prepared_values(
            compared_group["value"], remove_outliers
        )
        if not reference_values or not compared_values:
            continue
        reference_mean, reference_stdev = _mean_stdev(reference_values)
        compared_mean, compared_stdev = _mean_stdev(compared_values)
        first = reference_group.iloc[0]
        records.append({
            "test_name": _test_name(first),
            "unit": first.get("unit"),
            "reference_mean": _rounded(reference_mean),
            "reference_stdev": _rounded(reference_stdev),
            "compared_mean": _rounded(compared_mean),
            "compared_stdev": _rounded(compared_stdev),
            "relative_change_mean": _rounded(_relative_change(
                reference_mean, compared_mean
            )),
            "relative_change_stdev": _rounded(_relative_stdev(
                reference_mean, reference_stdev, compared_mean, compared_stdev
            )),
            "reference_count": len(reference_values),
            "compared_count": len(compared_values),
            "reference_outliers_removed": reference_removed,
            "compared_outliers_removed": compared_removed,
        })
    return sorted(records, key=lambda record: natural_key(record["test_name"]))


def _prepared_values(series: pd.Series, remove_outliers: bool) -> tuple[list[float], int]:
    values = sorted(float(value) for value in pd.to_numeric(series, errors="coerce").dropna())
    if not remove_outliers or not values:
        return values, 0
    numeric = pd.Series(values, dtype="float64")
    q1 = float(numeric.quantile(0.25, interpolation="linear"))
    q3 = float(numeric.quantile(0.75, interpolation="linear"))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    retained = [value for value in values if lower <= value <= upper]
    return retained, len(values) - len(retained)


def _mean_stdev(values: list[float]) -> tuple[float, float | None]:
    series = pd.Series(values, dtype="float64")
    mean = float(series.mean())
    stdev = float(series.std(ddof=1)) if len(values) > 1 else None
    return mean, stdev


def _relative_change(reference: float, compared: float) -> float | None:
    if reference == 0:
        return None
    return (compared - reference) / reference * 100.0


def _relative_stdev(
        reference_mean: float,
        reference_stdev: float | None,
        compared_mean: float,
        compared_stdev: float | None,
    ) -> float | None:
    if (
            reference_stdev is None or compared_stdev is None or
            reference_mean == 0 or compared_mean == 0
        ):
        return None
    return 100.0 * math.sqrt(
        (reference_stdev / reference_mean) ** 2 +
        (compared_stdev / compared_mean) ** 2
    )


def _raw_records(
        all_points: pd.DataFrame,
        source_data: pd.DataFrame,
        selected: dict[str, str | None],
        parameter: str,
        value: str,
        identity_keys: set[tuple[str, ...]],
    ) -> list[dict[str, Any]]:
    rows = []
    seen: set[tuple[int, str]] = set()
    reference = _filter_reference(all_points, selected)
    compared = _filter_candidate(
        _filter_common(all_points, selected, parameter), parameter, value
    )
    for side, points in (("reference", reference), ("compare", compared)):
        points = _with_pair_key(points, parameter, include_unit=False)
        for point in points.to_dict(orient="records"):
            if point["_pair_key"] not in identity_keys:
                continue
            source_index = int(point["source_index"])
            dedupe_key = (source_index, side)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            if source_index < 0 or source_index >= len(source_data):
                continue
            source = source_data.iloc[source_index]
            record = {
                column: json_safe_value(source.get(column))
                for column in RAW_EXPORT_COLUMNS
            }
            record["ref_cmp"] = side
            rows.append(record)
    return sorted(rows, key=_raw_sort_key)


def _raw_sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        0 if record.get("ref_cmp") == "reference" else 1,
        str(record.get("start_time") or ""),
        str(record.get("job") or ""),
        int(record.get("build") or 0),
        str(record.get("test_id") or ""),
    )


def _available_values(data: pd.DataFrame, dimension: str) -> list[str]:
    if data.empty or dimension not in data.columns:
        return []
    values = {str(value) for value in data[dimension].dropna() if str(value)}
    if dimension == "dut":
        return [value for value in DUT_ORDER if value in values]
    test_order = ("hoststack", "mrr", "ndr", "pdr", "soak", "latency")
    if dimension == "test_type":
        return [value for value in test_order if value in values]
    return sorted(values, key=natural_key)


def _option_records(values: list[str], dimension: str) -> list[dict[str, str]]:
    return [
        {
            "value": value,
            "label": "Latency" if dimension == "test_type" and value == "latency" else value,
        }
        for value in values
    ]


def _parameter_values(points: pd.DataFrame, parameter: str) -> list[str]:
    if points.empty:
        return []
    if parameter == "dut_version":
        return sorted({
            f"{row['release']}::{row['dut_version']}"
            for row in points[["release", "dut_version"]].to_dict(orient="records")
        }, key=natural_key)
    return _available_values(points, parameter)


def _reference_parameter_value(
        parameter: str,
        selected: dict[str, str | None],
    ) -> str:
    if parameter == "dut_version":
        return f"{selected['release']}::{selected['dut_version']}"
    return str(selected[parameter])


def _reference_label(parameter: str, selected: dict[str, str | None]) -> str:
    return _candidate_label(parameter, _reference_parameter_value(parameter, selected))


def _candidate_label(parameter: str, value: str) -> str:
    if parameter == "dut_version":
        release, version = _split_version_candidate(value)
        return f"{release} / {version}"
    if parameter == "test_type" and value == "latency":
        return "Latency"
    return value


def _split_version_candidate(value: str) -> tuple[str, str]:
    release, separator, version = value.partition("::")
    return (release, version) if separator and release and version else ("", "")


def _selection(dimension: str, value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if dimension == "framesize" and re.fullmatch(r"\d+b", normalized.lower()):
        return normalized[:-1].lower() + "B"
    return normalized.lower() if dimension != "value" else normalized.lower()


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
        return default, {"field": field, "message": f"{field} must be an integer.", "value": value}
    if parsed < minimum or (maximum is not None and parsed > maximum):
        message = f"{field} must be at least {minimum}."
        if maximum is not None:
            message = f"{field} must be between {minimum} and {maximum}."
        return parsed, {"field": field, "message": message, "value": value}
    return parsed, None


def _parse_bool(field: str, value: Any) -> tuple[bool, dict[str, Any] | None]:
    if isinstance(value, bool):
        return value, None
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True, None
    if normalized in {"0", "false", "no", "n"}:
        return False, None
    return False, {"field": field, "message": f"{field} must be boolean-compatible.", "value": value}


def _test_name(row: pd.Series) -> str:
    framesize = str(row.get("framesize") or "")
    cores = str(row.get("cores") or "")
    test = str(row.get("test") or "")
    return f"{framesize}-{cores}-{test}" if cores != "0c" else f"{framesize}--{test}"


def _rounded(value: float | None) -> float | None:
    return round(value, 2) if value is not None and math.isfinite(value) else None


def _title_dimensions(
        selected: dict[str, str | None],
        parameter: str,
        compared_value: str,
    ) -> list[dict[str, str]]:
    excluded = {parameter}
    if parameter == "dut_version":
        excluded.add("release")
    return [
        {"name": dimension, "value": str(selected[dimension])}
        for dimension in REFERENCE_DIMENSIONS
        if dimension not in excluded and selected.get(dimension)
    ]


def _paged_payload(
        dataset: str,
        all_records: list[dict[str, Any]],
        returned: list[dict[str, Any]],
        filters: dict[str, Any],
        status: dict[str, Any],
    ) -> dict[str, Any]:
    offset = int(filters["offset"])
    returned_count = len(returned)
    has_more = offset + returned_count < len(all_records)
    columns = list(returned[0]) if returned else []
    return {
        "schema_version": 1,
        "dataset": dataset,
        "total_row_count": len(all_records),
        "row_count": len(all_records),
        "returned_count": returned_count,
        "limit": int(filters["limit"]),
        "offset": offset,
        "has_more": has_more,
        "next_offset": offset + returned_count if has_more else None,
        "freshness": status.get("last_success_at"),
        "data_status": status.get("status"),
        "filters": filters,
        "columns": columns,
        "records": [json_safe_value(record) for record in returned],
    }
