# CSIT MCP

CSIT MCP is a two-service Python stack for exposing FD.io CSIT data through a FastMCP server and rendering a lightweight browser data explorer through a Starlette client.

The current project provides:

- a FastAPI + FastMCP server on port `8000`
- a Starlette browser explorer client on port `7860`
- S3 parquet loading for production-like use
- fixture JSON loading for no-AWS local development
- lifecycle-managed in-memory Pandas cache with readiness, refresh, normalization, and history metadata
- read-only MCP discovery, data, and analysis tools for Codex and other MCP clients
- semantic metadata for configured CSIT `result_*` columns
- decoded OpenMetrics telemetry samples from parquet `telemetry` columns
- JSON-safe payloads, pagination metadata, response-size guardrails, and capped private previews
- structured operational JSON logs for refreshes, MCP calls, and payload guardrails
- a dependency-free browser explorer with filters, tables, SVG charts, analysis panels, and graceful MCP error handling
- Docker Compose packaging with non-root runtime identity and lockfile-based builds

## Architecture

![CSIT MCP architecture](doc/diagrams/architecture.svg)

| Service | Location | Runtime | Port | Purpose |
| --- | --- | --- | --- | --- |
| `mcp-server` | `mcp-server/` | FastAPI + FastMCP | `8000` | Loads CSIT data, exposes MCP at `/mcp`, and serves liveness, readiness, and refresh HTTP routes. |
| `mcp-client` | `mcp-client/` | Starlette + FastMCP client | `7860` | Connects to the MCP server and renders an exploratory browser UI from discovery, data, and analysis tools. |

The server is assembled in `mcp-server/dashboard/__init__.py`. The assembly layer stays thin: settings, lifecycle, cache ownership, MCP handlers, query behavior, serialization, routes, and UI construction live in focused modules. The client is assembled in `mcp-client/app.py`; it owns MCP connection state, lazy reconnect, health reporting, and server-rendered explorer HTML.

Docker Compose uses an external network named `mcp`. Inside the network, the client connects to `http://mcp-server:8000/mcp`. From the host, use `http://localhost:7860` for the browser explorer and `http://localhost:8000/mcp` for MCP clients such as Codex.

## MCP Surface

The FastMCP server name is `csit_mcp`. FastAPI mounts the FastMCP HTTP app, and FastMCP serves MCP at `/mcp`.

| Type | Name or URI | Visibility | Behavior |
| --- | --- | --- | --- |
| Tool | `datasets` | Public | Lists datasets, cache status, row counts, freshness, and configured partitions. |
| Tool | `columns` | Public | Lists configured/cached column metadata and semantic result metadata for one dataset. |
| Tool | `values` | Public | Lists common values for one cached dataset column. |
| Tool | `schema` | Public | Returns configured schema, partition, release, path, and result-column metadata. |
| Tool | `compare_hosts` | Public | Compares one result column across host groups. |
| Tool | `trend_summary` | Public | Summarizes recent versus baseline behavior for one result column. |
| Tool | `find_regressions` | Public | Finds direction-aware recent-vs-baseline regressions. |
| Tool | `find_anomalies` | Public | Finds deterministic z-score anomalies. |
| Tool | `top_failures` | Public | Ranks groups by failed count and failure rate. |
| Tool | `telemetry_metrics` | Public | Returns paginated decoded OpenMetrics telemetry samples. |
| Tool | `telemetry_metric_values` | Public | Summarizes telemetry metric values by a selected group. |
| Tool | `telemetry_trend_summary` | Public | Compares recent telemetry metric values against a baseline window. |
| Tool | `telemetry_anomalies` | Public | Finds deterministic telemetry metric anomalies. |
| Tool | `job_statistics` | Public | Returns structured JSON for cached `statistics` data. |
| Tool | `trending` | Public | Returns structured JSON for cached `trending` data. |
| Tool | `iterative` | Public | Returns structured JSON for cached `iterative` data. |
| Tool | `coverage` | Public | Returns structured JSON for cached `coverage` data. |
| Tool | `dashboard` | Public | Returns a Prefab UI HTML dashboard with a searchable statistics table. |
| Resource | `server://info` | Public | Returns server metadata, exposed endpoints, public/private resource lists, and data cache status. |
| Resource | `data://parquet/{query}` | Private/internal | Returns capped JSON previews for one cached dataset or all cached datasets. |
| Route | `GET /health` | HTTP | Process liveness: `{"status": "healthy", "service": "mcp-server"}`. |
| Route | `GET /ready` | HTTP | Data readiness. Returns `200` when ready or degraded-but-servable, otherwise `503`. |
| Route | `POST /data/refresh` | HTTP | Starts a manual background reload. Returns `202` when started, `409` when already loading. |

`server://info` keeps the compatibility field `endpoints.resources == ["server://info"]`. It also exposes `endpoints.public_resources == ["server://info"]` and `endpoints.private_resources == ["data://parquet/{query}"]`.

### Discovery Tools

Use discovery tools before broad data queries. They let Codex inspect the available data surface without requesting large row sets.

| Tool | Arguments | Readiness requirement |
| --- | --- | --- |
| `datasets()` | none | Does not require data readiness. |
| `columns(dataset)` | `dataset` | Works before readiness with config-only and result-column metadata; adds dtype/null/list metadata when data is ready. |
| `values(dataset, column, limit=100)` | `dataset`, `column`, `limit` | Requires cached data readiness. |
| `schema(dataset)` | `dataset` | Does not require data readiness. |

### Data Tools

`trending`, `iterative`, and `coverage` share one query contract.

| Argument | Applies to | Notes |
| --- | --- | --- |
| `test_type`, `dut_type`, `job`, `hosts`, `test_id` | `trending`, `iterative`, `coverage` | Exact-match filters. `hosts` accepts a string or list and supports list-valued source cells. |
| `release` | `iterative`, `coverage` | Exact-match filter. Current configured release is `rls2606`. |
| `build` | `trending`, `iterative`, `coverage` | Integer match. |
| `passed` | `trending`, `iterative`, `coverage` | Boolean-compatible values are accepted. |
| `limit` | all data tools | Defaults to `1000`; valid range is `1..10000`. |
| `offset` | `trending`, `iterative`, `coverage` | Zero-based pagination offset. |
| `aggregation` | `trending`, `iterative`, `coverage` | `none`, `hosts`, `test_id`, or `hosts_by_test_id`. |
| `sort_by`, `sort_order`, `columns` | `trending`, `iterative`, `coverage` | Optional sorting and returned-column projection. |

`job_statistics(days=None, job=None, limit=1000)` supports `days`, `job`, and `limit`.

Successful data-tool responses are JSON strings with a stable envelope:

```json
{
  "schema_version": 1,
  "dataset": "iterative",
  "total_row_count": 5000,
  "row_count": 250,
  "returned_count": 100,
  "limit": 100,
  "offset": 0,
  "aggregation": "hosts_by_test_id",
  "has_more": true,
  "next_offset": 100,
  "freshness": "2026-06-05T09:30:00+00:00",
  "data_status": "ready",
  "filters": {},
  "columns": [],
  "records": []
}
```

Invalid arguments return `validation_error` with field-level details. If data is not ready, tools return `data_unavailable`. Oversized responses return `response_too_large` with suggestions to reduce `limit`, use `offset`, add filters, select `columns`, or use `aggregation`.

The private `data://parquet/{query}` resource is for internal inspection only. It remains registered for compatibility, but it is preview-only and listed under `endpoints.private_resources`. Prefer public discovery, analysis, and data tools for Codex and user-facing queries.

### Analysis Tools

Analysis tools return compact summaries for humans, Codex, and the browser explorer. They operate on `trending`, `iterative`, and `coverage`; unsupported datasets return `validation_error`.

| Tool | Main arguments | Output |
| --- | --- | --- |
| `compare_hosts` | `dataset`, `result_column`, optional test/build filters | Host-group statistics, best/worst host, and deltas. |
| `trend_summary` | `dataset`, `result_column`, optional filters, `order_by`, `recent_count`, `baseline_count` | Recent and baseline summaries with direction and deltas. |
| `find_regressions` | `dataset`, `result_column`, `group_by`, optional filters, window sizes, threshold | Groups whose recent window worsened against baseline. |
| `find_anomalies` | `dataset`, `result_column`, optional `group_by`, filters, threshold, limit | Z-score anomaly records with expected/actual values. |
| `top_failures` | `dataset`, `group_by`, optional filters, limit | Groups ranked by failed count and failure rate. |

Analysis responses use the same JSON string convention as data tools, but they return summaries rather than raw row pages:

```json
{
  "schema_version": 1,
  "analysis": "compare_hosts",
  "dataset": "iterative",
  "filters": {},
  "result_column": "result_receive_rate_rate_avg",
  "group_by": "hosts",
  "row_count": 250,
  "freshness": "2026-06-05T09:30:00+00:00",
  "data_status": "ready",
  "summary": {},
  "records": [],
  "explanation": "Compared result_receive_rate_rate_avg by hosts."
}
```

### Telemetry Tools

Telemetry tools operate on decoded OpenMetrics samples embedded in result dataset rows. After normalized result data is published, the server decodes a bounded, representative set of base64 + zlib parquet `telemetry` cells and parses them into a long-form metric index. Result readiness does not wait for this optional indexing step.

| Tool | Main arguments | Output |
| --- | --- | --- |
| `telemetry_metrics` | `dataset`, optional `metric_name`, `label_key`, result filters, `offset`, `limit` | Paginated metric samples with source row context. |
| `telemetry_metric_values` | `dataset`, `metric_name`, `group_by`, optional filters, `limit` | Grouped min/mean/max/percentile summaries for metric values. |
| `telemetry_trend_summary` | `dataset`, `metric_name`, `group_by`, filters, `order_by`, window sizes, `limit` | Recent-vs-baseline telemetry summaries. |
| `telemetry_anomalies` | `dataset`, `metric_name`, `group_by`, filters, `threshold`, `limit` | Z-score anomaly records for telemetry metric values. |

Telemetry samples include source context such as `job`, `build`, `start_time`, `test_type`, `dut_type`, `dut_version`, `tg_type`, `hosts`, `test_id`, `release`, and `passed`, plus `metric_name`, `labels`, `label_key`, `value`, `timestamp`, `type`, `unit`, and `help`. Datasets without a telemetry column return `validation_error`.

## Data

![CSIT MCP data flow](doc/diagrams/data-flow.svg)

The server caches four datasets:

| Cached dataset | Required for readiness | Source |
| --- | --- | --- |
| `statistics` | Yes | `stats_type=sra` from `s3://csit-docs-s3-cloudfront-index/csit/parquet/stats` |
| `trending` | Yes | `test_type=mrr`, `ndrpdr`, `hoststack`, `soak` from `s3://csit-docs-s3-cloudfront-index/csit/parquet/trending` |
| `iterative` | No | `release=rls2606`, multiple `test_type` partitions from `s3://csit-docs-s3-cloudfront-index/csit/parquet/iterative_rls2606` |
| `coverage` | No | `release=rls2606`, `test_type=ndrpdr` from `s3://csit-docs-s3-cloudfront-index/csit/parquet/coverage_rls2606` |

### Data Loading Lifecycle

Importing `server.app` does not read S3. During FastMCP lifespan startup, `dashboard/services/lifecycle.py` starts an initial background refresh on `DataCacheService`. If `CSIT_REFRESH_INTERVAL_SECONDS` is greater than `0`, the same lifespan starts an opt-in scheduled refresh loop.

`DataCacheService`:

- initializes empty cache slots for `statistics`, `trending`, `iterative`, and `coverage`
- caps `CSIT_TIME_PERIOD` at `CSIT_MAX_TIME_PERIOD`
- reads S3 parquet through `dashboard/data/data.py` or fixture JSON through `dashboard/data/fixture_data.py`
- normalizes loaded dataframes once before publishing them to the cache
- publishes required normalized result data before optional telemetry indexing
- tracks `starting`, `loading`, `ready`, `degraded`, and `failed`
- records freshness, cache age, load duration, row counts, dataset metadata, last error, and the source of the last refresh
- keeps the 10 most recent completed refresh attempts in memory
- treats `statistics` and `trending` as required for readiness
- preserves the previous successful cache when a later refresh fails

### Data Flow

The S3 data reader uses `mcp-server/dashboard/data/data.yaml` to select paths, partition keys, partition values, schemas, and columns. Fixture mode reads small JSON record files from `mcp-server/dashboard/data/fixtures/`.

`mcp-server/dashboard/data/result_metadata.yaml` adds static semantic metadata for configured `result_*` columns. Discovery payloads use it to expose display names, units or unit columns, scale, preferred direction, descriptions, and comparable dimensions such as `hosts`, `test_id`, `build`, `release`, `job`, `dut_type`, `dut_version`, `tg_type`, `passed`, and `start_time`.

After each successful read, cache-boundary normalization:

- converts `start_time` values to UTC ISO strings
- coerces `build` to nullable integers
- coerces `passed` to nullable booleans
- coerces text filter columns such as `test_id`, `job`, `release`, `dut_type`, and `test_type`
- coerces numeric `result_*` columns
- preserves list-valued `hosts` as Python lists in raw records
- starts a bounded telemetry index after normalized result data is ready
- decodes representative parquet `telemetry` cells from base64 + zlib OpenMetrics text
- publishes long-form telemetry metric samples separately from result rows
- adds row metadata fields `telemetry_metric_count`, `telemetry_decode_error`, and `telemetry_parse_error`

Telemetry parsing is dependency-free and supports canonical quoted OpenMetrics labels plus the unquoted label-value dialect emitted by CSIT telemetry, numeric values, optional timestamps, `# HELP`, `# TYPE`, `# UNIT`, comments, and `# EOF`. Decode and parse errors are recorded separately and do not fail readiness. The telemetry status for each source dataset reports `indexing`, `ready`, `partial`, `empty`, `not_available`, or `failed`, plus source/indexed row counts, sample counts, separate decode/parse error counts, limits, truncation, and errors. Structured `data_cache_published`, `telemetry_index_started`, and `telemetry_index_completed` events make this two-phase startup visible in logs.

Readiness, refresh, cache-error, and `server://info` payloads include status metadata: `ready`, `last_success_at`, `cache_age_seconds`, `row_counts`, `datasets`, `telemetry`, `configuration`, `last_refresh_started_by`, and `refresh_history`.

## Configuration

### Server Environment

Server runtime settings use `CSIT_*` environment variables.

| Variable | Default | Compose value | Meaning |
| --- | --- | --- | --- |
| `CSIT_DATA_MODE` | `s3` | unset | Data source mode: `s3` or `fixture`. |
| `CSIT_TIME_PERIOD` | `200` | `25` | Positive integer number of days back to read, capped at `CSIT_MAX_TIME_PERIOD`. |
| `CSIT_REFRESH_INTERVAL_SECONDS` | `0` | unset | Scheduled refresh interval. `0` or negative disables scheduled refresh. |
| `CSIT_CORS_ALLOW_ORIGINS` | `*` | unset | Browser CORS allowlist: `*` or comma-separated exact `http://` / `https://` origins. |
| `CSIT_TELEMETRY_MAX_SOURCE_ROWS` | `500` | unset | Positive integer maximum representative source rows indexed per dataset. |
| `CSIT_TELEMETRY_MAX_SAMPLES` | `100000` | unset | Positive integer maximum long-form metric samples indexed per dataset. |
| `CSIT_START_TRENDING` | `True` | `True` | Startup availability logging flag for trending data. |
| `CSIT_START_REPORT` | `True` | `False` | Startup availability logging flag for iterative/report data. |
| `CSIT_START_COVERAGE` | `True` | `True` | Startup availability logging flag for coverage data. |
| `CSIT_START_STATISTICS` | `True` | `True` | Startup availability logging flag for statistics data. |
| `CSIT_START_FAILURES` | `True` | `True` | Startup availability logging flag for failure/anomaly views. |
| `CSIT_AWS_ENDPOINT_URL` | empty | unset | Optional custom S3-compatible endpoint URL. |
| `CSIT_MAX_POOL_SIZE` | `30` | unset | Positive integer botocore maximum connection pool size. |
| `HOME` | image default | `/home/csit-mcp` | Writable container home for host UID/GID runtime execution. |
| `UV_CACHE_DIR` | image default | `/tmp/uv-runtime-cache` | Clean writable runtime uv cache, separate from the image build cache. |
| `AWS_SHARED_CREDENTIALS_FILE` | unset | `/home/csit-mcp/.aws/credentials` | Explicit AWS credentials path inside the server container. |
| `AWS_CONFIG_FILE` | unset | `/home/csit-mcp/.aws/config` | Explicit AWS config path inside the server container. |

The server validates documented `CSIT_*` settings at startup. Invalid configuration does not crash import or `/health`; the data cache marks loading as `failed`, `/ready` returns HTTP 503, and status payloads expose `data.configuration.valid == false` with field-level errors and effective fallback values.

The default `CSIT_CORS_ALLOW_ORIGINS=*` preserves trusted-local MCP and browser behavior. If the server is exposed beyond localhost or a private developer network, set exact browser origins, for example:

```sh
CSIT_CORS_ALLOW_ORIGINS=http://localhost:7860,https://csit.example
```

CORS is browser access control, not authentication. Do not expose the MCP server to untrusted networks without a separate access-control layer.

### Client Environment

| Variable | Default | Compose value | Meaning |
| --- | --- | --- | --- |
| `MCP_SERVER_URL` | `http://mcp-server:8000` | `http://mcp-server:8000` | Base URL of the MCP server. |
| `MCP_PATH` | `/mcp` | `/mcp` | MCP HTTP path mounted by the server. |
| `HOME` | image default | `/home/csit-mcp` | Writable container home for host UID/GID runtime execution. |
| `UV_CACHE_DIR` | image default | `/tmp/uv-runtime-cache` | Clean writable runtime uv cache, separate from the image build cache. |

### Scenarios

Use the base Compose file for S3-backed operation:

```sh
docker network create mcp
docker compose up --build
```

Use fixture mode for no-AWS local startup:

```sh
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml up --build
```

Enable scheduled refreshes by setting `CSIT_REFRESH_INTERVAL_SECONDS` on `mcp-server`, for example `3600` for roughly hourly refreshes after startup.

## Server

The server entrypoint is `mcp-server/server.py`. It creates `FastAPI(title="CSIT FastAPI server", lifespan=mcp_app.lifespan)`, adds CORS middleware from `CSIT_CORS_ALLOW_ORIGINS`, and mounts the FastMCP HTTP app. FastMCP serves MCP at `settings.mcp_path`, currently `/mcp`.

Important modules:

| Module | Responsibility |
| --- | --- |
| `dashboard/__init__.py` | Assembles logging, FastMCP, middleware, services, handlers, routes, and `mcp_app`. |
| `dashboard/settings.py` | Resolves and validates `AppSettings` from `Constants` and `CSIT_*` environment values. |
| `dashboard/services/data_cache.py` | Owns cache state, loading, refreshes, readiness, history, normalization, and dataset access. |
| `dashboard/services/lifecycle.py` | Starts startup loading, optional scheduled refreshes, and shutdown cancellation. |
| `dashboard/services/discovery.py` | Builds `datasets`, `columns`, `values`, and `schema` payloads. |
| `dashboard/services/result_metadata.py` | Loads static semantic metadata for configured `result_*` columns. |
| `dashboard/services/query.py` | Owns dataframe filtering, aggregation, sorting, projection, pagination, and validation. |
| `dashboard/services/analysis_statistics.py` | Provides internal statistical helpers for grouped summaries, trend windows, anomalies, and failure ranking. |
| `dashboard/services/analysis.py` | Builds compact analysis payloads and filter orchestration for public analysis tools. |
| `dashboard/services/telemetry.py` | Decodes base64 + zlib OpenMetrics telemetry, builds metric samples, and returns compact telemetry payloads. |
| `dashboard/services/serialization.py` | Builds JSON-safe records, shared payload dictionaries, private previews, and response-size guards. |
| `dashboard/services/observability.py` | Emits structured JSON operational log events. |
| `dashboard/mcp_tools.py` | Registers MCP tools/resources and delegates behavior to services. |
| `dashboard/routes.py` | Registers `/health`, `/ready`, and `POST /data/refresh`. |
| `dashboard/ui/dashboard.py` | Builds the Prefab dashboard from the statistics dataframe. |
| `dashboard/data/data.py` | Reads `data.yaml`, loads S3 parquet files, concatenates datasets, and validates columns. |
| `dashboard/data/result_metadata.yaml` | Defines display names, unit hints, preferred direction, and comparable dimensions for result columns. |
| `dashboard/data/fixture_data.py` | Reads local JSON fixtures for no-S3 development and smoke checks. |

Operational logs are JSON message strings emitted through Python logging. They include `event`, UTC `timestamp`, and metadata only. They do not log dataframe records, payload bodies, credentials, or raw large responses.

| Event | Meaning |
| --- | --- |
| `data_refresh_started`, `data_refresh_skipped`, `data_refresh_completed` | Refresh lifecycle and cache status. |
| `mcp_data_tool_completed` | Public data-tool call metadata and error type when applicable. |
| `mcp_analysis_tool_completed` | Public analysis-tool call metadata and error type when applicable. |
| `mcp_discovery_tool_completed` | Discovery-tool call metadata and error type when applicable. |
| `mcp_resource_completed` | Private parquet preview metadata and error type when applicable. |
| `response_too_large` | Serialization guardrail replaced an oversized response with guidance. |

## Client

The client entrypoint is `mcp-client/app.py`.

The client uses a small MCP connection state manager. During lifespan startup it attempts to connect to `MCP_SERVER_URL + MCP_PATH`, but startup does not fail if the MCP server is unavailable. It reconnects lazily before explorer rendering and client health checks, and it keeps the last successful server/tool/resource metadata in `/health`.

| Route | Meaning |
| --- | --- |
| `GET /` | Renders a dependency-free CSIT explorer with status banner, dataset tabs, query filters, paginated tables, inline SVG result charts, and compact analysis panels. |
| `GET /health` | Client liveness. Always returns HTTP 200 with MCP dependency status in the `mcp` block. |

The explorer flow is:

1. `datasets()` builds the status banner and row-count strip.
2. `columns(dataset)` chooses filter controls, result columns, and default chart metric.
3. `values(dataset, column, limit=25)` fills datalist hints for available filters.
4. `job_statistics`, `trending`, `iterative`, or `coverage` provides the table page.
5. Result datasets also call `compare_hosts`, `trend_summary`, `find_regressions`, `find_anomalies`, and `top_failures` for compact analysis panels.
6. Datasets with telemetry also call `telemetry_metrics`, `telemetry_metric_values`, `telemetry_trend_summary`, and `telemetry_anomalies` for OpenMetrics panels.

Returned MCP error payloads render inline in the relevant panel. Connection failures or required tool-call exceptions return a readable HTTP 503 status page. The client health payload includes MCP URL, connection state, last successful connection time, last error, server metadata, discovered tools/resources/prompts, and reconnect attempt count.

## Running With Docker Compose

The base compose file expects an external Docker network named `mcp` and runs services as the host UID/GID supplied through `${UID}:${GID}`.

```sh
docker network create mcp
docker compose up --build
```

For fixture mode:

```sh
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml up --build
```

Open:

- browser explorer: http://localhost:7860
- dashboard client health: http://localhost:7860/health
- server liveness: http://localhost:8000/health
- server readiness: http://localhost:8000/ready
- MCP endpoint: http://localhost:8000/mcp

Stop the stack:

```sh
docker compose down
```

The server health check uses `http://127.0.0.1:8000/ready`. The resilient client starts with the server process and reconnects lazily while S3 data loads; it no longer waits for the server health check before starting. Base S3 mode has a longer health-check start period because live parquet reads can take time. Fixture mode shortens the start period.

If your shell does not export `UID` and `GID`, pass them explicitly:

```sh
env UID=$(id -u) GID=$(id -g) docker compose up --build
```

Both Dockerfiles install dependencies with `uv sync --locked --no-install-project` before copying application source. Runtime entrypoints use `uv run --no-sync`, and both services use writable `HOME=/home/csit-mcp` and a clean `UV_CACHE_DIR=/tmp/uv-runtime-cache`. The root-owned build cache is kept separate so host UID/GID execution cannot inherit inaccessible cache files.

For S3-backed mode, host AWS credentials are mounted read-only into the server container at `/home/csit-mcp/.aws`. Fixture mode does not require AWS credentials.

## Integration With Codex

Start the stack first:

```sh
docker network create mcp
docker compose up --build
```

For local no-AWS testing, start fixture mode instead:

```sh
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml up --build
```

Configure Codex to connect to the streamable HTTP MCP endpoint:

```toml
[mcp_servers.csit_mcp]
url = "http://localhost:8000/mcp"
enabled = true
tool_timeout_sec = 120
default_tools_approval_mode = "prompt"
```

Add this block to `~/.codex/config.toml` for personal use. For repository-scoped setup, add it to `.codex/config.toml` inside this repository and trust the project in Codex.

In the Codex CLI TUI, use `/mcp` to confirm that `csit_mcp` is connected. If Codex runs remotely, `localhost` refers to the remote environment, not your laptop. Run the MCP server in the same environment as Codex or expose it through a secured reachable URL.

## Usage Examples

HTTP checks:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl -X POST http://localhost:8000/data/refresh
```

MCP endpoint:

```text
http://localhost:8000/mcp
```

Good Codex prompts:

```text
Use the CSIT MCP server to show server info.
Use the CSIT MCP server to list available datasets.
Use the CSIT MCP server to show columns for the iterative dataset.
Use the CSIT MCP server to show result metadata for iterative result columns.
Use the CSIT MCP server to list common values for iterative hosts.
Use the CSIT MCP server to list common values for trending job and test_type before querying rows.
Use the CSIT MCP server to fetch trending rows for job <job-name>, test_type mrr, columns job, build, hosts, test_id, result_receive_rate_rate_avg, limit 20.
Use the CSIT MCP server to compare hosts for iterative result_receive_rate_rate_avg on test iter-test-a.
Use the CSIT MCP server to summarize the trend for iterative result_receive_rate_rate_avg ordered by build.
Use the CSIT MCP server to find regressions for iterative result_receive_rate_rate_avg grouped by test_id.
Use the CSIT MCP server to find anomalies in trending result_receive_rate_rate_avg grouped by hosts.
Use the CSIT MCP server to show top failures in coverage grouped by test_id.
Use the CSIT MCP server to inspect telemetry metric names in trending with limit 20.
Use the CSIT MCP server to fetch telemetry samples for trending metric csit_packets_total filtered by hosts 2n-skx.
Use the CSIT MCP server to summarize telemetry metric csit_packets_total by test_id.
Use the CSIT MCP server to find telemetry anomalies for csit_packets_total grouped by hosts.
Use the CSIT MCP server to summarize job statistics for the last 7 days.
Use the CSIT MCP server to compare iterative results by host for a test_id using hosts_by_test_id aggregation and limit 20.
Use the CSIT MCP server to show coverage columns test_id, hosts, and result_pdr_lower_rate_value for VPP with limit 20.
Use the CSIT MCP server to explain why a query returned response_too_large and propose narrower filters.
Use the CSIT MCP server to check readiness and configuration errors before querying data.
Use the CSIT MCP dashboard tool and explain what data is shown.
Use the CSIT MCP server to fetch trending rows for vpp, 3na-spr, 200Ge2P1Cx7Veat, Mlx5, Ip4Base, 1C, 64B, test_type mrr, columns job, build, hosts, test_id, result_receive_rate_rate_avg, limit 20.
Are there any anomalies in the returned data?
```

For broad exploration, ask Codex to call `datasets()`, then `columns(dataset)`, then `values(dataset, column)`, and only then request records with filters, `columns`, `aggregation`, and a small `limit`.

For browser exploration, open `http://localhost:7860`, choose a dataset tab, apply filters, and use the result-column and metric selectors to update the table, chart, analysis panels, and telemetry panels.

## Development

Run server tests from `mcp-server/`:

```sh
uv run --locked python -m unittest discover
```

Run client tests from `mcp-client/`:

```sh
uv run --locked python -m unittest discover
```

Useful full check:

```sh
cd mcp-client
uv run --locked python -m py_compile app.py tests/test_app.py
uv run --locked python -m unittest discover
cd ../mcp-server
uv run --locked python -m py_compile dashboard/settings.py dashboard/data/fixture_data.py dashboard/services/data_cache.py dashboard/services/discovery.py dashboard/services/result_metadata.py dashboard/services/lifecycle.py dashboard/services/observability.py dashboard/services/query.py dashboard/services/analysis_statistics.py dashboard/services/analysis.py dashboard/services/telemetry.py dashboard/services/serialization.py dashboard/mcp_tools.py dashboard/routes.py tests/test_settings.py tests/test_data_cache.py tests/test_discovery_service.py tests/test_result_metadata_service.py tests/test_lifecycle.py tests/test_mcp_registration.py tests/test_query_service.py tests/test_analysis_service.py tests/test_telemetry_service.py tests/test_serialization_service.py
uv run --locked python -m unittest discover
cd ..
git diff --check
```

Current test coverage includes:

- client startup, lazy reconnect, `/health`, explorer rendering, query propagation, inline MCP errors, and failure pages
- data cache state transitions, refresh history, failed refresh preservation, and fixture mode
- startup settings validation, CORS validation, and configuration status metadata
- lifecycle scheduling without import-time S3 loading and opt-in scheduled refresh
- MCP tool/resource registration and response shapes
- discovery, result metadata, query, and serialization service behavior
- public analysis tools plus internal analysis/statistics service behavior
- OpenMetrics telemetry decoding, parsing, fixture samples, MCP telemetry tools, and client telemetry panels
- structured observability logs and response-size safety
- dashboard UI builder behavior
- `/health`, `/ready`, and `POST /data/refresh`

## Repository Map

```text
.
|-- docker-compose.yaml
|-- docker-compose.fixture.yaml
|-- doc/
|   |-- code/
|   |   |-- README.md
|   |   |-- api.md
|   |   |-- architecture.md
|   |   |-- configuration.md
|   |   |-- data-model.md
|   |   |-- deployment.md
|   |   |-- integration.md
|   |   |-- operations.md
|   |   |-- setup.md
|   |   |-- testing.md
|   |   |-- open-questions.md
|   |   `-- diagrams/
|   |-- diagrams/
|   |   |-- architecture.drawio
|   |   |-- architecture.svg
|   |   |-- data-flow.drawio
|   |   |-- data-flow.svg
|   |   |-- improvements-roadmap.drawio
|   |   `-- improvements-roadmap.svg
|   |-- improvements/
|   |   |-- improvements1.md
|   |   |-- improvements2.md
|   |   |-- improvements3.md
|   |   |-- improvements4.md
|   |   `-- improvements5.md
|   `-- tasks/
|       |-- task1.md
|       |-- task2.md
|       |-- task3.md
|       |-- task4.md
|       |-- task5.md
|       `-- task_code_doc.md
|-- mcp-client/
|   |-- .dockerignore
|   |-- .python-version
|   |-- app.py
|   |-- Dockerfile
|   |-- docker-bake.hcl
|   |-- pyproject.toml
|   |-- tests/
|   |   |-- __init__.py
|   |   `-- test_app.py
|   `-- uv.lock
|-- mcp-server/
|   |-- .dockerignore
|   |-- .python-version
|   |-- server.py
|   |-- Dockerfile
|   |-- pyproject.toml
|   |-- uv.lock
|   |-- dashboard/
|   |   |-- __init__.py
|   |   |-- mcp_tools.py
|   |   |-- routes.py
|   |   |-- settings.py
|   |   |-- data/
|   |   |   |-- data.py
|   |   |   |-- data.yaml
|   |   |   |-- fixture_data.py
|   |   |   |-- result_metadata.yaml
|   |   |   |-- fixtures/
|   |   |   `-- _metadata/
|   |   |-- services/
|   |   |   |-- analysis.py
|   |   |   |-- analysis_statistics.py
|   |   |   |-- data_cache.py
|   |   |   |-- discovery.py
|   |   |   |-- lifecycle.py
|   |   |   |-- observability.py
|   |   |   |-- query.py
|   |   |   |-- result_metadata.py
|   |   |   |-- serialization.py
|   |   |   `-- telemetry.py
|   |   |-- ui/
|   |   `-- utils/
|   `-- tests/
|       |-- test_analysis_service.py
|       |-- test_data_cache.py
|       |-- test_discovery_service.py
|       |-- test_lifecycle.py
|       |-- test_mcp_registration.py
|       |-- test_query_service.py
|       |-- test_result_metadata_service.py
|       |-- test_serialization_service.py
|       |-- test_settings.py
|       |-- test_telemetry_service.py
|       `-- test_ui_dashboard.py
```

## Notes

- Both services target Python `>=3.13` and include `uv.lock`.
- `CSIT_DATA_MODE=fixture` is the no-S3 local development and smoke-check path.
- `/health` is process liveness; `/ready` is data readiness.
- Public data responses are size-guarded; the private parquet resource returns previews, not full uncapped datasets.
- Public analysis responses are compact summaries intended for Codex, Claude-compatible MCP clients, and the browser explorer.
- The browser explorer is dependency-free Starlette-rendered HTML with inline CSS/SVG and small query-param based interactions.
- Operational logs are structured JSON metadata and intentionally exclude dataframe records and payload bodies.
- Project diagrams are stored in `doc/diagrams/` as editable `.drawio` files and exported `.svg` files.
