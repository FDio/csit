"""Internal compact analysis payload builders for CSIT dataframes."""

from typing import Any, Mapping

import pandas as pd

from .analysis_statistics import (
    AnalysisInputError,
    anomaly_records,
    compare_groups,
    normalized_group_key,
    top_failures,
    trend_window_summary,
)
from .result_metadata import ResultMetadataService
from .serialization import json_safe_value, validation_error_payload


ANALYSIS_DATASETS = ("trending", "iterative", "coverage")
TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}


def validate_analysis_dataset(dataset: str) -> dict[str, Any] | None:
    """Return a validation payload when a dataset cannot be analyzed."""

    if dataset in ANALYSIS_DATASETS:
        return None
    return validation_error_payload(
        [{
            "field": "dataset",
            "message": (
                "dataset must be one of: " +
                ", ".join(ANALYSIS_DATASETS)
            ),
            "value": dataset,
        }],
        {"dataset": dataset},
    )


def compare_hosts_analysis_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        result_column: str,
        result_metadata: ResultMetadataService,
        status: Mapping[str, Any] | None = None,
        test_id: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        build: int | None = None,
        passed: bool | None = None,
        preferred_direction: str | None = None
    ) -> dict[str, Any]:
    """Build a compact host-comparison analysis payload."""

    filtered_data, filters, error = _filtered_analysis_data(
        data,
        text_filters=[
            ("test_id", test_id),
            ("test_type", test_type),
            ("dut_type", dut_type),
            ("job", job),
            ("release", release),
        ],
        int_filters=[("build", build)],
        passed=passed,
    )
    if error is not None:
        return error

    direction, direction_error = _resolve_preferred_direction(
        result_metadata,
        result_column,
        preferred_direction,
    )
    filters["preferred_direction"] = (
        preferred_direction
        if direction_error is not None
        else direction
    )
    if direction_error is not None:
        return validation_error_payload([direction_error], filters)

    try:
        summary, records = compare_groups(
            filtered_data,
            group_by="hosts",
            result_column=result_column,
            preferred_direction=direction,
        )
    except AnalysisInputError as err:
        return validation_error_payload([err.to_detail()], filters)

    return _analysis_payload(
        analysis="compare_hosts",
        dataset=dataset,
        data=filtered_data,
        filters=filters,
        status=status,
        result_column=result_column,
        group_by="hosts",
        summary=summary,
        records=records,
        explanation=(
            f"Compared {result_column} by hosts; "
            f"{direction} values are treated as better."
        ),
    )


def compare_groups_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        group_by: str,
        result_column: str,
        filters: Mapping[str, Any] | None = None,
        status: Mapping[str, Any] | None = None,
        preferred_direction: str = "higher"
    ) -> dict[str, Any]:
    """Build a compact internal group-comparison analysis payload."""

    normalized_filters = _filters(filters)
    try:
        summary, records = compare_groups(
            data,
            group_by=group_by,
            result_column=result_column,
            preferred_direction=preferred_direction,
        )
    except AnalysisInputError as err:
        return validation_error_payload([err.to_detail()], normalized_filters)

    return _analysis_payload(
        analysis="compare_groups",
        dataset=dataset,
        data=data,
        filters=normalized_filters,
        status=status,
        result_column=result_column,
        group_by=group_by,
        summary=summary,
        records=records,
        explanation=(
            f"Compared {result_column} by {group_by}; "
            f"{preferred_direction} values are treated as better."
        ),
    )


def trend_summary_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        result_column: str,
        filters: Mapping[str, Any] | None = None,
        status: Mapping[str, Any] | None = None,
        order_by: str = "build",
        recent_count: int = 3,
        baseline_count: int = 3
    ) -> dict[str, Any]:
    """Build a compact internal recent-vs-baseline trend payload."""

    normalized_filters = _filters(filters)
    try:
        summary = trend_window_summary(
            data,
            result_column=result_column,
            order_by=order_by,
            recent_count=recent_count,
            baseline_count=baseline_count,
        )
    except AnalysisInputError as err:
        return validation_error_payload([err.to_detail()], normalized_filters)

    return _analysis_payload(
        analysis="trend_summary",
        dataset=dataset,
        data=data,
        filters={
            **normalized_filters,
            "order_by": order_by,
            "recent_count": recent_count,
            "baseline_count": baseline_count,
        },
        status=status,
        result_column=result_column,
        group_by=None,
        summary=summary,
        records=[],
        explanation=(
            f"Compared the latest {recent_count} ordered samples against the "
            f"previous {baseline_count} samples."
        ),
    )


def find_anomalies_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        result_column: str,
        filters: Mapping[str, Any] | None = None,
        status: Mapping[str, Any] | None = None,
        group_by: str | None = None,
        threshold: float = 2.0,
        limit: int = 20
    ) -> dict[str, Any]:
    """Build a compact internal deterministic anomaly payload."""

    normalized_filters = _filters(filters)
    try:
        threshold = _validate_positive_float("threshold", threshold)
        _validate_limit(limit)
        all_records = anomaly_records(
            data,
            result_column=result_column,
            group_by=group_by,
            threshold=threshold,
        )
        records = all_records[:limit]
    except AnalysisInputError as err:
        return validation_error_payload([err.to_detail()], normalized_filters)

    return _analysis_payload(
        analysis="find_anomalies",
        dataset=dataset,
        data=data,
        filters={
            **normalized_filters,
            "threshold": threshold,
            "limit": limit,
        },
        status=status,
        result_column=result_column,
        group_by=group_by,
        summary={
            "anomaly_count": len(all_records),
            "returned_count": len(records),
            "threshold": threshold,
            "method": "z_score",
        },
        records=records,
        explanation=(
            "Flags values whose absolute z-score is greater than or equal to "
            "the configured threshold."
        ),
    )


def find_regressions_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        result_column: str,
        group_by: str = "test_id",
        filters: Mapping[str, Any] | None = None,
        status: Mapping[str, Any] | None = None,
        order_by: str = "build",
        recent_count: int = 3,
        baseline_count: int = 3,
        threshold_percent: float = 10.0,
        preferred_direction: str = "higher",
        limit: int = 20
    ) -> dict[str, Any]:
    """Build a deterministic recent-vs-baseline regression payload."""

    normalized_filters = _filters(filters)
    try:
        _validate_group_by(data, group_by)
        _validate_limit(limit)
        recent_count = _validate_positive_int("recent_count", recent_count)
        baseline_count = _validate_positive_int("baseline_count", baseline_count)
        threshold_percent = _validate_positive_float(
            "threshold_percent",
            threshold_percent,
        )
        _validate_resolved_preferred_direction(preferred_direction)
        all_records, skipped_count = _regression_records(
            data,
            result_column=result_column,
            group_by=group_by,
            order_by=order_by,
            recent_count=recent_count,
            baseline_count=baseline_count,
            threshold_percent=threshold_percent,
            preferred_direction=preferred_direction,
        )
        records = all_records[:limit]
    except AnalysisInputError as err:
        return validation_error_payload([err.to_detail()], normalized_filters)

    return _analysis_payload(
        analysis="find_regressions",
        dataset=dataset,
        data=data,
        filters={
            **normalized_filters,
            "order_by": order_by,
            "recent_count": recent_count,
            "baseline_count": baseline_count,
            "threshold_percent": threshold_percent,
            "preferred_direction": preferred_direction,
            "limit": limit,
        },
        status=status,
        result_column=result_column,
        group_by=group_by,
        summary={
            "regression_count": len(all_records),
            "returned_count": len(records),
            "skipped_group_count": skipped_count,
            "threshold_percent": threshold_percent,
            "preferred_direction": preferred_direction,
            "method": "recent_vs_baseline",
        },
        records=records,
        explanation=(
            f"Reports {group_by} groups where recent {result_column} values "
            f"worsened by at least {threshold_percent}% against baseline."
        ),
    )


def top_failures_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        group_by: str,
        filters: Mapping[str, Any] | None = None,
        status: Mapping[str, Any] | None = None,
        limit: int = 10
    ) -> dict[str, Any]:
    """Build a compact internal failure-ranking payload."""

    normalized_filters = _filters(filters)
    try:
        records = top_failures(data, group_by=group_by, limit=limit)
    except AnalysisInputError as err:
        return validation_error_payload([err.to_detail()], normalized_filters)

    return _analysis_payload(
        analysis="top_failures",
        dataset=dataset,
        data=data,
        filters={
            **normalized_filters,
            "limit": limit,
        },
        status=status,
        result_column=None,
        group_by=group_by,
        summary={
            "group_count": len(records),
            "failed_count": sum(record["failed_count"] for record in records),
        },
        records=records,
        explanation=f"Ranks {group_by} groups by failed count and failure rate.",
    )


def filtered_trend_summary_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        result_column: str,
        status: Mapping[str, Any] | None = None,
        test_id: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        passed: bool | None = None,
        order_by: str = "build",
        recent_count: int = 3,
        baseline_count: int = 3
    ) -> dict[str, Any]:
    """Filter data and build a trend summary payload."""

    filtered_data, filters, error = _filtered_analysis_data(
        data,
        text_filters=[
            ("test_id", test_id),
            ("test_type", test_type),
            ("dut_type", dut_type),
            ("job", job),
            ("release", release),
            ("hosts", hosts),
        ],
        passed=passed,
    )
    if error is not None:
        return error

    return trend_summary_payload(
        dataset=dataset,
        data=filtered_data,
        result_column=result_column,
        filters=filters,
        status=status,
        order_by=order_by,
        recent_count=recent_count,
        baseline_count=baseline_count,
    )


def filtered_find_regressions_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        result_column: str,
        result_metadata: ResultMetadataService,
        status: Mapping[str, Any] | None = None,
        group_by: str = "test_id",
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        passed: bool | None = None,
        order_by: str = "build",
        recent_count: int = 3,
        baseline_count: int = 3,
        threshold_percent: float = 10.0,
        preferred_direction: str | None = None,
        limit: int = 20
    ) -> dict[str, Any]:
    """Filter data and build a regression payload."""

    filtered_data, filters, error = _filtered_analysis_data(
        data,
        text_filters=[
            ("test_type", test_type),
            ("dut_type", dut_type),
            ("job", job),
            ("release", release),
            ("hosts", hosts),
        ],
        passed=passed,
    )
    if error is not None:
        return error

    direction, direction_error = _resolve_preferred_direction(
        result_metadata,
        result_column,
        preferred_direction,
    )
    filters["preferred_direction"] = (
        preferred_direction
        if direction_error is not None
        else direction
    )
    if direction_error is not None:
        return validation_error_payload([direction_error], filters)

    return find_regressions_payload(
        dataset=dataset,
        data=filtered_data,
        result_column=result_column,
        group_by=group_by,
        filters=filters,
        status=status,
        order_by=order_by,
        recent_count=recent_count,
        baseline_count=baseline_count,
        threshold_percent=threshold_percent,
        preferred_direction=direction,
        limit=limit,
    )


def filtered_find_anomalies_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        result_column: str,
        status: Mapping[str, Any] | None = None,
        group_by: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        passed: bool | None = None,
        threshold: float = 2.0,
        limit: int = 20
    ) -> dict[str, Any]:
    """Filter data and build an anomaly payload."""

    filtered_data, filters, error = _filtered_analysis_data(
        data,
        text_filters=[
            ("test_type", test_type),
            ("dut_type", dut_type),
            ("job", job),
            ("release", release),
            ("hosts", hosts),
        ],
        passed=passed,
    )
    if error is not None:
        return error

    return find_anomalies_payload(
        dataset=dataset,
        data=filtered_data,
        result_column=result_column,
        filters=filters,
        status=status,
        group_by=group_by,
        threshold=threshold,
        limit=limit,
    )


def filtered_top_failures_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        status: Mapping[str, Any] | None = None,
        group_by: str = "test_id",
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        build: int | None = None,
        limit: int = 20
    ) -> dict[str, Any]:
    """Filter data and build a failure-ranking payload."""

    filtered_data, filters, error = _filtered_analysis_data(
        data,
        text_filters=[
            ("test_type", test_type),
            ("dut_type", dut_type),
            ("job", job),
            ("release", release),
            ("hosts", hosts),
        ],
        int_filters=[("build", build)],
    )
    if error is not None:
        return error

    return top_failures_payload(
        dataset=dataset,
        data=filtered_data,
        group_by=group_by,
        filters=filters,
        status=status,
        limit=limit,
    )


def _analysis_payload(
        *,
        analysis: str,
        dataset: str,
        data: pd.DataFrame,
        filters: Mapping[str, Any],
        status: Mapping[str, Any] | None,
        result_column: str | None,
        group_by: str | None,
        summary: Mapping[str, Any],
        records: list[dict[str, Any]],
        explanation: str
    ) -> dict[str, Any]:
    status = status or {}
    payload = {
        "schema_version": 1,
        "analysis": analysis,
        "dataset": dataset,
        "filters": json_safe_value(dict(filters)),
        "result_column": result_column,
        "group_by": group_by,
        "row_count": len(data),
        "freshness": status.get("last_success_at"),
        "data_status": status.get("status"),
        "summary": json_safe_value(dict(summary)),
        "records": json_safe_value(records),
        "explanation": explanation,
    }
    return payload


def _filters(filters: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(filters or {})


def _filtered_analysis_data(
        data: pd.DataFrame,
        *,
        text_filters: list[tuple[str, Any]],
        int_filters: list[tuple[str, Any]] | None = None,
        passed: bool | None = None
    ) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any] | None]:
    errors: list[dict[str, Any]] = []
    int_filters = int_filters or []
    parsed_int_filters = {
        column: _parse_optional_int(column, value)
        for column, value in int_filters
    }
    parsed_passed, passed_error = _parse_optional_bool(passed)
    if passed_error is not None:
        errors.append(passed_error)

    filters = {
        column: value
        for column, value in text_filters
    }
    filters.update({
        column: parsed_value
        for column, (parsed_value, _err) in parsed_int_filters.items()
    })
    filters["passed"] = parsed_passed
    errors.extend(
        err for _parsed, err in parsed_int_filters.values()
        if err is not None
    )

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

    if errors:
        return filtered_data, filters, validation_error_payload(errors, filters)
    return filtered_data, filters, None


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
        errors.append(_missing_column_error(column))
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
        errors.append(_missing_column_error(column))
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
        errors.append(_missing_column_error(column))
        return data
    normalized = data[column].astype(str).str.strip().str.lower()
    expected_values = TRUE_VALUES if value else FALSE_VALUES
    return data.loc[normalized.isin(expected_values)]


def _parse_optional_int(
        field: str,
        value: Any,
        *,
        minimum: int = 0
    ) -> tuple[int | None, dict[str, Any] | None]:
    if value is None:
        return None, None
    if isinstance(value, bool):
        return None, _int_error(field, value, minimum)
    if isinstance(value, float) and not value.is_integer():
        return None, _int_error(field, value, minimum)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None, _int_error(field, value, minimum)
    if parsed < minimum:
        return None, _int_error(field, value, minimum)
    return parsed, None


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


def _int_error(field: str, value: Any, minimum: int) -> dict[str, Any]:
    return {
        "field": field,
        "message": f"{field} must be an integer >= {minimum}.",
        "value": value,
    }


def _missing_column_error(column: str, field: str | None = None) -> dict[str, Any]:
    field = field or column
    return {
        "field": field,
        "message": (
            f"{field} filter is unsupported because column '{column}' "
            "is not available in the cached dataset."
        ),
    }


def _resolve_preferred_direction(
        result_metadata: ResultMetadataService,
        result_column: str,
        preferred_direction: str | None
    ) -> tuple[str, dict[str, Any] | None]:
    if preferred_direction is not None:
        normalized = str(preferred_direction).strip().lower()
        if normalized in {"higher", "lower"}:
            return normalized, None
        return "higher", {
            "field": "preferred_direction",
            "message": "preferred_direction must be 'higher' or 'lower'.",
            "value": preferred_direction,
        }

    metadata = result_metadata.metadata_for_column(result_column) or {}
    direction = metadata.get("preferred_direction")
    if direction in {"higher", "lower"}:
        return direction, None
    return "higher", None


def _validate_resolved_preferred_direction(preferred_direction: str) -> None:
    if preferred_direction not in {"higher", "lower"}:
        raise AnalysisInputError(
            "preferred_direction",
            "preferred_direction must be 'higher' or 'lower'.",
            preferred_direction,
        )


def _validate_group_by(data: pd.DataFrame, group_by: str) -> None:
    if not isinstance(group_by, str) or not group_by:
        raise AnalysisInputError(
            "group_by",
            "group_by must be a non-empty column name.",
            group_by,
        )
    if group_by not in data.columns:
        raise AnalysisInputError(
            "group_by",
            (
                f"group_by is unsupported because column '{group_by}' is not "
                "available in the dataframe."
            ),
            group_by,
        )


def _validate_limit(limit: int) -> None:
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise AnalysisInputError(
            "limit",
            "limit must be a positive integer.",
            limit,
        )


def _validate_positive_int(field: str, value: Any) -> int:
    if isinstance(value, bool):
        raise AnalysisInputError(field, f"{field} must be a positive integer.", value)
    if isinstance(value, float) and not value.is_integer():
        raise AnalysisInputError(field, f"{field} must be a positive integer.", value)
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AnalysisInputError(
            field,
            f"{field} must be a positive integer.",
            value,
        ) from exc
    if parsed < 1:
        raise AnalysisInputError(field, f"{field} must be a positive integer.", value)
    return parsed


def _validate_positive_float(field: str, value: Any) -> float:
    if isinstance(value, bool):
        raise AnalysisInputError(field, f"{field} must be greater than 0.", value)
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise AnalysisInputError(
            field,
            f"{field} must be greater than 0.",
            value,
        ) from exc
    if parsed <= 0:
        raise AnalysisInputError(field, f"{field} must be greater than 0.", value)
    return parsed


def _regression_records(
        data: pd.DataFrame,
        *,
        result_column: str,
        group_by: str,
        order_by: str,
        recent_count: int,
        baseline_count: int,
        threshold_percent: float,
        preferred_direction: str
    ) -> tuple[list[dict[str, Any]], int]:
    if data.empty:
        return [], 0

    working_data = data.copy()
    working_data["_analysis_group_key"] = working_data[group_by].map(
        normalized_group_key
    )
    records: list[dict[str, Any]] = []
    skipped_count = 0
    for group_key, group in working_data.groupby("_analysis_group_key", dropna=False):
        try:
            summary = trend_window_summary(
                group,
                result_column=result_column,
                order_by=order_by,
                recent_count=recent_count,
                baseline_count=baseline_count,
            )
        except AnalysisInputError as err:
            if err.field == "recent_count":
                skipped_count += 1
                continue
            raise

        regression_percent = _regression_percent(
            summary.get("relative_delta_percent"),
            preferred_direction,
        )
        if regression_percent is None or regression_percent < threshold_percent:
            continue
        records.append({
            group_by: json_safe_value(group_key),
            "group_key": json_safe_value(group_key),
            "baseline": summary["baseline"],
            "recent": summary["recent"],
            "mean_delta": summary["mean_delta"],
            "relative_delta_percent": summary["relative_delta_percent"],
            "regression_percent": regression_percent,
            "latest": summary["latest"],
            "earliest": summary["earliest"],
            "preferred_direction": preferred_direction,
            "explanation": _regression_explanation(
                result_column,
                group_by,
                group_key,
                regression_percent,
                preferred_direction,
            ),
        })

    return sorted(
        records,
        key=lambda item: (
            item["regression_percent"],
            str(item["group_key"]),
        ),
        reverse=True,
    ), skipped_count


def _regression_percent(
        relative_delta_percent: Any,
        preferred_direction: str
    ) -> float | None:
    if relative_delta_percent is None:
        return None
    if preferred_direction == "higher" and relative_delta_percent < 0:
        return abs(relative_delta_percent)
    if preferred_direction == "lower" and relative_delta_percent > 0:
        return relative_delta_percent
    return None


def _regression_explanation(
        result_column: str,
        group_by: str,
        group_key: Any,
        regression_percent: float,
        preferred_direction: str
    ) -> str:
    direction_text = (
        "decreased"
        if preferred_direction == "higher"
        else "increased"
    )
    return (
        f"{result_column} for {group_by}={group_key} {direction_text} by "
        f"{regression_percent:.2f}% against the baseline window."
    )
