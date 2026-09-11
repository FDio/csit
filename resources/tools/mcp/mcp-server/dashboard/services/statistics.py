"""Job statistics enrichment and cascading filter helpers."""

import re
from typing import Any

import pandas as pd


DUT_VALUES = ("dpdk", "trex", "vpp")
TEST_TYPE_VALUES = ("hoststack", "mrr", "ndrpdr", "soak")
CADENCE_VALUES = ("daily", "weekly")
DIMENSION_FIELDS = ("dut", "test_type", "cadence", "testbed")
PREFERRED_DEFAULTS = {
    "dut": "vpp",
    "test_type": "mrr",
    "cadence": "daily",
}
_TOPOLOGY_TOKEN = re.compile(r"^\d+n(?:\d+l)?[a-z]*$")
_NATURAL_PART = re.compile(r"(\d+)")


def parse_job_dimensions(job: Any) -> dict[str, str | None]:
    """Extract dashboard dimensions from a CSIT job name."""

    if job is None:
        return _empty_dimensions()
    try:
        if pd.isna(job):
            return _empty_dimensions()
    except (TypeError, ValueError):
        pass

    tokens = [token for token in str(job).strip().lower().split("-") if token]
    if not tokens:
        return _empty_dimensions()

    topology_index = next(
        (
            index for index in range(len(tokens) - 1, -1, -1)
            if _TOPOLOGY_TOKEN.fullmatch(tokens[index])
        ),
        None,
    )
    testbed = (
        "-".join(tokens[topology_index:])
        if topology_index is not None
        else None
    )
    return {
        "dut": _first_supported(tokens, DUT_VALUES),
        "test_type": _first_supported(tokens, TEST_TYPE_VALUES),
        "cadence": _first_supported(tokens, CADENCE_VALUES),
        "testbed": testbed,
    }


def enrich_job_statistics(
        statistics: pd.DataFrame,
        trending: pd.DataFrame,
    ) -> pd.DataFrame:
    """Return statistics rows with dimensions and joined pass/fail counts."""

    enriched = statistics.copy(deep=True)
    jobs = (
        enriched["job"]
        if "job" in enriched.columns
        else pd.Series([None] * len(enriched), index=enriched.index)
    )
    dimensions = pd.DataFrame(
        [parse_job_dimensions(job) for job in jobs],
        index=enriched.index,
    )
    for field in DIMENSION_FIELDS:
        enriched[field] = dimensions[field]

    enriched["passed_count"] = pd.Series(0, index=enriched.index, dtype="Int64")
    enriched["failed_count"] = pd.Series(0, index=enriched.index, dtype="Int64")
    enriched["total_test_count"] = pd.Series(
        0,
        index=enriched.index,
        dtype="Int64",
    )
    enriched["counts_available"] = False
    enriched["dut_version"] = None
    enriched["hosts"] = None

    required_statistics = {"job", "build"}
    required_trending = {"job", "build", "passed"}
    if (
            enriched.empty or
            trending.empty or
            not required_statistics.issubset(enriched.columns) or
            not required_trending.issubset(trending.columns)
        ):
        return enriched

    result_columns = ["job", "build", "passed"]
    result_columns.extend(
        column for column in ("dut_version", "hosts")
        if column in trending.columns
    )
    result_rows = trending.loc[:, result_columns].copy()
    result_rows["_job_key"] = result_rows["job"].astype("string")
    result_rows["_build_key"] = _build_keys(result_rows["build"])
    result_rows["_passed"] = result_rows["passed"].map(_normalized_passed)
    result_rows["_dut_version"] = (
        result_rows["dut_version"].map(_normalized_text)
        if "dut_version" in result_rows.columns
        else None
    )
    result_rows["_hosts"] = (
        result_rows["hosts"].map(_normalized_hosts)
        if "hosts" in result_rows.columns
        else None
    )
    result_rows = result_rows.dropna(subset=["_job_key", "_build_key"])
    if result_rows.empty:
        return enriched

    summaries = []
    for (job_key, build_key), group in result_rows.groupby(
            ["_job_key", "_build_key"],
            dropna=False,
            sort=False,
        ):
        versions = _distinct_text(group["_dut_version"])
        hosts = _distinct_hosts(group["_hosts"])
        summaries.append({
            "_job_key": job_key,
            "_build_key": build_key,
            "passed_count": sum(
                value is True for value in group["_passed"]
            ),
            "failed_count": sum(
                value is False for value in group["_passed"]
            ),
            "dut_version": ", ".join(versions) if versions else None,
            "hosts": hosts or None,
        })
    counts = pd.DataFrame(summaries)
    counts["total_test_count"] = counts["passed_count"] + counts["failed_count"]
    counts["counts_available"] = True

    enriched["_job_key"] = enriched["job"].astype("string")
    enriched["_build_key"] = _build_keys(enriched["build"])
    enriched = enriched.drop(
        columns=[
            "passed_count",
            "failed_count",
            "total_test_count",
            "counts_available",
            "dut_version",
            "hosts",
        ]
    ).merge(
        counts,
        how="left",
        on=["_job_key", "_build_key"],
        sort=False,
    )
    for field in ("passed_count", "failed_count", "total_test_count"):
        enriched[field] = pd.to_numeric(
            enriched[field],
            errors="coerce",
        ).fillna(0).astype("Int64")
    enriched["counts_available"] = (
        enriched["counts_available"].astype("boolean").fillna(False).astype(bool)
    )
    for field in ("dut_version", "hosts"):
        enriched[field] = (
            enriched[field].astype("object").where(enriched[field].notna(), None)
        )
    return enriched.drop(columns=["_job_key", "_build_key"])


def filter_job_statistics(
        data: pd.DataFrame,
        *,
        dut: Any,
        test_type: Any,
        cadence: Any,
        testbed: Any,
        select_defaults: bool,
    ) -> tuple[
        pd.DataFrame,
        dict[str, list[str]],
        dict[str, str | None],
        list[dict[str, Any]],
    ]:
    """Apply cascading dimensions and return options and normalized values."""

    requested = {
        "dut": _normalized_selection(dut),
        "test_type": _normalized_selection(test_type),
        "cadence": _normalized_selection(cadence),
        "testbed": _normalized_selection(testbed),
    }
    filtered = data
    options: dict[str, list[str]] = {}
    selected: dict[str, str | None] = {}
    errors: list[dict[str, Any]] = []

    for field in DIMENSION_FIELDS:
        available = _available_values(filtered, field)
        options[field] = available
        value = requested[field]
        if value is None and select_defaults:
            value = _default_value(field, available)
        elif value is not None and value not in available:
            if select_defaults:
                value = _default_value(field, available)
            else:
                errors.append({
                    "field": field,
                    "message": (
                        f"{field} must be one of the values available after "
                        "the preceding statistics filters."
                    ),
                    "value": requested[field],
                    "available": available,
                })
                value = None
        selected[field] = value
        if value is not None:
            filtered = filtered.loc[filtered[field].astype("string") == value]

    return filtered, options, selected, errors


def statistics_counts(data: pd.DataFrame) -> dict[str, int]:
    """Return classification and result-count availability metadata."""

    if data.empty:
        return {"unclassified_row_count": 0, "unmatched_run_count": 0}
    unclassified = data.loc[:, list(DIMENSION_FIELDS)].isna().any(axis=1)
    unavailable = ~data["counts_available"].fillna(False).astype(bool)
    return {
        "unclassified_row_count": int(unclassified.sum()),
        "unmatched_run_count": int(unavailable.sum()),
    }


def _first_supported(tokens: list[str], supported: tuple[str, ...]) -> str | None:
    return next((value for value in supported if value in tokens), None)


def _empty_dimensions() -> dict[str, None]:
    return {field: None for field in DIMENSION_FIELDS}


def _build_keys(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").astype("Int64")
    return numeric.astype("string")


def _normalized_passed(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    return None


def _normalized_selection(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    return normalized or None


def _default_value(field: str, available: list[str]) -> str | None:
    preferred = PREFERRED_DEFAULTS.get(field)
    if preferred in available:
        return preferred
    return available[0] if available else None


def _normalized_text(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    normalized = str(value).strip()
    return normalized or None


def _normalized_hosts(value: Any) -> list[str]:
    if value is None:
        return []
    if hasattr(value, "as_py"):
        value = value.as_py()
    elif hasattr(value, "to_pylist"):
        value = value.to_pylist()
    elif hasattr(value, "tolist") and not isinstance(value, str):
        value = value.tolist()

    values = value if isinstance(value, (list, tuple, set)) else [value]
    return [
        normalized
        for item in values
        if (normalized := _normalized_text(item)) is not None
    ]


def _distinct_text(values: pd.Series) -> list[str]:
    result = []
    for value in values:
        if value is not None and value not in result:
            result.append(value)
    return result


def _distinct_hosts(values: pd.Series) -> list[str]:
    result = []
    for hosts in values:
        for host in hosts or []:
            if host not in result:
                result.append(host)
    return result


def _available_values(data: pd.DataFrame, field: str) -> list[str]:
    if field not in data.columns or data.empty:
        return []
    values = {
        str(value)
        for value in data[field].dropna().tolist()
        if str(value).strip()
    }
    if field == "dut":
        return [value for value in DUT_VALUES if value in values]
    if field == "test_type":
        return [value for value in TEST_TYPE_VALUES if value in values]
    if field == "cadence":
        return [value for value in CADENCE_VALUES if value in values]
    return sorted(values, key=_natural_key)


def _natural_key(value: str) -> list[tuple[int, Any]]:
    return [
        (0, int(part)) if part.isdigit() else (1, part)
        for part in _NATURAL_PART.split(value)
        if part
    ]
