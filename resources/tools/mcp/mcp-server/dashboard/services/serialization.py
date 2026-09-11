"""Serialization helpers for CSIT MCP data responses."""

import json
from typing import Any, Mapping

import pandas as pd

from .data_cache import (
    DataCacheError,
    DataCacheService,
    DatasetNotFoundError,
)
from .observability import log_event


MAX_SERIALIZED_RESPONSE_BYTES = 1_000_000
RESOURCE_PREVIEW_RECORD_LIMIT = 1000
PRIVATE_PREVIEW_COLUMNS = frozenset({"telemetry"})

DEFAULT_TOO_LARGE_SUGGESTIONS = [
    "Lower limit or request a later page with offset.",
    "Use columns to return only the fields you need.",
    "Filter by dimensions such as test_type, dut_type, job, release, hosts, "
    "test_id, or build.",
    "Use aggregation=hosts, aggregation=test_id, or "
    "aggregation=hosts_by_test_id for summaries.",
]

RESOURCE_TOO_LARGE_SUGGESTIONS = [
    "Use public filtered tools instead of data://parquet for broad inspection.",
    "Call datasets(), columns(dataset), or values(dataset, column) before "
    "requesting records.",
    "Use columns, limit, offset, filters, or aggregation on the public data "
    "tools.",
]


def cache_error_payload(
        err: DataCacheError,
        data_cache: DataCacheService
    ) -> dict[str, Any]:
    error_type = (
        "dataset_not_found"
        if isinstance(err, DatasetNotFoundError)
        else "data_unavailable"
    )
    return {
        "error": error_type,
        "message": str(err),
        "data": data_cache.status_snapshot(),
    }


def validation_error_payload(
        errors: list[dict[str, Any]],
        filters: Mapping[str, Any]
    ) -> dict[str, Any]:
    return {
        "error": "validation_error",
        "message": "Invalid MCP tool arguments.",
        "details": {
            "errors": errors,
        },
        "filters": filters,
    }


def dataframe_payload(data: pd.DataFrame) -> dict[str, Any]:
    public_data, omitted = _public_preview_data(data)
    payload = _limited_dataframe_payload(
        public_data,
        preview_limit=RESOURCE_PREVIEW_RECORD_LIMIT,
    )
    if omitted:
        payload["omitted_columns"] = omitted
    return payload


def parquet_payload(
        query: str,
        data: Mapping[str, pd.DataFrame] | pd.DataFrame,
        *,
        preview_limit: int = RESOURCE_PREVIEW_RECORD_LIMIT
    ) -> dict[str, Any]:
    if isinstance(data, pd.DataFrame):
        public_data, omitted = _public_preview_data(data)
        payload = {
            "query": query,
            **_limited_dataframe_payload(
                public_data,
                preview_limit=preview_limit,
            ),
        }
        if omitted:
            payload["omitted_columns"] = omitted
        return payload

    return {
        "query": query,
        "datasets": {
            name: dataframe_payload_with_limit(dataset, preview_limit)
            for name, dataset in data.items()
        },
    }


def dataframe_payload_with_limit(
        data: pd.DataFrame,
        preview_limit: int,
    ) -> dict[str, Any]:
    public_data, omitted = _public_preview_data(data)
    payload = _limited_dataframe_payload(
        public_data,
        preview_limit=preview_limit,
    )
    if omitted:
        payload["omitted_columns"] = omitted
    return payload


def limited_tool_payload(
        dataset: str,
        source_data: pd.DataFrame,
        filtered_data: pd.DataFrame,
        returned_data: pd.DataFrame,
        available_data: pd.DataFrame,
        filters: Mapping[str, Any],
        data_cache: DataCacheService
    ) -> dict[str, Any]:
    limit = filters["limit"]
    offset = filters.get("offset", 0) or 0
    available_row_count = len(available_data)
    returned_count = len(returned_data)
    has_more = offset + returned_count < available_row_count
    next_offset = offset + returned_count if "offset" in filters and has_more else None
    status = data_cache.status_snapshot()
    payload = {
        "schema_version": 1,
        "dataset": dataset,
        "total_row_count": len(source_data),
        "row_count": len(filtered_data),
        "returned_count": returned_count,
        "limit": limit,
        "has_more": has_more,
        "next_offset": next_offset,
        "freshness": status["last_success_at"],
        "data_status": status["status"],
        "filters": filters,
        "columns": list(returned_data.columns),
        "records": records_from_dataframe(returned_data),
    }
    if "offset" in filters:
        payload["offset"] = filters["offset"]
    if "aggregation" in filters:
        payload["aggregation"] = filters["aggregation"]
    return payload


def safe_json_dumps(
        payload: dict[str, Any],
        *,
        max_bytes: int | None = None,
        suggestions: list[str] | None = None,
        **json_kwargs: Any
    ) -> str:
    if max_bytes is None:
        max_bytes = MAX_SERIALIZED_RESPONSE_BYTES
    text = json.dumps(payload, **json_kwargs)
    estimated_bytes = len(text.encode("utf-8"))
    if estimated_bytes <= max_bytes:
        return text

    too_large_payload = response_too_large_payload(
        payload=payload,
        estimated_bytes=estimated_bytes,
        max_bytes=max_bytes,
        suggestions=suggestions,
    )
    log_event(
        "response_too_large",
        max_bytes=max_bytes,
        estimated_bytes=estimated_bytes,
        context=too_large_payload["context"],
        suggestions_count=len(too_large_payload["suggestions"]),
    )
    return json.dumps(too_large_payload)


def response_too_large_payload(
        *,
        payload: Mapping[str, Any],
        estimated_bytes: int,
        max_bytes: int,
        suggestions: list[str] | None = None
    ) -> dict[str, Any]:
    return {
        "error": "response_too_large",
        "message": "Serialized MCP response exceeds the configured size limit.",
        "max_bytes": max_bytes,
        "estimated_bytes": estimated_bytes,
        "context": _response_context(payload),
        "suggestions": suggestions or DEFAULT_TOO_LARGE_SUGGESTIONS,
    }


def records_from_dataframe(data: pd.DataFrame) -> list[dict[str, Any]]:
    columns = [str(column) for column in data.columns]
    return [
        {
            column: json_safe_value(value)
            for column, value in zip(columns, row, strict=True)
        }
        for row in data.itertuples(index=False, name=None)
    ]


def json_safe_value(value: Any) -> Any:
    if hasattr(value, "as_py"):
        try:
            value = value.as_py()
        except (TypeError, ValueError):
            pass

    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {
            str(key): json_safe_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [json_safe_value(item) for item in value]
    if not isinstance(value, (str, bytes)) and hasattr(value, "tolist"):
        try:
            listed = value.tolist()
        except (TypeError, ValueError):
            listed = value
        if listed is not value:
            return json_safe_value(listed)
    if not isinstance(value, (str, bytes)) and hasattr(value, "item"):
        try:
            item = value.item()
        except (TypeError, ValueError):
            item = value
        if item is not value:
            return json_safe_value(item)

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value


def _limited_dataframe_payload(
        data: pd.DataFrame,
        *,
        preview_limit: int
    ) -> dict[str, Any]:
    preview = _preview_dataframe(data, preview_limit)
    row_count = len(data)
    returned_count = len(preview)
    has_more = returned_count < row_count
    return {
        "row_count": row_count,
        "total_row_count": row_count,
        "returned_count": returned_count,
        "has_more": has_more,
        "truncated": has_more,
        "records": records_from_dataframe(preview),
    }


def _preview_dataframe(data: pd.DataFrame, preview_limit: int) -> pd.DataFrame:
    return data.iloc[:max(preview_limit, 0)]


def _public_preview_data(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    omitted = sorted(PRIVATE_PREVIEW_COLUMNS.intersection(data.columns))
    return data.drop(columns=omitted, errors="ignore"), omitted


def _response_context(payload: Mapping[str, Any]) -> dict[str, Any]:
    context_keys = (
        "dataset",
        "query",
        "total_row_count",
        "row_count",
        "returned_count",
        "limit",
        "offset",
        "aggregation",
    )
    context = {
        key: payload[key]
        for key in context_keys
        if key in payload
    }
    if "datasets" in payload and isinstance(payload["datasets"], Mapping):
        context["datasets"] = {
            name: {
                key: details[key]
                for key in (
                    "total_row_count",
                    "row_count",
                    "returned_count",
                    "has_more",
                    "truncated",
                )
                if isinstance(details, Mapping) and key in details
            }
            for name, details in payload["datasets"].items()
        }
    return context
