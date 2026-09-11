# Testing

Both projects use standard-library `unittest`. Tests use fake readers, dataframes,
and fake MCP clients; routine test runs do not need S3.

## Server

Run from `mcp-server/`:

```sh
uv run --locked python -m unittest discover
uv run --locked python -c "import server; assert server.app"
```

| Test area | Files |
| --- | --- |
| Settings, lifecycle, cache | `test_settings.py`, `test_lifecycle.py`, `test_data_cache.py` |
| Memory accounting and compact indexes | `test_memory_service.py` |
| Discovery and result metadata | `test_discovery_service.py`, `test_result_metadata_service.py` |
| Generic query/admission/analysis/serialization | `test_query_service.py`, `test_query_guard.py`, `test_analysis_service.py`, `test_serialization_service.py` |
| Telemetry | `test_telemetry_service.py` |
| Authoritative telemetry locator, byte budgets, concurrency, and process isolation | `test_telemetry_query_service.py`, `test_telemetry_worker.py` |
| Statistics | `test_statistics_service.py` |
| Trending and JumpAvg | `test_trending_service.py`, `test_trending_analysis.py` |
| Iterative | `test_iterative_service.py` |
| Coverage and HDR Histogram | `test_coverage_service.py` |
| Comparison | `test_comparison_service.py` |
| MCP contracts | `test_mcp_registration.py` |
| Legacy Prefab UI | `test_ui_dashboard.py` |

Server tests cover fixture loading, required-first staged publication, cache
transitions, refresh preservation,
structured events, validation and unavailable-data paths, pagination/payload
guards, tool signatures, resource visibility, and the 29-tool capability count.
Telemetry coverage includes standard and CSIT label dialects, production
`DUT1/mrr` semantic selection, direct/runtime source preference, active-state
fallback, thread identity, and stage-specific empty-result diagnostics.

Run the repeatable fixture benchmark from `mcp-server/`:

```sh
uv run --locked python scripts/memory_benchmark.py --mode fixture --days 60
```

For representative retained data, use `--mode s3 --days 60` and repeat with
`--days 150`. Output contains startup, loaded-cache, and warm-index checkpoints
with elapsed time, RSS, cgroup state, dataframe components, and derived indexes.

## Client

Run from `mcp-client/`:

```sh
uv run --locked python -m unittest discover
```

| Test area | Files |
| --- | --- |
| MCP state, routes, Statistics | `test_app.py`, `test_dashboard.py` |
| Statistics export | `test_statistics_export.py` |
| Trending UI/export | `test_trending_dashboard.py`, `test_trending_export.py` |
| Iterative UI/export | `test_iterative_dashboard.py`, `test_iterative_export.py` |
| Coverage UI/export | `test_coverage_dashboard.py`, `test_coverage_export.py` |
| Comparison orchestration/UI/export | `test_comparison_app.py`, `test_comparison_dashboard.py`, `test_comparison_export.py` |

Fake MCP clients exercise startup failure, lazy reconnect, metadata retention,
dashboard tool arguments, pagination, canonical redirects, inline errors,
HTTP 503 pages, binary export responses, and shutdown cleanup.

## Targeted Syntax Checks

```sh
cd mcp-server
uv run --locked python -m py_compile \
  dashboard/mcp_tools.py dashboard/services/*.py

cd ../mcp-client
uv run --locked python -m py_compile \
  app.py dashboard.py *_dashboard.py *_export.py
```

## Compose And Documentation Checks

```sh
docker compose config
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml config
xmllint --noout doc/diagrams/*.drawio doc/diagrams/*.svg \
  doc/code/diagrams/*.drawio doc/code/diagrams/*.svg
git diff --check
```

## Confirmed Test Boundaries

- There is no browser automation suite; HTML/SVG/JavaScript behavior is tested
  through rendered markup and asset assertions.
- Routine tests mock S3; they do not validate live credentials, network access,
  or current production parquet contents.
- Docker build and end-to-end Compose smoke checks are manual commands.
- The repository contains no CI workflow, so these commands are not enforced by
  a checked-in pipeline.
