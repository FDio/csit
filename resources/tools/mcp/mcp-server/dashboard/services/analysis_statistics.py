"""Statistical helpers for internal CSIT analysis services."""

from typing import Any, Iterable

import pandas as pd

from .serialization import json_safe_value


TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}
NUMERIC_SUMMARY_FIELDS = (
    "count",
    "min",
    "mean",
    "max",
    "median",
    "std",
    "p10",
    "p90",
)


class AnalysisInputError(ValueError):
    """Raised when analysis input data or arguments are invalid."""

    def __init__(
            self,
            field: str,
            message: str,
            value: Any = None
        ) -> None:
        super().__init__(message)
        self.field = field
        self.message = message
        self.value = value

    def to_detail(self) -> dict[str, Any]:
        """Return an existing validation-error compatible detail."""

        detail = {
            "field": self.field,
            "message": self.message,
        }
        if self.value is not None:
            detail["value"] = json_safe_value(self.value)
        return detail


def normalized_group_key(value: Any) -> str | None:
    """Return a stable text key for scalar or list-valued dimensions."""

    safe_value = json_safe_value(value)
    if safe_value is None:
        return None
    if isinstance(safe_value, list):
        return ",".join(sorted(str(item) for item in safe_value))
    return str(safe_value)


def numeric_summary(data: pd.DataFrame, result_column: str) -> dict[str, Any]:
    """Return min/mean/max/median/std and percentile summaries."""

    values = _numeric_series(data, result_column).dropna()
    if values.empty:
        return _empty_numeric_summary()

    return {
        "count": int(values.count()),
        "min": _safe_number(values.min()),
        "mean": _safe_number(values.mean()),
        "max": _safe_number(values.max()),
        "median": _safe_number(values.median()),
        "std": _safe_number(values.std()),
        "p10": _safe_number(values.quantile(0.10)),
        "p90": _safe_number(values.quantile(0.90)),
    }


def pass_fail_counts(data: pd.DataFrame) -> dict[str, Any]:
    """Return row, pass, fail, and failure-rate counts."""

    row_count = len(data)
    if "passed" not in data.columns:
        return {
            "row_count": row_count,
            "passed_count": 0,
            "failed_count": 0,
            "failure_rate": None,
        }

    normalized = data["passed"].astype(str).str.strip().str.lower()
    passed_count = int(normalized.isin(TRUE_VALUES).sum())
    failed_count = int(normalized.isin(FALSE_VALUES).sum())
    return {
        "row_count": row_count,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "failure_rate": (
            failed_count / row_count
            if row_count
            else None
        ),
    }


def grouped_summary(
        data: pd.DataFrame,
        *,
        group_by: str,
        result_column: str | None = None
    ) -> list[dict[str, Any]]:
    """Return compact per-group counts and optional numeric summaries."""

    _require_column(data, group_by, field="group_by")
    if result_column is not None:
        _numeric_series(data, result_column)

    if data.empty:
        return []

    working_data = data.copy()
    working_data["_analysis_group_key"] = working_data[group_by].map(
        normalized_group_key
    )
    records: list[dict[str, Any]] = []

    for group_key, group in working_data.groupby("_analysis_group_key", dropna=False):
        record: dict[str, Any] = {
            group_by: json_safe_value(group_key),
            "group_key": json_safe_value(group_key),
            **pass_fail_counts(group),
        }
        if result_column is not None:
            record["result"] = numeric_summary(group, result_column)
        records.append(record)

    return sorted(records, key=lambda item: str(item["group_key"]))


def compare_groups(
        data: pd.DataFrame,
        *,
        group_by: str,
        result_column: str,
        preferred_direction: str = "higher"
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return best/worst group comparison and grouped records."""

    if preferred_direction not in {"higher", "lower"}:
        raise AnalysisInputError(
            "preferred_direction",
            "preferred_direction must be 'higher' or 'lower'.",
            preferred_direction,
        )

    records = [
        record for record in grouped_summary(
            data,
            group_by=group_by,
            result_column=result_column,
        )
        if record["result"]["count"] > 0
    ]
    if not records:
        return {
            "group_count": 0,
            "best_group": None,
            "worst_group": None,
            "absolute_delta": None,
            "relative_delta_percent": None,
            "preferred_direction": preferred_direction,
        }, []

    reverse = preferred_direction == "higher"
    records = sorted(
        records,
        key=lambda item: (
            item["result"]["mean"],
            str(item["group_key"]),
        ),
        reverse=reverse,
    )
    best = records[0]
    worst = records[-1]
    best_mean = best["result"]["mean"]
    worst_mean = worst["result"]["mean"]
    absolute_delta = (
        abs(best_mean - worst_mean)
        if best_mean is not None and worst_mean is not None
        else None
    )
    relative_delta = (
        (absolute_delta / abs(worst_mean)) * 100
        if absolute_delta is not None and worst_mean not in (None, 0)
        else None
    )

    return {
        "group_count": len(records),
        "best_group": best["group_key"],
        "worst_group": worst["group_key"],
        "best_mean": best_mean,
        "worst_mean": worst_mean,
        "absolute_delta": _safe_number(absolute_delta),
        "relative_delta_percent": _safe_number(relative_delta),
        "preferred_direction": preferred_direction,
    }, records


def trend_window_summary(
        data: pd.DataFrame,
        *,
        result_column: str,
        order_by: str = "build",
        recent_count: int = 3,
        baseline_count: int = 3
    ) -> dict[str, Any]:
    """Compare a recent ordered window with the preceding baseline window."""

    _require_positive_count("recent_count", recent_count)
    _require_positive_count("baseline_count", baseline_count)
    values = _ordered_numeric_data(
        data,
        result_column=result_column,
        order_by=order_by,
    )
    required_count = recent_count + baseline_count
    if len(values) < required_count:
        raise AnalysisInputError(
            "recent_count",
            (
                "not enough ordered numeric samples for requested recent and "
                "baseline windows"
            ),
            {
                "available": len(values),
                "required": required_count,
            },
        )

    recent = values.tail(recent_count)
    baseline = values.iloc[-required_count:-recent_count]
    baseline_summary = numeric_summary(baseline, result_column)
    recent_summary = numeric_summary(recent, result_column)
    baseline_mean = baseline_summary["mean"]
    recent_mean = recent_summary["mean"]
    if baseline_mean is None or recent_mean is None:
        raise AnalysisInputError(
            "recent_count",
            (
                "not enough numeric samples in recent and baseline windows "
                f"for result column '{result_column}'"
            ),
            {
                "baseline_count": baseline_summary["count"],
                "recent_count": recent_summary["count"],
            },
        )

    delta = recent_mean - baseline_mean
    relative_delta = (
        (delta / abs(baseline_mean)) * 100
        if baseline_mean not in (None, 0)
        else None
    )

    return {
        "order_by": order_by,
        "recent_count": recent_count,
        "baseline_count": baseline_count,
        "baseline": baseline_summary,
        "recent": recent_summary,
        "mean_delta": _safe_number(delta),
        "relative_delta_percent": _safe_number(relative_delta),
        "direction": _trend_direction(delta),
        "latest": _safe_number(recent[result_column].iloc[-1]),
        "earliest": _safe_number(baseline[result_column].iloc[0]),
    }


def anomaly_records(
        data: pd.DataFrame,
        *,
        result_column: str,
        group_by: str | None = None,
        threshold: float = 2.0
    ) -> list[dict[str, Any]]:
    """Return deterministic z-score anomaly records."""

    if threshold <= 0:
        raise AnalysisInputError(
            "threshold",
            "threshold must be greater than 0.",
            threshold,
        )
    if group_by is not None:
        _require_column(data, group_by, field="group_by")
    values = _numeric_series(data, result_column)
    working_data = data.copy()
    working_data["_analysis_value"] = values
    if group_by is None:
        groups: Iterable[tuple[str | None, pd.DataFrame]] = (
            (None, working_data),
        )
    else:
        working_data["_analysis_group_key"] = working_data[group_by].map(
            normalized_group_key
        )
        groups = working_data.groupby("_analysis_group_key", dropna=False)

    anomalies: list[dict[str, Any]] = []
    for group_key, group in groups:
        numeric_values = group["_analysis_value"].dropna()
        if len(numeric_values) < 3:
            continue
        expected = numeric_values.mean()
        std = numeric_values.std()
        if pd.isna(std) or std == 0:
            continue
        for index, value in numeric_values.items():
            score = abs((value - expected) / std)
            if score < threshold:
                continue
            source_row = data.loc[index]
            anomalies.append(
                {
                    "group_key": json_safe_value(group_key),
                    "actual": _safe_number(value),
                    "expected": _safe_number(expected),
                    "score": _safe_number(score),
                    "threshold": threshold,
                    "direction": "above" if value > expected else "below",
                    "build": json_safe_value(source_row.get("build")),
                    "test_id": json_safe_value(source_row.get("test_id")),
                    "start_time": json_safe_value(source_row.get("start_time")),
                    "explanation": (
                        f"{result_column} is {score:.2f} standard deviations "
                        f"from the group mean."
                    ),
                }
            )

    return sorted(
        anomalies,
        key=lambda item: (
            item["score"],
            str(item.get("group_key")),
        ),
        reverse=True,
    )


def top_failures(
        data: pd.DataFrame,
        *,
        group_by: str,
        limit: int = 10
    ) -> list[dict[str, Any]]:
    """Return groups ordered by failed count and failure rate."""

    _require_column(data, group_by, field="group_by")
    _require_column(data, "passed", field="passed")
    _require_positive_count("limit", limit)
    if data.empty:
        return []

    working_data = data.copy()
    working_data["_analysis_group_key"] = working_data[group_by].map(
        normalized_group_key
    )
    records = []
    for group_key, group in working_data.groupby("_analysis_group_key", dropna=False):
        records.append(
            {
                group_by: json_safe_value(group_key),
                "group_key": json_safe_value(group_key),
                **pass_fail_counts(group),
            }
        )

    return sorted(
        records,
        key=lambda item: (
            item["failed_count"],
            item["failure_rate"] or 0,
            str(item["group_key"]),
        ),
        reverse=True,
    )[:limit]


def _numeric_series(data: pd.DataFrame, result_column: str) -> pd.Series:
    _require_column(data, result_column, field="result_column")
    values = pd.to_numeric(data[result_column], errors="coerce")
    if not data.empty and values.dropna().empty:
        raise AnalysisInputError(
            "result_column",
            f"result_column '{result_column}' must contain numeric values.",
            result_column,
        )
    return values


def _ordered_numeric_data(
        data: pd.DataFrame,
        *,
        result_column: str,
        order_by: str
    ) -> pd.DataFrame:
    _require_column(data, order_by, field="order_by")
    values = _numeric_series(data, result_column)
    ordered = data.copy()
    ordered[result_column] = values
    if order_by == "start_time":
        ordered["_analysis_order"] = pd.to_datetime(
            ordered[order_by],
            errors="coerce",
            utc=True,
        )
    else:
        numeric_order = pd.to_numeric(ordered[order_by], errors="coerce")
        ordered["_analysis_order"] = numeric_order
        if numeric_order.dropna().empty:
            ordered["_analysis_order"] = ordered[order_by].map(
                normalized_group_key
            )

    ordered = ordered.dropna(subset=[result_column, "_analysis_order"])
    return (
        ordered.sort_values(
            by="_analysis_order",
            ascending=True,
            kind="mergesort",
        )
        .drop(columns=["_analysis_order"])
    )


def _require_column(data: pd.DataFrame, column: str, *, field: str) -> None:
    if column not in data.columns:
        raise AnalysisInputError(
            field,
            (
                f"{field} is unsupported because column '{column}' is not "
                "available in the dataframe."
            ),
            column,
        )


def _require_positive_count(field: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise AnalysisInputError(
            field,
            f"{field} must be a positive integer.",
            value,
        )


def _empty_numeric_summary() -> dict[str, Any]:
    return {
        field: 0 if field == "count" else None
        for field in NUMERIC_SUMMARY_FIELDS
    }


def _safe_number(value: Any) -> int | float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    safe_value = json_safe_value(value)
    if isinstance(safe_value, float) and safe_value.is_integer():
        return int(safe_value)
    return safe_value


def _trend_direction(delta: float) -> str:
    if abs(delta) <= 1e-12:
        return "flat"
    return "up" if delta > 0 else "down"
