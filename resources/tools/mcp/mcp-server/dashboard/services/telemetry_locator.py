"""Lightweight source-row index for targeted telemetry queries."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from .memory import compact_semantic_frame

from .result_series import (
    LOGICAL_TEST_TYPES,
    hosts_value,
    is_passed,
    natural_key,
    parse_result_dimensions,
    series_id_for_dimensions,
    text_value,
)


LOCATOR_COLUMNS = (
    "_source_row",
    "series_id",
    "name",
    "test_type",
    "testbed",
    "start_time",
)
SERIES_COLUMNS = (
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
)
ALL_LOCATOR_COLUMNS = tuple(dict.fromkeys((*LOCATOR_COLUMNS, *SERIES_COLUMNS)))
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
DEFAULT_CATALOG_LIMIT = 1000
MAX_CATALOG_LIMIT = 10_000


def build_telemetry_locator(
        data: pd.DataFrame,
        telemetry_source: pd.DataFrame,
    ) -> pd.DataFrame:
    """Return compact passed-series rows which have raw telemetry available."""

    if data.empty or telemetry_source.empty:
        return pd.DataFrame(columns=ALL_LOCATOR_COLUMNS)

    available_rows = set(
        pd.to_numeric(
            telemetry_source.get("_source_row", pd.Series(dtype="Int64")),
            errors="coerce",
        ).dropna().astype(int)
    )
    positions = sorted(
        source_row for source_row in available_rows
        if 0 <= source_row < len(data)
    )
    if not positions:
        return pd.DataFrame(columns=ALL_LOCATOR_COLUMNS)
    identity_columns = [
        column for column in (
            "test_id", "dut_type", "job", "hosts", "test_type", "passed",
            "start_time",
        )
        if column in data.columns
    ]
    selected = data.iloc[positions].loc[:, identity_columns].copy(deep=False)
    selected.insert(0, "_source_row", positions)
    records: list[dict[str, Any]] = []
    dimensions_cache: dict[tuple[Any, ...], dict[str, str] | None] = {}
    for row in selected.to_dict(orient="records"):
        if not is_passed(row.get("passed")):
            continue
        hosts = row.get("hosts")
        if not isinstance(hosts, (list, tuple, set)) and hasattr(
                hosts, "tolist"
            ):
            try:
                hosts = hosts.tolist()
            except (TypeError, ValueError):
                pass
        host_key = (
            tuple(str(item) for item in hosts)
            if isinstance(hosts, (list, tuple, set)) else str(hosts)
        )
        cache_key = (
            row.get("test_id"), row.get("dut_type"), row.get("job"), host_key,
        )
        if cache_key not in dimensions_cache:
            dimensions_cache[cache_key] = parse_result_dimensions(row)
        dimensions = dimensions_cache[cache_key]
        if dimensions is None:
            continue
        logical_types = LOGICAL_TEST_TYPES.get(
            text_value(row.get("test_type")) or "",
            (),
        )
        for logical_type in logical_types:
            series_id = series_id_for_dimensions(dimensions, logical_type)
            records.append({
                "_source_row": row["_source_row"],
                "series_id": series_id,
                "name": "-".join((
                    dimensions["dut"],
                    dimensions["infra"],
                    dimensions["area"],
                    dimensions["framesize"],
                    dimensions["cores"],
                    dimensions["test"],
                )),
                **{
                    key: dimensions[key]
                    for key in SERIES_COLUMNS
                    if key in dimensions
                },
                "test_type": logical_type,
                "testbed": dimensions["testbed"],
                "start_time": text_value(row.get("start_time")),
            })
    locator = pd.DataFrame.from_records(
        records,
        columns=ALL_LOCATOR_COLUMNS,
    ).drop_duplicates(keep="first")
    return compact_semantic_frame(
        locator,
        categorical_columns=(
            "series_id", "name", "dut", "area", "area_label", "test",
            "infra", "testbed", "framesize", "cores", "test_type",
        ),
    )


def resolve_telemetry_rows(
        locator: pd.DataFrame,
        *,
        series: list[str],
        testbed: str | None,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
    ) -> dict[str, Any]:
    """Resolve selected series to source rows without building trend analysis."""

    requested = list(dict.fromkeys(str(value) for value in series))
    if locator.empty:
        return {
            "matches": pd.DataFrame(columns=LOCATOR_COLUMNS[:4]),
            "series": [],
            "unknown_series": requested,
            "available_start_time": None,
            "available_end_time": None,
        }

    known = set(locator["series_id"].astype(str))
    selected = [value for value in requested if value in known]
    unknown = [value for value in requested if value not in known]
    matches = locator.loc[locator["series_id"].isin(selected)].copy()
    if testbed is not None:
        matches = matches.loc[
            matches["testbed"].astype("string") == str(testbed)
        ]
    available_times = pd.to_datetime(
        matches["start_time"], errors="coerce", utc=True,
    )
    valid_times = available_times.dropna()
    available_start = valid_times.min().isoformat() if not valid_times.empty else None
    available_end = valid_times.max().isoformat() if not valid_times.empty else None
    matches = matches.loc[
        available_times.between(start_time, end_time, inclusive="both")
    ]
    series_frame = (
        locator.loc[locator["series_id"].isin(selected), list(SERIES_COLUMNS)]
        .drop_duplicates(subset="series_id", keep="first")
        .sort_values(["name", "series_id"], kind="stable")
    )
    return {
        "matches": matches.loc[:, list(LOCATOR_COLUMNS[:4])].drop_duplicates(),
        "series": series_frame.to_dict(orient="records"),
        "unknown_series": unknown,
        "available_start_time": available_start,
        "available_end_time": available_end,
    }


def telemetry_catalog_payload(
        locator: pd.DataFrame,
        status: Mapping[str, Any],
        *,
        filters: Mapping[str, Any],
        offset: Any = 0,
        limit: Any = DEFAULT_CATALOG_LIMIT,
    ) -> dict[str, Any]:
    """Return telemetry-capable logical series without building result trends."""

    parsed_offset, offset_error = _bounded_integer(
        "offset", offset, minimum=0, maximum=None, default=0,
    )
    parsed_limit, limit_error = _bounded_integer(
        "limit", limit, minimum=1, maximum=MAX_CATALOG_LIMIT,
        default=DEFAULT_CATALOG_LIMIT,
    )
    errors = [
        error for error in (offset_error, limit_error) if error is not None
    ]
    filtered = locator
    normalized_filters: dict[str, str | None] = {}
    options: dict[str, list[str]] = {}
    for dimension in CATALOG_DIMENSIONS:
        available = (
            sorted(
                {
                    str(value) for value in filtered[dimension].dropna()
                    if str(value)
                },
                key=natural_key,
            )
            if not filtered.empty and dimension in filtered.columns else []
        )
        options[dimension] = available
        raw_value = filters.get(dimension)
        value = str(raw_value).strip().lower() if raw_value is not None else None
        if (
            dimension == "framesize" and value and
            value.endswith("b") and value[:-1].isdigit()
        ):
            value = f"{value[:-1]}B"
        if value in (None, "", "all"):
            normalized_filters[dimension] = None
            continue
        if value not in available:
            errors.append({
                "field": dimension,
                "message": (
                    f"{dimension} must be one of the values available after "
                    "the preceding telemetry filters."
                ),
                "value": raw_value,
                "available": available,
            })
            normalized_filters[dimension] = None
            continue
        normalized_filters[dimension] = value
        filtered = filtered.loc[
            filtered[dimension].astype("string") == value
        ]

    response_filters = {
        **normalized_filters,
        "offset": parsed_offset,
        "limit": parsed_limit,
    }
    if errors:
        return {
            "error": "validation_error",
            "message": "Invalid MCP tool arguments.",
            "details": {"errors": errors},
            "filters": response_filters,
            "filter_options": options,
        }

    series = (
        filtered.loc[:, list(SERIES_COLUMNS)]
        .drop_duplicates(subset="series_id", keep="first")
        .sort_values(["name", "series_id"], kind="stable")
    )
    page = series.iloc[parsed_offset:parsed_offset + parsed_limit]
    returned_count = len(page)
    has_more = parsed_offset + returned_count < len(series)
    return {
        "schema_version": 1,
        "dataset": "telemetry_catalog",
        "source_dataset": "trending",
        "total_row_count": len(locator),
        "row_count": len(series),
        "returned_count": returned_count,
        "limit": parsed_limit,
        "offset": parsed_offset,
        "has_more": has_more,
        "next_offset": parsed_offset + returned_count if has_more else None,
        "freshness": status.get("last_success_at"),
        "data_status": status.get("status"),
        "filters": response_filters,
        "filter_options": options,
        "columns": list(page.columns),
        "records": page.to_dict(orient="records"),
    }


def raw_telemetry_frame(data: pd.DataFrame) -> pd.DataFrame:
    """Detach raw telemetry blobs from an owned dataframe without deep copying."""

    if data.empty or "telemetry" not in data.columns:
        return pd.DataFrame(columns=["_source_row", "telemetry"])
    values = data.pop("telemetry").reset_index(drop=True)
    detached = pd.DataFrame({
        "_source_row": pd.Series(range(len(values)), dtype="Int64"),
        "telemetry": values,
    })
    return index_raw_telemetry_frame(detached.loc[
        detached["telemetry"].map(_has_raw_telemetry)
    ].reset_index(drop=True))


def index_raw_telemetry_frame(data: pd.DataFrame) -> pd.DataFrame:
    """Index a telemetry sidecar once for constant-time selected-row access."""

    if data.empty or "_source_row" not in data.columns:
        return data
    data["_source_row"] = pd.to_numeric(
        data["_source_row"], errors="coerce"
    ).astype("Int64")
    return data.set_index("_source_row", drop=False, verify_integrity=True)


def attach_raw_telemetry(
        data: pd.DataFrame,
        telemetry_source: pd.DataFrame,
    ) -> pd.DataFrame:
    """Return a shallow result frame with its raw telemetry column restored."""

    if data.empty or telemetry_source.empty:
        return data
    raw = telemetry_source.set_index("_source_row")["telemetry"]
    attached = data.copy(deep=False)
    attached["telemetry"] = pd.Series(
        [raw.get(position) for position in range(len(data))],
        index=data.index,
        dtype=object,
    )
    return attached


def telemetry_blob(
        telemetry_source: pd.DataFrame,
        source_row: int,
    ) -> Any:
    """Return one raw telemetry cell from a detached source frame."""

    if telemetry_source.empty:
        return None
    matches = telemetry_source.loc[
        telemetry_source["_source_row"] == source_row,
        "telemetry",
    ]
    return matches.iloc[0] if not matches.empty else None


def _has_raw_telemetry(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if not isinstance(value, (list, tuple, set)) and hasattr(value, "tolist"):
        try:
            value = value.tolist()
        except (TypeError, ValueError):
            return False
    if isinstance(value, (list, tuple, set)):
        return any(str(item).strip() for item in value if item is not None)
    try:
        return not pd.isna(value)
    except (TypeError, ValueError):
        return bool(value)


def _bounded_integer(
        field: str,
        value: Any,
        *,
        minimum: int,
        maximum: int | None,
        default: int,
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
        expected = f">= {minimum}"
        if maximum is not None:
            expected = f"between {minimum} and {maximum}"
        return default, {
            "field": field,
            "message": f"{field} must be {expected}.",
            "value": value,
        }
    return parsed, None
