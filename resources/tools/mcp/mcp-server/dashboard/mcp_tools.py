"""MCP tool and resource registration for CSIT dashboard data."""

import json

import pandas as pd
from mcp.types import ToolAnnotations
from prefab_ui.app import PrefabApp

from .services.analysis import (
    compare_hosts_analysis_payload,
    filtered_find_anomalies_payload,
    filtered_find_regressions_payload,
    filtered_top_failures_payload,
    filtered_trend_summary_payload,
    validate_analysis_dataset,
)
from .services.data_cache import DataCacheError, DataCacheService
from .services.coverage import (
    DEFAULT_COVERAGE_LIMIT,
)
from .services.comparison import (
    DEFAULT_COMPARISON_LIMIT,
)
from .services.discovery import DEFAULT_VALUES_LIMIT, DiscoveryService
from .services.iterative import (
    DEFAULT_ITERATIVE_LIMIT,
)
from .services.index_registry import DerivedIndexRegistry
from .services.query import (
    DEFAULT_TOOL_LIMIT,
    job_statistics_payload,
    result_tool_payload,
)
from .services.query_guard import QueryAdmissionController
from .services.serialization import cache_error_payload, parquet_payload
from .services.serialization import (
    RESOURCE_TOO_LARGE_SUGGESTIONS,
    safe_json_dumps,
    validation_error_payload,
)
from .services.observability import log_event
from .services.result_metadata import ResultMetadataService
from .services.telemetry import (
    DEFAULT_ANALYSIS_LIMIT,
    DEFAULT_TELEMETRY_LIMIT,
    TELEMETRY_DATASETS,
    telemetry_anomalies_payload,
    telemetry_metric_values_payload,
    telemetry_metrics_payload,
    telemetry_trend_summary_payload,
)
from .services.telemetry_query import (
    DEFAULT_TIMESERIES_LIMIT,
    TelemetryQueryService,
)
from .services.telemetry_locator import (
    DEFAULT_CATALOG_LIMIT as DEFAULT_TELEMETRY_CATALOG_LIMIT,
    telemetry_catalog_payload,
)
from .services.trending import (
    DEFAULT_TRENDING_LIMIT,
)
from .settings import AppSettings
from .ui.dashboard import build_dashboard, build_status_page


READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False
)
PUBLIC_TOOLS = (
    "datasets",
    "columns",
    "values",
    "schema",
    "compare_hosts",
    "trend_summary",
    "find_regressions",
    "find_anomalies",
    "top_failures",
    "telemetry_metrics",
    "telemetry_metric_values",
    "telemetry_trend_summary",
    "telemetry_anomalies",
    "telemetry_catalog",
    "telemetry_timeseries",
    "job_statistics",
    "trending_catalog",
    "trending_series",
    "trending",
    "iterative_catalog",
    "iterative_series",
    "iterative",
    "coverage_catalog",
    "coverage_tables",
    "coverage",
    "comparison_catalog",
    "comparison_table",
    "comparison_data",
    "dashboard",
)
PUBLIC_RESOURCES = ("server://info",)
PRIVATE_RESOURCES = ("data://parquet/{query}",)


def register_mcp_tools(mcp, data_cache: DataCacheService, settings: AppSettings) -> None:
    """Register CSIT MCP resources and tools."""

    result_metadata = ResultMetadataService()
    discovery = DiscoveryService(
        data_cache=data_cache,
        settings=settings,
        result_metadata=result_metadata,
    )
    derived_indexes = DerivedIndexRegistry()
    trending_service = derived_indexes.trending
    telemetry_query_service = TelemetryQueryService(
        settings=settings,
    )
    iterative_service = derived_indexes.iterative
    coverage_service = derived_indexes.coverage
    comparison_service = derived_indexes.comparison
    statistics_service = derived_indexes.statistics
    query_admission = QueryAdmissionController(settings)
    register_listener = getattr(data_cache, "register_generation_listener", None)
    if register_listener is not None:
        register_listener(derived_indexes.clear)
        register_listener(telemetry_query_service.clear)
    register_reporter = getattr(data_cache, "register_memory_reporter", None)
    if register_reporter is not None:
        register_reporter("derived_indexes", derived_indexes.memory_snapshot)
        register_reporter(
            "telemetry_queries", telemetry_query_service.memory_snapshot
        )

    @mcp.resource(
        uri="server://info",
        name="ServerInfo",
        tags={"fd.io", "public", "read", "server", "info"},
        description="Provides the server info.",
    )
    def server_info() -> str:
        """Return metadata describing the FastMCP server and exposed endpoints."""
        info_data = {
            "name": settings.server_name,
            "description": settings.server_description,
            "version": settings.server_version,
            "capabilities": {
                "tools": len(PUBLIC_TOOLS),
                "resources": 1,
                "prompts": 0,
            },
            "endpoints": {
                "tools": list(PUBLIC_TOOLS),
                "resources": list(PUBLIC_RESOURCES),
                "public_resources": list(PUBLIC_RESOURCES),
                "private_resources": list(PRIVATE_RESOURCES),
            },
            "data": data_cache.status_snapshot(),
            "telemetry_queries": telemetry_query_service.status_snapshot(),
            "query_admission": query_admission.status_snapshot(),
        }
        return json.dumps(info_data, indent=2)

    @mcp.resource(
        uri="data://parquet/{query}",
        name="DataParquet",
        tags={"fd.io", "private", "read", "data", "parquet"},
        description="Provides cached CSIT parquet data as serialized JSON."
    )
    def get_parquet(query: str = "all") -> str:
        """Return cached CSIT parquet data for the requested category."""
        try:
            data = data_cache.get_parquet(query=query)
            payload = parquet_payload(query=query, data=data)
            return _serialize_resource_payload(
                "data://parquet/{query}",
                query,
                payload,
                data_cache=data_cache,
                suggestions=RESOURCE_TOO_LARGE_SUGGESTIONS,
            )
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_resource_payload(
                "data://parquet/{query}",
                query,
                payload,
                data_cache=data_cache,
            )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="datasets",
        tags={"fd.io", "public", "read", "discovery", "datasets"},
        description=(
            "Lists cached CSIT datasets with status, row counts, and "
            "configured partitions."
        ),
    )
    def datasets() -> str:
        """Return discovery metadata for all CSIT datasets."""
        payload = discovery.datasets_payload()
        return _serialize_discovery_payload(
            "datasets",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="columns",
        tags={"fd.io", "public", "read", "discovery", "columns"},
        description=(
            "Lists configured and cached columns for a CSIT dataset."
        ),
    )
    def columns(dataset: str) -> str:
        """Return column metadata for one CSIT dataset."""
        payload = discovery.columns_payload(dataset=dataset)
        return _serialize_discovery_payload(
            "columns",
            payload,
            dataset=dataset,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="values",
        tags={"fd.io", "public", "read", "discovery", "values"},
        description=(
            "Lists common values for one column in a cached CSIT dataset."
        ),
    )
    def values(
            dataset: str,
            column: str,
            limit: int = DEFAULT_VALUES_LIMIT
        ) -> str:
        """Return common values for one dataset column."""
        payload = discovery.values_payload(
            dataset=dataset,
            column=column,
            limit=limit,
        )
        return _serialize_discovery_payload(
            "values",
            payload,
            dataset=dataset,
            column=column,
            limit=limit,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="schema",
        tags={"fd.io", "public", "read", "discovery", "schema"},
        description=(
            "Lists configured schema and partition metadata for a CSIT dataset."
        ),
    )
    def schema(dataset: str) -> str:
        """Return configured schema metadata for one CSIT dataset."""
        payload = discovery.schema_payload(dataset=dataset)
        return _serialize_discovery_payload(
            "schema",
            payload,
            dataset=dataset,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="compare_hosts",
        tags={"fd.io", "public", "read", "analysis", "compare", "hosts"},
        description=(
            "Compares one CSIT result column across host groups with compact "
            "statistics and best/worst summaries."
        ),
    )
    def compare_hosts(
            dataset: str,
            result_column: str,
            test_id: str | None = None,
            test_type: str | None = None,
            dut_type: str | None = None,
            job: str | None = None,
            release: str | None = None,
            build: int | None = None,
            passed: bool | None = None,
            preferred_direction: str | None = None
        ) -> str:
        """Compare a result column across host groups."""
        data, error_payload = _analysis_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "compare_hosts",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        payload = compare_hosts_analysis_payload(
            dataset=dataset,
            data=data,
            result_column=result_column,
            result_metadata=result_metadata,
            status=data_cache.status_snapshot(),
            test_id=test_id,
            test_type=test_type,
            dut_type=dut_type,
            job=job,
            release=release,
            build=build,
            passed=passed,
            preferred_direction=preferred_direction,
        )
        return _serialize_analysis_tool_payload(
            "compare_hosts",
            dataset,
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="trend_summary",
        tags={"fd.io", "public", "read", "analysis", "trend"},
        description=(
            "Summarizes recent versus baseline behavior for one CSIT result "
            "column."
        ),
    )
    def trend_summary(
            dataset: str,
            result_column: str,
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
        ) -> str:
        """Summarize recent versus baseline result behavior."""
        data, error_payload = _analysis_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "trend_summary",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        payload = filtered_trend_summary_payload(
            dataset=dataset,
            data=data,
            result_column=result_column,
            status=data_cache.status_snapshot(),
            test_id=test_id,
            test_type=test_type,
            dut_type=dut_type,
            job=job,
            release=release,
            hosts=hosts,
            passed=passed,
            order_by=order_by,
            recent_count=recent_count,
            baseline_count=baseline_count,
        )
        return _serialize_analysis_tool_payload(
            "trend_summary",
            dataset,
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="find_regressions",
        tags={"fd.io", "public", "read", "analysis", "regressions"},
        description=(
            "Finds direction-aware recent-vs-baseline regressions for one "
            "CSIT result column."
        ),
    )
    def find_regressions(
            dataset: str,
            result_column: str,
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
        ) -> str:
        """Find recent-vs-baseline regressions in cached CSIT results."""
        data, error_payload = _analysis_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "find_regressions",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        payload = filtered_find_regressions_payload(
            dataset=dataset,
            data=data,
            result_column=result_column,
            result_metadata=result_metadata,
            status=data_cache.status_snapshot(),
            group_by=group_by,
            test_type=test_type,
            dut_type=dut_type,
            job=job,
            release=release,
            hosts=hosts,
            passed=passed,
            order_by=order_by,
            recent_count=recent_count,
            baseline_count=baseline_count,
            threshold_percent=threshold_percent,
            preferred_direction=preferred_direction,
            limit=limit,
        )
        return _serialize_analysis_tool_payload(
            "find_regressions",
            dataset,
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="find_anomalies",
        tags={"fd.io", "public", "read", "analysis", "anomalies"},
        description=(
            "Finds deterministic z-score anomalies for one CSIT result column."
        ),
    )
    def find_anomalies(
            dataset: str,
            result_column: str,
            group_by: str | None = None,
            test_type: str | None = None,
            dut_type: str | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            passed: bool | None = None,
            threshold: float = 2.0,
            limit: int = 20
        ) -> str:
        """Find z-score anomalies in cached CSIT results."""
        data, error_payload = _analysis_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "find_anomalies",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        payload = filtered_find_anomalies_payload(
            dataset=dataset,
            data=data,
            result_column=result_column,
            status=data_cache.status_snapshot(),
            group_by=group_by,
            test_type=test_type,
            dut_type=dut_type,
            job=job,
            release=release,
            hosts=hosts,
            passed=passed,
            threshold=threshold,
            limit=limit,
        )
        return _serialize_analysis_tool_payload(
            "find_anomalies",
            dataset,
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="top_failures",
        tags={"fd.io", "public", "read", "analysis", "failures"},
        description=(
            "Ranks CSIT groups by failed count and failure rate."
        ),
    )
    def top_failures(
            dataset: str,
            group_by: str = "test_id",
            test_type: str | None = None,
            dut_type: str | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            build: int | None = None,
            limit: int = 20
        ) -> str:
        """Return compact top failure groups from cached CSIT results."""
        data, error_payload = _analysis_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "top_failures",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        payload = filtered_top_failures_payload(
            dataset=dataset,
            data=data,
            status=data_cache.status_snapshot(),
            group_by=group_by,
            test_type=test_type,
            dut_type=dut_type,
            job=job,
            release=release,
            hosts=hosts,
            build=build,
            limit=limit,
        )
        return _serialize_analysis_tool_payload(
            "top_failures",
            dataset,
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="telemetry_metrics",
        tags={"fd.io", "public", "read", "telemetry", "metrics"},
        description=(
            "Returns paginated decoded OpenMetrics telemetry samples for a "
            "CSIT result dataset."
        ),
    )
    def telemetry_metrics(
            dataset: str,
            metric_name: str | None = None,
            label_key: str | None = None,
            test_type: str | None = None,
            dut_type: str | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            test_id: str | None = None,
            build: int | None = None,
            passed: bool | None = None,
            offset: int = 0,
            limit: int = DEFAULT_TELEMETRY_LIMIT
        ) -> str:
        """Return decoded OpenMetrics telemetry samples."""
        data, error_payload = _telemetry_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_data_tool_payload(
                "telemetry_metrics",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        response = telemetry_query_service.run_guarded_diagnostic(
            "telemetry_metrics",
            dataset,
            lambda: _serialize_data_tool_payload(
                "telemetry_metrics",
                dataset,
                telemetry_metrics_payload(
                    dataset=dataset,
                    data=data,
                    status=data_cache.status_snapshot(),
                    metric_name=metric_name,
                    label_key=label_key,
                    test_type=test_type,
                    dut_type=dut_type,
                    job=job,
                    release=release,
                    hosts=hosts,
                    test_id=test_id,
                    build=build,
                    passed=passed,
                    offset=offset,
                    limit=limit,
                ),
                data_cache=data_cache,
            ),
        )
        if isinstance(response, str):
            return response
        return _serialize_data_tool_payload(
            "telemetry_metrics",
            dataset,
            response,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="telemetry_metric_values",
        tags={"fd.io", "public", "read", "telemetry", "summary"},
        description=(
            "Summarizes decoded OpenMetrics telemetry values for one metric."
        ),
    )
    def telemetry_metric_values(
            dataset: str,
            metric_name: str,
            group_by: str = "metric_name",
            label_key: str | None = None,
            test_type: str | None = None,
            dut_type: str | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            test_id: str | None = None,
            build: int | None = None,
            passed: bool | None = None,
            limit: int = DEFAULT_ANALYSIS_LIMIT
        ) -> str:
        """Return grouped telemetry metric value summaries."""
        data, error_payload = _telemetry_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "telemetry_metric_values",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        response = telemetry_query_service.run_guarded_diagnostic(
            "telemetry_metric_values",
            dataset,
            lambda: _serialize_analysis_tool_payload(
                "telemetry_metric_values",
                dataset,
                telemetry_metric_values_payload(
                    dataset=dataset,
                    data=data,
                    status=data_cache.status_snapshot(),
                    metric_name=metric_name,
                    group_by=group_by,
                    label_key=label_key,
                    test_type=test_type,
                    dut_type=dut_type,
                    job=job,
                    release=release,
                    hosts=hosts,
                    test_id=test_id,
                    build=build,
                    passed=passed,
                    limit=limit,
                ),
                data_cache=data_cache,
            ),
        )
        if isinstance(response, str):
            return response
        return _serialize_analysis_tool_payload(
            "telemetry_metric_values",
            dataset,
            response,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="telemetry_trend_summary",
        tags={"fd.io", "public", "read", "telemetry", "trend"},
        description=(
            "Summarizes recent versus baseline OpenMetrics telemetry behavior."
        ),
    )
    def telemetry_trend_summary(
            dataset: str,
            metric_name: str,
            group_by: str = "metric_name",
            label_key: str | None = None,
            test_type: str | None = None,
            dut_type: str | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            test_id: str | None = None,
            passed: bool | None = None,
            order_by: str = "build",
            recent_count: int = 3,
            baseline_count: int = 3,
            limit: int = DEFAULT_ANALYSIS_LIMIT
        ) -> str:
        """Return compact telemetry trend summaries."""
        data, error_payload = _telemetry_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "telemetry_trend_summary",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        response = telemetry_query_service.run_guarded_diagnostic(
            "telemetry_trend_summary",
            dataset,
            lambda: _serialize_analysis_tool_payload(
                "telemetry_trend_summary",
                dataset,
                telemetry_trend_summary_payload(
                    dataset=dataset,
                    data=data,
                    status=data_cache.status_snapshot(),
                    metric_name=metric_name,
                    group_by=group_by,
                    label_key=label_key,
                    test_type=test_type,
                    dut_type=dut_type,
                    job=job,
                    release=release,
                    hosts=hosts,
                    test_id=test_id,
                    passed=passed,
                    order_by=order_by,
                    recent_count=recent_count,
                    baseline_count=baseline_count,
                    limit=limit,
                ),
                data_cache=data_cache,
            ),
        )
        if isinstance(response, str):
            return response
        return _serialize_analysis_tool_payload(
            "telemetry_trend_summary",
            dataset,
            response,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="telemetry_anomalies",
        tags={"fd.io", "public", "read", "telemetry", "anomalies"},
        description=(
            "Finds deterministic z-score anomalies in OpenMetrics telemetry."
        ),
    )
    def telemetry_anomalies(
            dataset: str,
            metric_name: str,
            group_by: str = "metric_name",
            label_key: str | None = None,
            test_type: str | None = None,
            dut_type: str | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            test_id: str | None = None,
            passed: bool | None = None,
            threshold: float = 2.0,
            limit: int = DEFAULT_ANALYSIS_LIMIT
        ) -> str:
        """Return compact telemetry anomaly records."""
        data, error_payload = _telemetry_data_or_error(dataset, data_cache)
        if error_payload is not None:
            return _serialize_analysis_tool_payload(
                "telemetry_anomalies",
                dataset,
                error_payload,
                data_cache=data_cache,
            )

        response = telemetry_query_service.run_guarded_diagnostic(
            "telemetry_anomalies",
            dataset,
            lambda: _serialize_analysis_tool_payload(
                "telemetry_anomalies",
                dataset,
                telemetry_anomalies_payload(
                    dataset=dataset,
                    data=data,
                    status=data_cache.status_snapshot(),
                    metric_name=metric_name,
                    group_by=group_by,
                    label_key=label_key,
                    test_type=test_type,
                    dut_type=dut_type,
                    job=job,
                    release=release,
                    hosts=hosts,
                    test_id=test_id,
                    passed=passed,
                    threshold=threshold,
                    limit=limit,
                ),
                data_cache=data_cache,
            ),
        )
        if isinstance(response, str):
            return response
        return _serialize_analysis_tool_payload(
            "telemetry_anomalies",
            dataset,
            response,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="telemetry_catalog",
        tags={"fd.io", "public", "read", "telemetry", "discovery"},
        description=(
            "Lists telemetry-capable Trending series from the compact source "
            "locator. Use this before one telemetry_timeseries call; it does "
            "not build JumpAvg analysis or decode telemetry."
        ),
    )
    def telemetry_catalog(
            dataset: str = "trending",
            dut: str | None = None,
            area: str | None = None,
            test: str | None = None,
            infra: str | None = None,
            testbed: str | None = None,
            framesize: str | None = None,
            cores: str | None = None,
            test_type: str | None = None,
            offset: int = 0,
            limit: int = DEFAULT_TELEMETRY_CATALOG_LIMIT,
        ) -> str:
        """Return telemetry-capable logical series without result analysis."""

        if str(dataset).strip().lower() != "trending":
            payload = validation_error_payload(
                [{
                    "field": "dataset",
                    "message": "telemetry_catalog currently supports trending.",
                    "value": dataset,
                }],
                {"dataset": dataset, "offset": offset, "limit": limit},
            )
        else:
            try:
                locator = data_cache.get_telemetry_locator("trending")
            except (AttributeError, DataCacheError) as err:
                if isinstance(err, DataCacheError):
                    payload = cache_error_payload(err, data_cache)
                else:
                    payload = {
                        "error": "data_unavailable",
                        "message": "Telemetry locator is unavailable.",
                        "data": data_cache.status_snapshot(),
                    }
            else:
                payload = telemetry_catalog_payload(
                    locator,
                    data_cache.status_snapshot(),
                    filters={
                        "dut": dut,
                        "area": area,
                        "test": test,
                        "infra": infra,
                        "testbed": testbed,
                        "framesize": framesize,
                        "cores": cores,
                        "test_type": test_type,
                    },
                    offset=offset,
                    limit=limit,
                )
        return _serialize_data_tool_payload(
            "telemetry_catalog", "trending", payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="telemetry_timeseries",
        tags={"fd.io", "public", "read", "telemetry", "timeseries"},
        description=(
            "Preferred bounded telemetry analysis tool. Decodes authoritative "
            "source rows from a lightweight locator for selected Trending "
            "series and a requested time window in one concurrency-controlled "
            "call. Use "
            "metric='cycles_per_packet' for VPP node evolution analysis; use "
            "telemetry_metrics only for sampled diagnostic previews. Raw "
            "telemetry is intentionally unavailable through generic result "
            "tools."
        ),
    )
    def telemetry_timeseries(
            dataset: str,
            series: list[str],
            metric: str,
            node_names: list[str] | None = None,
            testbed: str | None = None,
            days: int = 30,
            start_time: str | None = None,
            end_time: str | None = None,
            passed: bool = True,
            aggregation: str = "per_run",
            offset: int = 0,
            limit: int = DEFAULT_TIMESERIES_LIMIT,
        ) -> str:
        """Return complete targeted telemetry time-series points."""

        try:
            data = data_cache.get_parquet(query=dataset)
            get_raw_telemetry = getattr(data_cache, "get_raw_telemetry", None)
            get_locator = getattr(data_cache, "get_telemetry_locator", None)
            telemetry_source = (
                get_raw_telemetry(dataset)
                if get_raw_telemetry is not None else None
            )
            telemetry_locator = (
                get_locator(dataset)
                if get_locator is not None else None
            )
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "telemetry_timeseries", dataset, payload,
                data_cache=data_cache,
            )
        payload = query_admission.run(
            tool="telemetry_timeseries",
            dataset=dataset,
            row_count=len(data),
            callback=lambda: telemetry_query_service.timeseries_payload(
                data,
                data_cache.status_snapshot(),
                telemetry_source=telemetry_source,
                telemetry_locator=telemetry_locator,
                dataset=dataset,
                series=series,
                metric=metric,
                node_names=node_names,
                testbed=testbed,
                days=days,
                start_time=start_time,
                end_time=end_time,
                passed=passed,
                aggregation=aggregation,
                offset=offset,
                limit=limit,
            ),
        )
        return _serialize_data_tool_payload(
            "telemetry_timeseries", dataset, payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="trending_catalog",
        tags={"fd.io", "public", "read", "trending", "discovery"},
        description=(
            "Provides parsed CSIT trending test combinations and cascading "
            "filter options."
        ),
    )
    def trending_catalog(
            dut: str | None = None,
            area: str | None = None,
            test: str | None = None,
            infra: str | None = None,
            testbed: str | None = None,
            framesize: str | None = None,
            cores: str | None = None,
            test_type: str | None = None,
            select_defaults: bool = False,
            offset: int = 0,
            limit: int = DEFAULT_TRENDING_LIMIT,
        ) -> str:
        """Return compact logical-series metadata for trending filters."""

        try:
            data = data_cache.get_parquet(query="trending")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "trending_catalog",
                "trending",
                payload,
                data_cache=data_cache,
            )
        payload = trending_service.catalog_payload(
            data,
            data_cache.status_snapshot(),
            dut=dut,
            area=area,
            test=test,
            infra=infra,
            testbed=testbed,
            framesize=framesize,
            cores=cores,
            test_type=test_type,
            select_defaults=select_defaults,
            offset=offset,
            limit=limit,
        )
        return _serialize_data_tool_payload(
            "trending_catalog",
            "trending",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="trending_series",
        tags={"fd.io", "public", "read", "trending", "series"},
        description=(
            "Provides paginated semantic points for selected trending series."
        ),
    )
    def trending_series(
            series: list[str],
            offset: int = 0,
            limit: int = DEFAULT_TRENDING_LIMIT,
        ) -> str:
        """Return semantic throughput, bandwidth, and latency points."""

        try:
            data = data_cache.get_parquet(query="trending")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "trending_series",
                "trending",
                payload,
                data_cache=data_cache,
            )
        payload = trending_service.series_payload(
            data,
            data_cache.status_snapshot(),
            series=series,
            offset=offset,
            limit=limit,
        )
        return _serialize_data_tool_payload(
            "trending_series",
            "trending",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="trending",
        tags={"fd.io", "public", "read", "trending"},
        description=(
            "Provides filtered trending result data with response metadata. "
            "Raw telemetry is private; use telemetry_timeseries instead."
        ),
    )
    def trending(
            test_type: str | None = None,
            dut_type: str | None = None,
            passed: bool | None = None,
            job: str | None = None,
            hosts: str | list[str] | None = None,
            test_id: str | None = None,
            build: int | None = None,
            offset: int = 0,
            aggregation: str = "none",
            sort_by: str | None = None,
            sort_order: str = "desc",
            columns: list[str] | str | None = None,
            limit: int = DEFAULT_TOOL_LIMIT
        ) -> str:
        """Return filtered trending data from the cached parquet data."""
        try:
            data = data_cache.get_parquet(query="trending")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "trending",
                "trending",
                payload,
                data_cache=data_cache,
            )

        payload = query_admission.run(
            tool="trending",
            dataset="trending",
            row_count=len(data),
            callback=lambda: result_tool_payload(
                dataset="trending",
                data=data,
                data_cache=data_cache,
                text_filters=[
                    ("test_type", test_type),
                    ("dut_type", dut_type),
                    ("job", job),
                    ("hosts", hosts),
                    ("test_id", test_id),
                ],
                int_filters=[
                    ("build", build),
                ],
                passed=passed,
                limit=limit,
                offset=offset,
                aggregation=aggregation,
                sort_by=sort_by,
                sort_order=sort_order,
                columns=columns,
            ),
        )
        return _serialize_data_tool_payload(
            "trending",
            "trending",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="job_statistics",
        tags={"fd.io", "public", "read", "job", "statistics"},
        description=(
            "Provides filtered job duration statistics for CSIT tests with "
            "response metadata."
        ),
    )
    def job_statistics(
            days: int | None = None,
            job: str | None = None,
            limit: int = DEFAULT_TOOL_LIMIT,
            dut: str | None = None,
            test_type: str | None = None,
            cadence: str | None = None,
            testbed: str | None = None,
            select_defaults: bool = False,
        ) -> str:
        """Return filtered run duration and pass/fail statistics."""
        try:
            data = data_cache.get_parquet(query="statistics")
            trending_data = data_cache.get_parquet(query="trending")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "job_statistics",
                "statistics",
                payload,
                data_cache=data_cache,
            )

        payload = job_statistics_payload(
            data=data,
            trending_data=trending_data,
            data_cache=data_cache,
            days=days,
            job=job,
            limit=limit,
            dut=dut,
            test_type=test_type,
            cadence=cadence,
            testbed=testbed,
            select_defaults=select_defaults,
            enriched_data=statistics_service.enriched_data(
                data, trending_data, data_cache.status_snapshot()
            ),
        )
        return _serialize_data_tool_payload(
            "job_statistics",
            "statistics",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="iterative_catalog",
        tags={"fd.io", "public", "read", "iterative", "discovery"},
        description=(
            "Provides parsed CSIT iterative test combinations and cascading "
            "filter options."
        ),
    )
    def iterative_catalog(
            release: str | None = None,
            dut: str | None = None,
            dut_version: str | None = None,
            area: str | None = None,
            test: str | None = None,
            infra: str | None = None,
            testbed: str | None = None,
            framesize: str | None = None,
            cores: str | None = None,
            test_type: str | None = None,
            select_defaults: bool = False,
            offset: int = 0,
            limit: int = DEFAULT_ITERATIVE_LIMIT,
        ) -> str:
        """Return compact logical-series metadata for iterative filters."""

        try:
            data = data_cache.get_parquet(query="iterative")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "iterative_catalog",
                "iterative",
                payload,
                data_cache=data_cache,
            )
        payload = iterative_service.catalog_payload(
            data,
            data_cache.status_snapshot(),
            release=release,
            dut=dut,
            dut_version=dut_version,
            area=area,
            test=test,
            infra=infra,
            testbed=testbed,
            framesize=framesize,
            cores=cores,
            test_type=test_type,
            select_defaults=select_defaults,
            offset=offset,
            limit=limit,
        )
        return _serialize_data_tool_payload(
            "iterative_catalog",
            "iterative",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="iterative_series",
        tags={"fd.io", "public", "read", "iterative", "series"},
        description=(
            "Provides paginated semantic samples for selected iterative series."
        ),
    )
    def iterative_series(
            series: list[str],
            offset: int = 0,
            limit: int = DEFAULT_ITERATIVE_LIMIT,
        ) -> str:
        """Return semantic throughput, bandwidth, and latency samples."""

        try:
            data = data_cache.get_parquet(query="iterative")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "iterative_series",
                "iterative",
                payload,
                data_cache=data_cache,
            )
        payload = iterative_service.series_payload(
            data,
            data_cache.status_snapshot(),
            series=series,
            offset=offset,
            limit=limit,
        )
        return _serialize_data_tool_payload(
            "iterative_series",
            "iterative",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="iterative",
        tags={"fd.io", "public", "read", "iterative"},
        description=(
            "Provides filtered iterative CSIT test data with response metadata."
        ),
    )
    def iterative(
            test_type: str | None = None,
            dut_type: str | None = None,
            passed: bool | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            test_id: str | None = None,
            build: int | None = None,
            offset: int = 0,
            aggregation: str = "none",
            sort_by: str | None = None,
            sort_order: str = "desc",
            columns: list[str] | str | None = None,
            limit: int = DEFAULT_TOOL_LIMIT
        ) -> str:
        """Return filtered iterative CSIT test data from cached parquet data."""
        try:
            data = data_cache.get_parquet(query="iterative")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "iterative",
                "iterative",
                payload,
                data_cache=data_cache,
            )

        payload = query_admission.run(
            tool="iterative",
            dataset="iterative",
            row_count=len(data),
            callback=lambda: result_tool_payload(
                dataset="iterative",
                data=data,
                data_cache=data_cache,
                text_filters=[
                    ("test_type", test_type),
                    ("dut_type", dut_type),
                    ("job", job),
                    ("release", release),
                    ("hosts", hosts),
                    ("test_id", test_id),
                ],
                int_filters=[
                    ("build", build),
                ],
                passed=passed,
                limit=limit,
                offset=offset,
                aggregation=aggregation,
                sort_by=sort_by,
                sort_order=sort_order,
                columns=columns,
            ),
        )
        return _serialize_data_tool_payload(
            "iterative",
            "iterative",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="coverage_catalog",
        tags={"fd.io", "public", "read", "coverage", "discovery"},
        description=(
            "Provides parsed CSIT coverage dimensions and cascading filter "
            "options."
        ),
    )
    def coverage_catalog(
            release: str | None = None,
            dut: str | None = None,
            dut_version: str | None = None,
            area: str | None = None,
            infra: str | None = None,
        ) -> str:
        """Return compact Coverage filter metadata without selecting defaults."""

        try:
            data = data_cache.get_parquet(query="coverage")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "coverage_catalog",
                "coverage",
                payload,
                data_cache=data_cache,
            )
        payload = coverage_service.catalog_payload(
            data,
            data_cache.status_snapshot(),
            release=release,
            dut=dut,
            dut_version=dut_version,
            area=area,
            infra=infra,
        )
        return _serialize_data_tool_payload(
            "coverage_catalog",
            "coverage",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="coverage_tables",
        tags={"fd.io", "public", "read", "coverage", "tables"},
        description=(
            "Provides paginated CSIT coverage table rows for a complete "
            "filter selection."
        ),
    )
    def coverage_tables(
            release: str,
            dut: str,
            dut_version: str,
            area: str,
            infra: str,
            offset: int = 0,
            limit: int = DEFAULT_COVERAGE_LIMIT,
        ) -> str:
        """Return decoded throughput and latency rows for Coverage tables."""

        try:
            data = data_cache.get_parquet(query="coverage")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "coverage_tables",
                "coverage",
                payload,
                data_cache=data_cache,
            )
        payload = coverage_service.tables_payload(
            data,
            data_cache.status_snapshot(),
            release=release,
            dut=dut,
            dut_version=dut_version,
            area=area,
            infra=infra,
            offset=offset,
            limit=limit,
        )
        return _serialize_data_tool_payload(
            "coverage_tables",
            "coverage",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="coverage",
        tags={"fd.io", "public", "read", "coverage"},
        description=(
            "Provides filtered CSIT coverage data with response metadata."
        ),
    )
    def coverage(
            test_type: str | None = None,
            dut_type: str | None = None,
            passed: bool | None = None,
            job: str | None = None,
            release: str | None = None,
            hosts: str | list[str] | None = None,
            test_id: str | None = None,
            build: int | None = None,
            offset: int = 0,
            aggregation: str = "none",
            sort_by: str | None = None,
            sort_order: str = "desc",
            columns: list[str] | str | None = None,
            limit: int = DEFAULT_TOOL_LIMIT
        ) -> str:
        """Return filtered coverage CSIT test data from cached parquet data."""
        try:
            data = data_cache.get_parquet(query="coverage")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "coverage",
                "coverage",
                payload,
                data_cache=data_cache,
            )

        payload = query_admission.run(
            tool="coverage",
            dataset="coverage",
            row_count=len(data),
            callback=lambda: result_tool_payload(
                dataset="coverage",
                data=data,
                data_cache=data_cache,
                text_filters=[
                    ("test_type", test_type),
                    ("dut_type", dut_type),
                    ("job", job),
                    ("release", release),
                    ("hosts", hosts),
                    ("test_id", test_id),
                ],
                int_filters=[
                    ("build", build),
                ],
                passed=passed,
                limit=limit,
                offset=offset,
                aggregation=aggregation,
                sort_by=sort_by,
                sort_order=sort_order,
                columns=columns,
            ),
        )
        return _serialize_data_tool_payload(
            "coverage",
            "coverage",
            payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="comparison_catalog",
        tags={"fd.io", "public", "read", "comparison", "discovery"},
        description=(
            "Provides Iterative reference filters and meaningful comparison "
            "parameter values."
        ),
    )
    def comparison_catalog(
            release: str | None = None,
            dut: str | None = None,
            dut_version: str | None = None,
            infra: str | None = None,
            framesize: str | None = None,
            cores: str | None = None,
            test_type: str | None = None,
            parameter: str | None = None,
            value: str | None = None,
        ) -> str:
        """Return cascading filters for Iterative comparisons."""

        try:
            data = data_cache.get_parquet(query="iterative")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "comparison_catalog", "iterative", payload,
                data_cache=data_cache,
            )
        payload = comparison_service.catalog_payload(
            data,
            data_cache.status_snapshot(),
            release=release,
            dut=dut,
            dut_version=dut_version,
            infra=infra,
            framesize=framesize,
            cores=cores,
            test_type=test_type,
            parameter=parameter,
            value=value,
        )
        return _serialize_data_tool_payload(
            "comparison_catalog", "iterative", payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="comparison_table",
        tags={"fd.io", "public", "read", "comparison", "table"},
        description="Provides paginated Iterative comparison summary rows.",
    )
    def comparison_table(
            release: str,
            dut: str,
            dut_version: str,
            infra: str,
            framesize: str,
            cores: str,
            test_type: str,
            parameter: str,
            value: str,
            remove_extreme_outliers: bool = False,
            offset: int = 0,
            limit: int = DEFAULT_COMPARISON_LIMIT,
        ) -> str:
        """Return mean, stdev, and relative-change comparison rows."""

        try:
            data = data_cache.get_parquet(query="iterative")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "comparison_table", "iterative", payload,
                data_cache=data_cache,
            )
        payload = comparison_service.table_payload(
            data,
            data_cache.status_snapshot(),
            release=release,
            dut=dut,
            dut_version=dut_version,
            infra=infra,
            framesize=framesize,
            cores=cores,
            test_type=test_type,
            parameter=parameter,
            value=value,
            remove_extreme_outliers=remove_extreme_outliers,
            offset=offset,
            limit=limit,
        )
        return _serialize_data_tool_payload(
            "comparison_table", "iterative", payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        annotations=READ_ONLY_ANNOTATIONS,
        name="comparison_data",
        tags={"fd.io", "public", "read", "comparison", "data"},
        description="Provides paginated raw Iterative rows for a comparison.",
    )
    def comparison_data(
            release: str,
            dut: str,
            dut_version: str,
            infra: str,
            framesize: str,
            cores: str,
            test_type: str,
            parameter: str,
            value: str,
            offset: int = 0,
            limit: int = DEFAULT_COMPARISON_LIMIT,
        ) -> str:
        """Return matching reference and compared source records."""

        try:
            data = data_cache.get_parquet(query="iterative")
        except DataCacheError as err:
            payload = cache_error_payload(err, data_cache)
            return _serialize_data_tool_payload(
                "comparison_data", "iterative", payload,
                data_cache=data_cache,
            )
        payload = comparison_service.data_payload(
            data,
            data_cache.status_snapshot(),
            release=release,
            dut=dut,
            dut_version=dut_version,
            infra=infra,
            framesize=framesize,
            cores=cores,
            test_type=test_type,
            parameter=parameter,
            value=value,
            offset=offset,
            limit=limit,
        )
        return _serialize_data_tool_payload(
            "comparison_data", "iterative", payload,
            data_cache=data_cache,
        )

    @mcp.tool(
        app=True,
        annotations=READ_ONLY_ANNOTATIONS,
        name="dashboard",
        tags={"fd.io", "public", "read", "ui", "dashboard"},
        description="Provides the overall dashboard for CSIT data.",
    )
    def dashboard() -> PrefabApp:
        """Build and render the dashboard view for CSIT parquet data."""
        try:
            statistics = data_cache.get_parquet("statistics")
        except DataCacheError as err:
            return build_status_page(cache_error_payload(err, data_cache))

        return build_dashboard(statistics)


def _serialize_data_tool_payload(
        tool_name: str,
        dataset: str,
        payload: dict,
        *,
        data_cache: DataCacheService
    ) -> str:
    _log_data_tool_payload(
        tool_name,
        dataset,
        payload,
        status_snapshot=data_cache.status_snapshot(),
    )
    return safe_json_dumps(payload)


def _serialize_analysis_tool_payload(
        tool_name: str,
        dataset: str,
        payload: dict,
        *,
        data_cache: DataCacheService
    ) -> str:
    _log_analysis_tool_payload(
        tool_name,
        dataset,
        payload,
        status_snapshot=data_cache.status_snapshot(),
    )
    return safe_json_dumps(payload)


def _serialize_discovery_payload(
        tool_name: str,
        payload: dict,
        *,
        data_cache: DataCacheService,
        dataset: str | None = None,
        column: str | None = None,
        limit: int | None = None
    ) -> str:
    _log_discovery_payload(
        tool_name,
        payload,
        dataset=dataset,
        column=column,
        limit=limit,
        status_snapshot=data_cache.status_snapshot(),
    )
    return safe_json_dumps(payload)


def _serialize_resource_payload(
        resource: str,
        query: str,
        payload: dict,
        *,
        data_cache: DataCacheService,
        suggestions: list[str] | None = None
    ) -> str:
    _log_resource_payload(
        resource,
        query,
        payload,
        status_snapshot=data_cache.status_snapshot(),
    )
    return safe_json_dumps(payload, suggestions=suggestions)


def _analysis_data_or_error(
        dataset: str,
        data_cache: DataCacheService
    ) -> tuple[pd.DataFrame | None, dict | None]:
    dataset_error = validate_analysis_dataset(dataset)
    if dataset_error is not None:
        return None, dataset_error
    try:
        return data_cache.get_parquet(query=dataset), None
    except DataCacheError as err:
        return None, cache_error_payload(err, data_cache)


def _telemetry_data_or_error(
        dataset: str,
        data_cache: DataCacheService
    ) -> tuple[pd.DataFrame | None, dict | None]:
    if dataset not in TELEMETRY_DATASETS:
        return None, validation_error_payload(
            [{
                "field": "dataset",
                "message": (
                    "dataset must be one of: " +
                    ", ".join(TELEMETRY_DATASETS)
                ),
                "value": dataset,
            }],
            {"dataset": dataset},
        )
    try:
        data_cache.get_parquet(query=dataset)
        telemetry_data = data_cache.get_telemetry(dataset)
    except DataCacheError as err:
        return None, cache_error_payload(err, data_cache)

    telemetry_info = (
        data_cache.status_snapshot().get("telemetry", {}).get(dataset, {})
    )
    if not telemetry_info.get("available") and telemetry_data.empty:
        return None, validation_error_payload(
            [{
                "field": "dataset",
                "message": (
                    f"dataset '{dataset}' has no telemetry available in the "
                    "private source sidecar."
                ),
                "value": dataset,
            }],
            {"dataset": dataset},
        )
    return telemetry_data, None


def _log_data_tool_payload(
        tool_name: str,
        dataset: str,
        payload: dict,
        *,
        status_snapshot: dict
    ) -> None:
    filters = payload.get("filters", {})
    status = payload.get("data", status_snapshot)
    log_event(
        "mcp_data_tool_completed",
        tool=tool_name,
        dataset=payload.get("dataset", dataset),
        error=payload.get("error"),
        aggregation=payload.get("aggregation") or filters.get("aggregation"),
        limit=payload.get("limit") or filters.get("limit"),
        offset=(
            payload.get("offset")
            if "offset" in payload
            else filters.get("offset")
        ),
        total_row_count=payload.get("total_row_count"),
        row_count=payload.get("row_count"),
        returned_count=payload.get("returned_count"),
        has_more=payload.get("has_more"),
        data_status=payload.get("data_status") or status.get("status"),
        cache_age_seconds=status.get("cache_age_seconds"),
    )


def _log_analysis_tool_payload(
        tool_name: str,
        dataset: str,
        payload: dict,
        *,
        status_snapshot: dict
    ) -> None:
    status = payload.get("data", status_snapshot)
    records = payload.get("records")
    log_event(
        "mcp_analysis_tool_completed",
        tool=tool_name,
        analysis=payload.get("analysis"),
        dataset=payload.get("dataset", dataset),
        error=payload.get("error"),
        result_column=payload.get("result_column"),
        group_by=payload.get("group_by"),
        row_count=payload.get("row_count"),
        returned_count=(
            len(records)
            if isinstance(records, list)
            else None
        ),
        data_status=payload.get("data_status") or status.get("status"),
        cache_age_seconds=status.get("cache_age_seconds"),
    )


def _log_discovery_payload(
        tool_name: str,
        payload: dict,
        *,
        dataset: str | None,
        column: str | None,
        limit: int | None,
        status_snapshot: dict
    ) -> None:
    status = payload.get("data", status_snapshot)
    log_event(
        "mcp_discovery_tool_completed",
        tool=tool_name,
        dataset=payload.get("dataset", dataset),
        column=payload.get("column", column),
        limit=payload.get("limit", limit),
        error=payload.get("error"),
        returned_count=_discovery_returned_count(payload),
        ready=payload.get("ready"),
        data_status=status.get("status"),
        cache_age_seconds=status.get("cache_age_seconds"),
    )


def _log_resource_payload(
        resource: str,
        query: str,
        payload: dict,
        *,
        status_snapshot: dict
    ) -> None:
    status = payload.get("data", status_snapshot)
    log_event(
        "mcp_resource_completed",
        resource=resource,
        query=payload.get("query", query),
        error=payload.get("error"),
        total_row_count=payload.get("total_row_count"),
        row_count=payload.get("row_count"),
        returned_count=payload.get("returned_count"),
        has_more=payload.get("has_more"),
        truncated=payload.get("truncated"),
        datasets=_dataset_summaries(payload),
        data_status=status.get("status"),
        cache_age_seconds=status.get("cache_age_seconds"),
    )


def _discovery_returned_count(payload: dict) -> int | None:
    for key in ("returned_count", "entry_count"):
        if key in payload:
            return payload[key]
    for key in ("datasets", "columns", "values", "schemas"):
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)
    return None


def _dataset_summaries(payload: dict) -> dict | None:
    datasets = payload.get("datasets")
    if not isinstance(datasets, dict):
        return None
    return {
        name: {
            key: value
            for key, value in details.items()
            if key in (
                "total_row_count",
                "row_count",
                "returned_count",
                "has_more",
                "truncated",
            )
        }
        for name, details in datasets.items()
        if isinstance(details, dict)
    }
