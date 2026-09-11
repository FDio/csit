#!/usr/bin/env python3
"""Starlette client for the CSIT MCP dashboard."""

import inspect
import json
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from os import environ
from typing import Any
from urllib.parse import urlencode

from fastmcp import Client
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from uvicorn import run

from dashboard import (
    DATASETS,
    STATIC_DIR,
    render_dashboard_page,
    render_status_page,
)
from statistics_export import (
    MISSING_TEST_ID,
    canonical_failed_test_name as _canonical_failed_test_name,
    csv_export_bytes,
    default_export_filename,
    sanitized_export_filename,
    statistics_export_table,
    xlsx_export_bytes,
)
from trending_export import (
    csv_export_bytes as trending_csv_export_bytes,
    default_trending_export_filename,
    sanitized_trending_export_filename,
    trending_export_table,
    xlsx_export_bytes as trending_xlsx_export_bytes,
)


MCP_SERVER_URL = environ.get("MCP_SERVER_URL", "http://mcp-server:8000")
MCP_PATH = environ.get("MCP_PATH", "/mcp")
ROUTE_PREFIX = "/"
LOGGER = logging.getLogger("csit-mcp-client")
STATISTICS_LIMIT = 10_000
STATISTICS_FILTERS = ("dut", "test_type", "cadence", "testbed")
RUN_DETAILS_PAGE_SIZE = 1_000
EXPORT_FORMATS = {"csv", "xlsx"}
TRENDING_FILTERS = (
    "dut",
    "area",
    "test",
    "infra",
    "testbed",
    "framesize",
    "cores",
    "test_type",
)
TRENDING_PAGE_SIZE = 500


class MCPClientState:
    """Track MCP connection state and reconnect lazily when needed."""

    def __init__(self, url: str, client_factory=Client) -> None:
        self.url = url
        self._client_factory = client_factory
        self._client = None
        self._client_context = None
        self._lock = None
        self.last_connected_at: str | None = None
        self.last_error: str | None = None
        self.last_error_at: str | None = None
        self.server: dict[str, Any] | None = None
        self.tools: list[str] = []
        self.resources: list[str] = []
        self.prompts: list[str] = []
        self.reconnect_attempts = 0

    @property
    def lock(self):
        if self._lock is None:
            import asyncio

            self._lock = asyncio.Lock()
        return self._lock

    def is_connected(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(self._client.is_connected())
        except Exception:
            return False

    async def ensure_connected(self):
        """Return a connected MCP client, reconnecting if needed."""

        if self.is_connected():
            return self._client
        async with self.lock:
            if self.is_connected():
                return self._client

            self.reconnect_attempts += 1
            await self.close()
            context = self._client_factory(self.url)
            try:
                client = await context.__aenter__()
                result = await client.initialize(timeout=10.0)
                tools = await client.list_tools()
                resources = await client.list_resources()
                prompts = await client.list_prompts()
            except Exception as err:
                await self._close_context(context)
                self._record_error(err)
                raise

            self._client_context = context
            self._client = client
            self.last_connected_at = self._utcnow()
            self.last_error = None
            self.last_error_at = None
            self.server = self._server_info(result)
            self.tools = self._item_names(tools)
            self.resources = self._item_names(resources)
            self.prompts = self._item_names(prompts)
            self._log_connection_status()
            return client

    async def close(self) -> None:
        """Close the active MCP client context if one exists."""

        if self._client_context is None:
            self._client = None
            return
        context = self._client_context
        self._client_context = None
        self._client = None
        await self._close_context(context)

    def status(self) -> dict[str, Any]:
        """Return JSON-ready client and MCP connection status."""

        return {
            "url": self.url,
            "connected": self.is_connected(),
            "last_connected_at": self.last_connected_at,
            "last_error": self.last_error,
            "last_error_at": self.last_error_at,
            "server": self.server,
            "tools": self.tools,
            "resources": self.resources,
            "prompts": self.prompts,
            "reconnect_attempts": self.reconnect_attempts,
        }

    async def _close_context(self, context) -> None:
        try:
            result = context.__aexit__(None, None, None)
            if inspect.isawaitable(result):
                await result
        except Exception as err:
            self._record_error(err)

    def _record_error(self, err: Exception) -> None:
        self.last_error = f"{type(err).__name__}: {err}"
        self.last_error_at = self._utcnow()

    def _log_connection_status(self) -> None:
        LOGGER.info("Connected: %s", self.is_connected())
        if self.server:
            LOGGER.info("MCP Server: %s", self.server.get("name"))
        LOGGER.info("MCP Available tools: %s", self.tools)
        LOGGER.info("MCP Available resources: %s", self.resources)
        LOGGER.info("MCP Available prompts: %s", self.prompts)

    @staticmethod
    def _server_info(result) -> dict[str, Any] | None:
        server_info = getattr(result, "serverInfo", None)
        if server_info is None:
            return None
        return {
            "name": getattr(server_info, "name", None),
            "version": getattr(server_info, "version", None),
        }

    @staticmethod
    def _item_names(items) -> list[str]:
        return [str(getattr(item, "name", item)) for item in items]

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(tz=UTC).isoformat()


def make_lifespan(mcp_state: MCPClientState):
    @asynccontextmanager
    async def lifespan(app):
        """Try initial MCP connection without failing Starlette startup."""

        app.state.mcp_state = mcp_state
        try:
            await mcp_state.ensure_connected()
        except Exception as err:
            LOGGER.info(
                "MCP initial connection failed: %s: %s",
                type(err).__name__,
                err,
            )
        yield
        await mcp_state.close()

    return lifespan


def _status_payload(mcp_state: MCPClientState) -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "mcp-client",
        "mcp": mcp_state.status(),
    }


async def health_check(request: Request) -> JSONResponse:
    """Return client liveness and MCP connection status."""

    mcp_state: MCPClientState = request.app.state.mcp_state
    try:
        await mcp_state.ensure_connected()
    except Exception:
        pass
    return JSONResponse(_status_payload(mcp_state), status_code=200)


async def render_dashboard(request: Request) -> HTMLResponse:
    """Render the selected dashboard dataset from MCP tool payloads."""

    mcp_state: MCPClientState = request.app.state.mcp_state
    selected_dataset = _selected_dataset(request)
    try:
        client = await mcp_state.ensure_connected()
        datasets_payload = await _call_json_tool(client, "datasets")
        statistics_payload = None
        if selected_dataset == "statistics":
            statistics_payload = await _call_json_tool(
                client,
                "job_statistics",
                _statistics_arguments(request),
            )
        trending_catalog_payload = None
        trending_series_payload = None
        selected_trending_series: list[str] = []
        if selected_dataset == "trending":
            selected_trending_series = _selected_trending_series(request)
            trending_catalog_payload = await _call_json_tool(
                client,
                "trending_catalog",
                _trending_arguments(request),
            )
            action = request.query_params.get("trending_action")
            if action and not trending_catalog_payload.get("error"):
                filters = trending_catalog_payload.get("filters") or {}
                if action == "add":
                    matches = await _all_trending_catalog_records(
                        client,
                        trending_catalog_payload,
                    )
                    selected_trending_series = list(dict.fromkeys([
                        *selected_trending_series,
                        *(
                            str(record.get("series_id"))
                            for record in matches
                            if record.get("series_id")
                        ),
                    ]))
                elif action == "remove_selected":
                    removed = set(request.query_params.getlist("remove"))
                    selected_trending_series = [
                        value for value in selected_trending_series
                        if value not in removed
                    ]
                elif action == "remove_all":
                    selected_trending_series = []
                if action in {"add", "remove_selected", "remove_all"}:
                    return RedirectResponse(
                        _trending_url(filters, selected_trending_series),
                        status_code=303,
                    )
            if selected_trending_series:
                trending_series_payload = await _all_trending_points(
                    client,
                    selected_trending_series,
                )
    except Exception as err:
        mcp_state._record_error(err)
        return HTMLResponse(
            render_status_page(mcp_state.status()),
            status_code=503,
        )

    return HTMLResponse(
        render_dashboard_page(
            selected_dataset,
            datasets_payload,
            mcp_state.status(),
            statistics_payload,
            trending_catalog_payload,
            trending_series_payload,
            selected_trending_series,
        ),
        status_code=200,
    )


async def statistics_run_details(request: Request) -> JSONResponse:
    """Return all failed test IDs for one statistics run."""

    job = str(request.query_params.get("job") or "").strip()
    build_value = request.query_params.get("build")
    if not job:
        return _run_details_error(
            400,
            "validation_error",
            "A non-empty job query parameter is required.",
        )
    try:
        build = int(str(build_value))
    except (TypeError, ValueError):
        return _run_details_error(
            400,
            "validation_error",
            "Build must be a non-negative integer.",
        )
    if build < 0:
        return _run_details_error(
            400,
            "validation_error",
            "Build must be a non-negative integer.",
        )

    mcp_state: MCPClientState = request.app.state.mcp_state
    try:
        client = await mcp_state.ensure_connected()
        failed_tests = await _failed_test_ids(client, job=job, build=build)
    except _MalformedUpstreamResponse as err:
        return _run_details_error(502, "invalid_upstream_response", str(err))
    except _MCPDataUnavailable as err:
        return _run_details_error(503, err.error, err.message)
    except Exception as err:
        mcp_state._record_error(err)
        return _run_details_error(
            503,
            "data_unavailable",
            f"Failed to load run details: {type(err).__name__}: {err}",
        )

    return JSONResponse(
        {
            "job": job,
            "build": build,
            "failed_count": len(failed_tests),
            "failed_tests": failed_tests,
        }
    )


async def statistics_export(request: Request) -> Response:
    """Generate a complete Statistics CSV or XLSX export on demand."""

    export_format = str(request.query_params.get("format") or "xlsx").lower()
    if export_format not in EXPORT_FORMATS:
        return _export_error(
            400,
            "validation_error",
            "Format must be either xlsx or csv.",
        )

    mcp_state: MCPClientState = request.app.state.mcp_state
    try:
        client = await mcp_state.ensure_connected()
        payload = await _call_json_tool(
            client,
            "job_statistics",
            _statistics_arguments(request),
        )
        _raise_for_export_payload_error(payload)
        records = _export_statistics_records(payload)
        failed_tests = await _export_failed_tests(client, records)
    except _MalformedUpstreamResponse as err:
        return _export_error(502, "invalid_upstream_response", str(err))
    except _ExportValidationError as err:
        return _export_error(400, "validation_error", str(err))
    except _MCPDataUnavailable as err:
        return _export_error(503, err.error, err.message)
    except Exception as err:
        mcp_state._record_error(err)
        return _export_error(
            503,
            "data_unavailable",
            f"Failed to generate Statistics export: {type(err).__name__}: {err}",
        )

    filters = payload.get("filters")
    if not isinstance(filters, dict):
        return _export_error(
            502,
            "invalid_upstream_response",
            "The job_statistics response does not contain normalized filters.",
        )
    dut = str(filters.get("dut") or request.query_params.get("dut") or "dut")
    headers, rows = statistics_export_table(
        records,
        dut=dut,
        failed_tests=failed_tests,
    )
    default_name = default_export_filename(filters)
    filename = sanitized_export_filename(
        request.query_params.get("filename"),
        default_name,
        export_format,
    )
    if export_format == "csv":
        content = csv_export_bytes(headers, rows)
        media_type = "text/csv; charset=utf-8"
    else:
        content = xlsx_export_bytes(headers, rows)
        media_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    return Response(
        content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


async def trending_export(request: Request) -> Response:
    """Generate a complete selected-series Trending CSV or XLSX export."""

    export_format = str(request.query_params.get("format") or "xlsx").lower()
    if export_format not in EXPORT_FORMATS:
        return _export_error(
            400,
            "validation_error",
            "Format must be either xlsx or csv.",
        )
    selected_series = _selected_trending_series(request)
    if not selected_series:
        return _export_error(
            400,
            "validation_error",
            "At least one series query parameter is required.",
        )

    mcp_state: MCPClientState = request.app.state.mcp_state
    try:
        client = await mcp_state.ensure_connected()
        payload = await _all_trending_points(client, selected_series)
        _raise_for_trending_export_payload_error(payload)
        records = _validated_records(payload, "trending_series")
    except _MalformedUpstreamResponse as err:
        return _export_error(502, "invalid_upstream_response", str(err))
    except _ExportValidationError as err:
        return _export_error(400, "validation_error", str(err))
    except _MCPDataUnavailable as err:
        return _export_error(503, err.error, err.message)
    except Exception as err:
        mcp_state._record_error(err)
        return _export_error(
            503,
            "data_unavailable",
            f"Failed to generate Trending export: {type(err).__name__}: {err}",
        )

    headers, rows = trending_export_table(records)
    default_name = default_trending_export_filename()
    filename = sanitized_trending_export_filename(
        request.query_params.get("filename"),
        default_name,
        export_format,
    )
    if export_format == "csv":
        content = trending_csv_export_bytes(headers, rows)
        media_type = "text/csv; charset=utf-8"
    else:
        content = trending_xlsx_export_bytes(headers, rows)
        media_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    return Response(
        content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


async def _failed_test_ids(client, *, job: str, build: int) -> list[str]:
    failed_tests: list[str] = []
    offset = 0
    seen_offsets = {offset}

    while True:
        payload = await _call_json_tool(
            client,
            "trending",
            {
                "job": job,
                "build": build,
                "passed": False,
                "offset": offset,
                "aggregation": "none",
                "columns": ["test_id"],
                "limit": RUN_DETAILS_PAGE_SIZE,
            },
        )
        error = payload.get("error")
        if error:
            message = str(payload.get("message") or "Trending data is unavailable.")
            if error in {"empty_response", "invalid_json", "invalid_payload"}:
                raise _MalformedUpstreamResponse(message)
            raise _MCPDataUnavailable(str(error), message)

        records = payload.get("records")
        if not isinstance(records, list):
            raise _MalformedUpstreamResponse(
                "The trending tool response does not contain a records list."
            )
        for record in records:
            if not isinstance(record, dict):
                raise _MalformedUpstreamResponse(
                    "The trending tool returned a non-object record."
                )
            test_id = record.get("test_id")
            normalized = str(test_id).strip() if test_id is not None else ""
            failed_tests.append(
                _canonical_failed_test_name(normalized)
                if normalized
                else MISSING_TEST_ID
            )

        has_more = payload.get("has_more")
        if not isinstance(has_more, bool):
            raise _MalformedUpstreamResponse(
                "The trending tool response has invalid pagination metadata."
            )
        if not has_more:
            return failed_tests

        next_offset = payload.get("next_offset")
        if (
            isinstance(next_offset, bool)
            or not isinstance(next_offset, int)
            or next_offset <= offset
            or next_offset in seen_offsets
        ):
            raise _MalformedUpstreamResponse(
                "The trending tool response has an invalid next_offset."
            )
        offset = next_offset
        seen_offsets.add(offset)


def _run_details_error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        {"error": error, "message": message},
        status_code=status_code,
    )


class _MCPDataUnavailable(Exception):
    def __init__(self, error: str, message: str) -> None:
        super().__init__(message)
        self.error = error
        self.message = message


class _MalformedUpstreamResponse(Exception):
    pass


def _raise_for_export_payload_error(payload: dict[str, Any]) -> None:
    error = payload.get("error")
    if not error:
        return
    message = str(payload.get("message") or "Statistics data is unavailable.")
    if error in {"empty_response", "invalid_json", "invalid_payload"}:
        raise _MalformedUpstreamResponse(message)
    if error == "validation_error":
        raise _ExportValidationError(message)
    raise _MCPDataUnavailable(str(error), message)


def _export_statistics_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    has_more = payload.get("has_more")
    if not isinstance(has_more, bool):
        raise _MalformedUpstreamResponse(
            "The job_statistics response has invalid pagination metadata."
        )
    if has_more:
        raise _MalformedUpstreamResponse(
            "The Statistics result exceeds the 10000-row export limit. "
            "Choose narrower filters before downloading."
        )
    records = payload.get("records")
    if not isinstance(records, list) or not all(
            isinstance(record, dict) for record in records
    ):
        raise _MalformedUpstreamResponse(
            "The job_statistics response does not contain a valid records list."
        )
    return records


async def _export_failed_tests(
        client,
        records: list[dict[str, Any]],
) -> dict[tuple[str, int], list[str]]:
    expected_counts: dict[tuple[str, int], int] = {}
    for record in records:
        if not record.get("counts_available"):
            continue
        failed_count = _non_negative_integer(record.get("failed_count"))
        if failed_count is None:
            raise _MalformedUpstreamResponse(
                "A Statistics record has an invalid failed_count."
            )
        if failed_count == 0:
            continue
        job = str(record.get("job") or "").strip()
        build = _non_negative_integer(record.get("build"))
        if not job or build is None:
            raise _MalformedUpstreamResponse(
                "A failed Statistics run has no valid job/build identity."
            )
        key = (job, build)
        previous = expected_counts.get(key)
        if previous is not None and previous != failed_count:
            raise _MalformedUpstreamResponse(
                "Duplicate Statistics records disagree on failed_count."
            )
        expected_counts[key] = failed_count

    failed_tests: dict[tuple[str, int], list[str]] = {}
    for (job, build), expected_count in expected_counts.items():
        tests = await _failed_test_ids(client, job=job, build=build)
        if len(tests) != expected_count:
            raise _MalformedUpstreamResponse(
                f"Failed-test rows for {job}/{build} are incomplete: "
                f"expected {expected_count}, received {len(tests)}."
            )
        failed_tests[(job, build)] = tests
    return failed_tests


def _non_negative_integer(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = int(str(value))
    except (TypeError, ValueError):
        return None
    return number if number >= 0 and str(value).strip() == str(number) else None


class _ExportValidationError(Exception):
    pass


def _export_error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        {"error": error, "message": message},
        status_code=status_code,
    )


def _selected_dataset(request: Request) -> str:
    selected = str(request.query_params.get("dataset") or "statistics")
    return selected if selected in DATASETS else "statistics"


def _statistics_arguments(request: Request) -> dict[str, Any]:
    arguments: dict[str, Any] = {
        "limit": STATISTICS_LIMIT,
        "select_defaults": True,
    }
    for field in STATISTICS_FILTERS:
        value = request.query_params.get(field)
        if value is not None and str(value).strip():
            arguments[field] = str(value).strip()
    return arguments


def _trending_arguments(request: Request) -> dict[str, Any]:
    arguments: dict[str, Any] = {
        "select_defaults": True,
        "offset": 0,
        "limit": TRENDING_PAGE_SIZE,
    }
    for field in TRENDING_FILTERS:
        value = request.query_params.get(field)
        if value is not None and str(value).strip():
            arguments[field] = str(value).strip()
    return arguments


def _selected_trending_series(request: Request) -> list[str]:
    return list(dict.fromkeys(
        value.strip()
        for value in request.query_params.getlist("series")
        if value.strip()
    ))


async def _all_trending_catalog_records(
        client,
        first_payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
    records = _validated_records(first_payload, "trending_catalog")
    payload = first_payload
    seen_offsets = {0}
    while _validated_has_more(payload, "trending_catalog"):
        next_offset = _validated_next_offset(
            payload,
            seen_offsets,
            "trending_catalog",
        )
        filters = payload.get("filters")
        if not isinstance(filters, dict):
            raise _MalformedUpstreamResponse(
                "The trending_catalog response has no normalized filters."
            )
        arguments = {
            field: filters.get(field)
            for field in TRENDING_FILTERS
            if filters.get(field) is not None
        }
        arguments.update({
            "select_defaults": True,
            "offset": next_offset,
            "limit": TRENDING_PAGE_SIZE,
        })
        payload = await _call_json_tool(client, "trending_catalog", arguments)
        _raise_for_trending_payload_error(payload, "trending_catalog")
        records.extend(_validated_records(payload, "trending_catalog"))
    return records


async def _all_trending_points(
        client,
        selected_series: list[str],
    ) -> dict[str, Any]:
    arguments = {
        "series": selected_series,
        "offset": 0,
        "limit": TRENDING_PAGE_SIZE,
    }
    first = await _call_json_tool(client, "trending_series", arguments)
    if first.get("error"):
        return first
    records = _validated_records(first, "trending_series")
    payload = first
    seen_offsets = {0}
    while _validated_has_more(payload, "trending_series"):
        next_offset = _validated_next_offset(
            payload,
            seen_offsets,
            "trending_series",
        )
        payload = await _call_json_tool(
            client,
            "trending_series",
            {
                "series": selected_series,
                "offset": next_offset,
                "limit": TRENDING_PAGE_SIZE,
            },
        )
        _raise_for_trending_payload_error(payload, "trending_series")
        records.extend(_validated_records(payload, "trending_series"))
    merged = dict(first)
    merged["records"] = records
    merged["returned_count"] = len(records)
    merged["has_more"] = False
    merged["next_offset"] = None
    return merged


def _validated_records(
        payload: dict[str, Any],
        tool_name: str,
    ) -> list[dict[str, Any]]:
    records = payload.get("records")
    if not isinstance(records, list) or not all(
            isinstance(record, dict) for record in records
        ):
        raise _MalformedUpstreamResponse(
            f"The {tool_name} response does not contain a valid records list."
        )
    return list(records)


def _validated_has_more(payload: dict[str, Any], tool_name: str) -> bool:
    has_more = payload.get("has_more")
    if not isinstance(has_more, bool):
        raise _MalformedUpstreamResponse(
            f"The {tool_name} response has invalid pagination metadata."
        )
    return has_more


def _validated_next_offset(
        payload: dict[str, Any],
        seen_offsets: set[int],
        tool_name: str,
    ) -> int:
    next_offset = payload.get("next_offset")
    current_offset = payload.get("offset", 0)
    if (
            isinstance(next_offset, bool)
            or not isinstance(next_offset, int)
            or next_offset <= current_offset
            or next_offset in seen_offsets
        ):
        raise _MalformedUpstreamResponse(
            f"The {tool_name} response has an invalid next_offset."
        )
    seen_offsets.add(next_offset)
    return next_offset


def _raise_for_trending_payload_error(
        payload: dict[str, Any],
        tool_name: str,
    ) -> None:
    error = payload.get("error")
    if not error:
        return
    message = str(payload.get("message") or f"{tool_name} is unavailable.")
    if error in {"empty_response", "invalid_json", "invalid_payload"}:
        raise _MalformedUpstreamResponse(message)
    raise _MCPDataUnavailable(str(error), message)


def _raise_for_trending_export_payload_error(payload: dict[str, Any]) -> None:
    error = payload.get("error")
    if not error:
        return
    message = str(payload.get("message") or "Trending data is unavailable.")
    if error in {"empty_response", "invalid_json", "invalid_payload"}:
        raise _MalformedUpstreamResponse(message)
    if error == "validation_error":
        raise _ExportValidationError(message)
    raise _MCPDataUnavailable(str(error), message)


def _trending_url(filters: dict[str, Any], series: list[str]) -> str:
    query: list[tuple[str, str]] = [("dataset", "trending")]
    for field in TRENDING_FILTERS:
        value = filters.get(field)
        if value is not None and str(value):
            query.append((field, str(value)))
    query.extend(("series", value) for value in sorted(set(series)))
    return "/?" + urlencode(query)


async def _call_json_tool(
        client,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
    """Call one MCP tool and parse its first text block as a JSON object."""

    result = await client.call_tool(tool_name, arguments or {})
    text = _first_text_content(result)
    if not text:
        return {
            "error": "empty_response",
            "message": f"The {tool_name} tool returned no text content.",
        }
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as err:
        return {
            "error": "invalid_json",
            "message": f"The {tool_name} tool returned invalid JSON: {err}",
        }
    if not isinstance(payload, dict):
        return {
            "error": "invalid_payload",
            "message": f"The {tool_name} tool returned a non-object payload.",
        }
    return payload


def _first_text_content(result) -> str:
    for block in getattr(result, "content", []) or []:
        if getattr(block, "type", None) == "text":
            return str(getattr(block, "text", ""))
    return ""


def create_app(
        *,
        client_factory=Client,
        mcp_server_url: str = MCP_SERVER_URL,
        mcp_path: str = MCP_PATH,
    ) -> Starlette:
    """Create the Starlette dashboard client app."""

    mcp_state = MCPClientState(
        url=f"{mcp_server_url}{mcp_path}",
        client_factory=client_factory,
    )
    return Starlette(
        lifespan=make_lifespan(mcp_state),
        routes=[
            Route(ROUTE_PREFIX, render_dashboard),
            Route("/health", health_check),
            Route("/api/statistics/run-details", statistics_run_details),
            Route("/api/statistics/export", statistics_export),
            Route("/api/trending/export", trending_export),
            Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
        ],
    )


app = create_app()

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=7860)
