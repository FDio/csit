"""Query helpers for CSIT MCP dataframe-backed tools."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd
try:
    import pyarrow as pa
except ImportError:
    ARROW_EXCEPTIONS = ()
else:
    ARROW_EXCEPTIONS = (pa.ArrowException,)

from .data_cache import DataCacheService
from .serialization import (
    json_safe_value,
    limited_tool_payload,
    validation_error_payload,
)
from .statistics import (
    enrich_job_statistics,
    filter_job_statistics,
    statistics_counts,
)


DEFAULT_TOOL_LIMIT = 1000
MAX_TOOL_LIMIT = 10000
TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}
AGGREGATION_MODES = ("none", "hosts", "test_id", "hosts_by_test_id")
AGGREGATION_GROUP_COLUMNS = {
    "hosts": ("hosts",),
    "test_id": ("test_id",),
    "hosts_by_test_id": ("test_id", "hosts"),
}
SORT_ORDERS = ("asc", "desc")
SORT_FALLBACK_EXCEPTIONS = (TypeError, ValueError) + ARROW_EXCEPTIONS


def result_tool_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        data_cache: DataCacheService,
        text_filters: list[tuple[str, Any]],
        int_filters: list[tuple[str, Any]],
        passed: bool | None,
        limit: int,
        offset: int,
        aggregation: str,
        sort_by: str | None,
        sort_order: str,
        columns: Any
    ) -> dict[str, Any]:
    """Build a structured response for trending, iterative, and coverage."""

    parsed_limit, limit_error = _parse_optional_int(
        "limit",
        limit,
        default=DEFAULT_TOOL_LIMIT,
        maximum=MAX_TOOL_LIMIT,
    )
    parsed_offset, offset_error = _parse_optional_int(
        "offset",
        offset,
        default=0,
        minimum=0,
    )
    parsed_passed, passed_error = _parse_optional_bool(passed)
    parsed_aggregation, aggregation_error = _parse_aggregation(aggregation)
    parsed_sort_order, sort_order_error = _parse_sort_order(sort_order)
    parsed_columns, columns_error = _parse_columns(columns)
    parsed_int_filters = {
        column: _parse_optional_int(column, value, default=None, minimum=0)
        for column, value in int_filters
    }
    filters = {
        column: value
        for column, value in text_filters
    }
    filters.update({
        column: parsed_value
        for column, (parsed_value, _err) in parsed_int_filters.items()
    })
    filters["passed"] = parsed_passed
    filters["limit"] = parsed_limit
    filters["offset"] = parsed_offset
    filters["aggregation"] = parsed_aggregation
    filters["sort_by"] = sort_by
    filters["sort_order"] = parsed_sort_order
    filters["columns"] = parsed_columns
    errors = [
        err for err in (
            limit_error,
            offset_error,
            passed_error,
            aggregation_error,
            sort_order_error,
            columns_error,
            *(err for _parsed, err in parsed_int_filters.values()),
        )
        if err is not None
    ]

    filtered_data = data
    for column, value in text_filters:
        filtered_data = _filter_by_text(
            filtered_data,
            column=column,
            value=value,
            errors=errors,
        )
    for column, (value, _err) in parsed_int_filters.items():
        filtered_data = _filter_by_int(
            filtered_data,
            column=column,
            value=value,
            errors=errors,
        )
    filtered_data = _filter_by_bool(
        filtered_data,
        column="passed",
        value=parsed_passed,
        errors=errors,
    )
    response_data = _aggregate_results(
        filtered_data,
        parsed_aggregation,
        errors=errors,
    )
    response_data = _sort_results(
        response_data,
        sort_by=sort_by,
        sort_order=parsed_sort_order,
        errors=errors,
    )
    response_data = _select_columns(
        response_data,
        columns=parsed_columns,
        errors=errors,
    )

    if errors:
        return validation_error_payload(errors, filters)

    returned_data = _page_data(response_data, parsed_offset, parsed_limit)

    return limited_tool_payload(
        dataset=dataset,
        source_data=data,
        filtered_data=filtered_data,
        returned_data=returned_data,
        available_data=response_data,
        filters=filters,
        data_cache=data_cache,
    )


def job_statistics_payload(
        *,
        data: pd.DataFrame,
        trending_data: pd.DataFrame | None = None,
        data_cache: DataCacheService,
        days: int | None,
        job: str | None,
        limit: int,
        dut: str | None = None,
        test_type: str | None = None,
        cadence: str | None = None,
        testbed: str | None = None,
        select_defaults: bool = False,
    ) -> dict[str, Any]:
    """Build a structured response for cached job statistics."""

    parsed_limit, limit_error = _parse_optional_int(
        "limit",
        limit,
        default=DEFAULT_TOOL_LIMIT,
        maximum=MAX_TOOL_LIMIT,
    )
    parsed_days, days_error = _parse_optional_int("days", days)
    parsed_select_defaults, defaults_error = _parse_bool_field(
        "select_defaults",
        select_defaults,
        default=False,
    )
    filters = {
        "days": parsed_days,
        "job": job,
        "limit": parsed_limit,
        "dut": dut,
        "test_type": test_type,
        "cadence": cadence,
        "testbed": testbed,
        "select_defaults": parsed_select_defaults,
    }
    errors = [
        err for err in (limit_error, days_error, defaults_error)
        if err is not None
    ]
    enriched_data = enrich_job_statistics(
        data,
        trending_data if trending_data is not None else pd.DataFrame(),
    )
    filtered_data = _filter_by_text(
        enriched_data,
        column="job",
        value=job,
        errors=errors,
    )
    filtered_data = _filter_by_days(
        filtered_data,
        days=parsed_days,
        errors=errors,
    )
    filtered_data, filter_options, selected, dimension_errors = (
        filter_job_statistics(
            filtered_data,
            dut=dut,
            test_type=test_type,
            cadence=cadence,
            testbed=testbed,
            select_defaults=parsed_select_defaults,
        )
    )
    filters.update(selected)
    errors.extend(dimension_errors)

    if errors:
        payload = validation_error_payload(errors, filters)
        payload["filter_options"] = filter_options
        return payload

    returned_data = _page_data(filtered_data, 0, parsed_limit)

    payload = limited_tool_payload(
        dataset="statistics",
        source_data=data,
        filtered_data=filtered_data,
        returned_data=returned_data,
        available_data=filtered_data,
        filters=filters,
        data_cache=data_cache,
    )
    payload["filter_options"] = filter_options
    payload.update(statistics_counts(enriched_data))
    return payload


def _parse_bool_field(
        field: str,
        value: Any,
        *,
        default: bool,
    ) -> tuple[bool, dict[str, Any] | None]:
    if isinstance(value, bool):
        return value, None
    if value is None:
        return default, None
    normalized = str(value).strip().lower()
    if normalized in TRUE_VALUES:
        return True, None
    if normalized in FALSE_VALUES:
        return False, None
    return default, {
        "field": field,
        "message": f"{field} must be a boolean value.",
        "value": value,
    }


def _page_data(data: pd.DataFrame, offset: int, limit: int) -> pd.DataFrame:
    return data.iloc[offset:offset + limit]


def _parse_optional_int(
        field: str,
        value: Any,
        *,
        default: int | None = None,
        minimum: int = 1,
        maximum: int | None = None
    ) -> tuple[int | None, dict[str, Any] | None]:
    if value is None:
        return default, None
    if isinstance(value, bool):
        return default, _int_error(field, value, minimum, maximum)
    if isinstance(value, float) and not value.is_integer():
        return default, _int_error(field, value, minimum, maximum)

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default, _int_error(field, value, minimum, maximum)

    if parsed < minimum or (maximum is not None and parsed > maximum):
        return default, _int_error(field, value, minimum, maximum)

    return parsed, None


def _parse_aggregation(value: Any) -> tuple[str, dict[str, Any] | None]:
    if value is None:
        return "none", None

    parsed = str(value).strip().lower()
    if parsed in AGGREGATION_MODES:
        return parsed, None

    return "none", {
        "field": "aggregation",
        "message": (
            "aggregation must be one of: " +
            ", ".join(AGGREGATION_MODES)
        ),
        "value": value,
    }


def _int_error(
        field: str,
        value: Any,
        minimum: int,
        maximum: int | None
    ) -> dict[str, Any]:
    expected = f"integer >= {minimum}"
    if maximum is not None:
        expected = f"integer between {minimum} and {maximum}"
    return {
        "field": field,
        "message": f"{field} must be an {expected}.",
        "value": value,
    }


def _parse_sort_order(value: Any) -> tuple[str, dict[str, Any] | None]:
    if value is None:
        return "desc", None

    parsed = str(value).strip().lower()
    if parsed in SORT_ORDERS:
        return parsed, None

    return "desc", {
        "field": "sort_order",
        "message": "sort_order must be one of: " + ", ".join(SORT_ORDERS),
        "value": value,
    }


def _parse_columns(value: Any) -> tuple[list[str] | None, dict[str, Any] | None]:
    if value is None:
        return None, None
    if isinstance(value, str):
        return [value], None
    if isinstance(value, (list, tuple)) and all(
            isinstance(item, str) for item in value
        ):
        return list(value), None

    return None, {
        "field": "columns",
        "message": "columns must be a string or a list of strings.",
        "value": json_safe_value(value),
    }


def _parse_optional_bool(value: Any) -> tuple[bool | None, dict[str, Any] | None]:
    if value is None:
        return None, None
    if isinstance(value, bool):
        return value, None

    normalized = str(value).strip().lower()
    if normalized in TRUE_VALUES:
        return True, None
    if normalized in FALSE_VALUES:
        return False, None

    return None, {
        "field": "passed",
        "message": "passed must be a boolean value.",
        "value": value,
    }


def _filter_by_text(
        data: pd.DataFrame,
        *,
        column: str,
        value: Any,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if value is None:
        return data
    if column not in data.columns:
        errors.append(_missing_filter_column_error(column))
        return data
    return data.loc[
        data[column].map(lambda item: _text_filter_matches(item, value))
    ]


def _text_filter_matches(actual: Any, expected: Any) -> bool:
    actual_value = json_safe_value(actual)
    expected_value = json_safe_value(expected)

    if isinstance(expected_value, list):
        return _normalized_text_key(actual_value) == _normalized_text_key(
            expected_value
        )
    if isinstance(actual_value, list):
        expected_text = str(expected_value)
        return (
            expected_text in {str(item) for item in actual_value} or
            _normalized_text_key(actual_value) == expected_text
        )

    return _normalized_text_key(actual_value) == _normalized_text_key(expected_value)


def _normalized_text_key(value: Any) -> str | None:
    safe_value = json_safe_value(value)
    if safe_value is None:
        return None
    if isinstance(safe_value, list):
        return ",".join(sorted(str(item) for item in safe_value))
    return str(safe_value)


def _filter_by_int(
        data: pd.DataFrame,
        *,
        column: str,
        value: int | None,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if value is None:
        return data
    if column not in data.columns:
        errors.append(_missing_filter_column_error(column))
        return data

    numeric_values = pd.to_numeric(data[column], errors="coerce")
    return data.loc[numeric_values == value]


def _filter_by_bool(
        data: pd.DataFrame,
        *,
        column: str,
        value: bool | None,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if value is None:
        return data
    if column not in data.columns:
        errors.append(_missing_filter_column_error(column))
        return data

    normalized = data[column].astype(str).str.strip().str.lower()
    expected_values = TRUE_VALUES if value else FALSE_VALUES
    return data.loc[normalized.isin(expected_values)]


def _filter_by_days(
        data: pd.DataFrame,
        *,
        days: int | None,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if days is None:
        return data
    if "start_time" not in data.columns:
        errors.append(_missing_filter_column_error("start_time", field="days"))
        return data

    timestamps = pd.to_datetime(data["start_time"], errors="coerce", utc=True)
    cutoff = datetime.now(tz=UTC) - timedelta(days=days)
    return data.loc[timestamps >= cutoff]


def _missing_filter_column_error(
        column: str,
        field: str | None = None
    ) -> dict[str, Any]:
    field = field or column
    return {
        "field": field,
        "message": (
            f"{field} filter is unsupported because column '{column}' "
            "is not available in the cached dataset."
        ),
    }


def _aggregate_results(
        data: pd.DataFrame,
        aggregation: str,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if aggregation == "none":
        return data

    group_columns = AGGREGATION_GROUP_COLUMNS[aggregation]
    missing_columns = [
        column for column in group_columns
        if column not in data.columns
    ]
    if missing_columns:
        errors.extend(
            _missing_filter_column_error(column, field="aggregation")
            for column in missing_columns
        )
        return data

    working_data = data.copy()
    for column in group_columns:
        working_data[column] = working_data[column].map(_normalized_text_key)

    if working_data.empty:
        return _empty_aggregation_frame(working_data, group_columns)

    grouped = working_data.groupby(list(group_columns), dropna=False)
    summary = grouped.size().reset_index(name="row_count")

    if "passed" in working_data.columns:
        passed_values = (
            working_data["passed"].astype(str).str.strip().str.lower().isin(TRUE_VALUES)
        )
        passed_counts = (
            working_data.assign(_passed_value=passed_values)
            .groupby(list(group_columns), dropna=False)["_passed_value"]
            .sum()
            .reset_index(name="passed_count")
        )
        summary = summary.merge(passed_counts, on=list(group_columns), how="left")
        summary["passed_count"] = summary["passed_count"].astype(int)
        summary["failed_count"] = summary["row_count"] - summary["passed_count"]
    else:
        summary["passed_count"] = 0
        summary["failed_count"] = 0

    numeric_summary = _numeric_result_summary(working_data, group_columns)
    if not numeric_summary.empty:
        summary = summary.merge(numeric_summary, on=list(group_columns), how="left")

    return summary


def _sort_results(
        data: pd.DataFrame,
        *,
        sort_by: str | None,
        sort_order: str,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if sort_by is None:
        return data
    if sort_by not in data.columns:
        errors.append(_missing_filter_column_error(sort_by, field="sort_by"))
        return data

    ascending = sort_order == "asc"
    if _series_contains_list_values(data[sort_by]):
        return _sort_by_normalized_text_key(
            data,
            sort_by=sort_by,
            ascending=ascending,
        )

    try:
        return data.sort_values(
            by=sort_by,
            ascending=ascending,
            na_position="last",
            kind="mergesort",
        )
    except SORT_FALLBACK_EXCEPTIONS:
        return _sort_by_normalized_text_key(
            data,
            sort_by=sort_by,
            ascending=ascending,
        )


def _select_columns(
        data: pd.DataFrame,
        *,
        columns: list[str] | None,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if columns is None:
        return data

    missing_columns = [
        column for column in columns
        if column not in data.columns
    ]
    if missing_columns:
        errors.extend(
            _missing_filter_column_error(column, field="columns")
            for column in missing_columns
        )
        return data

    return data.loc[:, columns]


def _sort_by_normalized_text_key(
        data: pd.DataFrame,
        *,
        sort_by: str,
        ascending: bool
    ) -> pd.DataFrame:
    return (
        data.assign(_sort_key=data[sort_by].map(_normalized_text_key))
        .sort_values(
            by="_sort_key",
            ascending=ascending,
            na_position="last",
            kind="mergesort",
        )
        .drop(columns=["_sort_key"])
    )


def _series_contains_list_values(series: pd.Series) -> bool:
    if str(series.dtype).startswith("list<"):
        return True

    for value in series.head(100):
        if isinstance(json_safe_value(value), list):
            return True
    return False


def _empty_aggregation_frame(
        data: pd.DataFrame,
        group_columns: tuple[str, ...]
    ) -> pd.DataFrame:
    columns = list(group_columns) + ["row_count", "passed_count", "failed_count"]
    for column in _numeric_result_columns(data):
        columns.extend([
            f"{column}_min",
            f"{column}_mean",
            f"{column}_max",
        ])
    return pd.DataFrame(columns=columns)


def _numeric_result_summary(
        data: pd.DataFrame,
        group_columns: tuple[str, ...]
    ) -> pd.DataFrame:
    numeric_columns = _numeric_result_columns(data)
    if not numeric_columns:
        return pd.DataFrame()

    summary = (
        data.groupby(list(group_columns), dropna=False)[numeric_columns]
        .agg(["min", "mean", "max"])
        .reset_index()
    )
    summary.columns = [
        "_".join(str(item) for item in column if item)
        if isinstance(column, tuple)
        else str(column)
        for column in summary.columns
    ]
    return summary


def _numeric_result_columns(data: pd.DataFrame) -> list[str]:
    return [
        column for column in data.columns
        if (
            column.startswith("result_") and
            pd.api.types.is_numeric_dtype(data[column])
        )
    ]
