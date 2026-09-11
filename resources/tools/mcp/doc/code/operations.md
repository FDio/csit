# Operations And Troubleshooting

## Health And Readiness

| Endpoint | Meaning |
| --- | --- |
| Server `GET /health` | Process liveness only; always `200` while the app responds. |
| Server `GET /ready` | Cache/configuration readiness; `200` for ready/degraded-but-servable, otherwise `503`. |
| Client `GET /health` | Client liveness; always `200` with nested MCP dependency state. |

The client health `mcp` object includes URL, connected state, last successful
connection, latest error/time, server identity, tool/resource/prompt names, and
reconnect attempts. A healthy client can report a disconnected MCP dependency.

## Refresh Operations

```sh
curl -X POST http://localhost:8000/data/refresh
```
- `202 refresh_started`: background refresh accepted.
- `409 refresh_in_progress`: another refresh is active.

Startup, manual, and scheduled attempts are recorded separately. The in-memory
history retains the 10 most recent completed attempts with start/end time,
duration, source, final status, error, and row counts.

If a refresh fails after a successful load, the old cache remains available and
status becomes degraded. If no successful required cache exists, status is
failed.

## Status Inspection

```sh
curl -s http://localhost:8000/ready
curl -s http://localhost:7860/health
```

Important server status fields:

- `status`, `ready`, `last_error`;
- `last_attempt_at`, `last_success_at`, `cache_age_seconds`;
- `last_refresh_started_by` and `load_duration_seconds`;
- `row_counts` and per-dataset `datasets` entries;
- per-dataset `telemetry` indexing/decode/parse/truncation metadata;
- `configuration.valid`, errors, and effective values;
- `refresh_history`.

## Structured Logs

[`observability.py`](../../mcp-server/dashboard/services/observability.py)
emits one JSON object per operational event through Python logging. Important
events include:

| Event | Meaning |
| --- | --- |
| `data_refresh_started` | A startup/manual/scheduled attempt began. |
| `data_refresh_skipped` | A concurrent attempt was rejected. |
| `data_cache_published` | Normalized required data became available. |
| `telemetry_index_started` / `telemetry_index_completed` | Bounded telemetry expansion progress and counters. |
| `data_refresh_completed` | Final refresh status, duration, row counts, error, and cache age. |
| `mcp_discovery_tool_completed` | Discovery call metadata. |
| `mcp_data_tool_completed` | Generic or dataset-oriented data call metadata. |
| `mcp_analysis_tool_completed` | Analysis call metadata. |
| `mcp_resource_completed` | Resource preview metadata. |
| `response_too_large` | A payload was replaced by a guarded error. |

Logs intentionally exclude dataframe records, response bodies, telemetry
payloads, and credentials.

## Payload Safety

Structured MCP output is capped at 1,000,000 serialized bytes. The private
parquet resource additionally previews at most 1,000 records per dataset.

When `response_too_large` is returned:

1. reduce `limit`;
2. select only required columns;
3. add exact dimension filters;
4. use aggregation or a compact analysis tool;
5. paginate with `offset` where supported.

Client export endpoints deliberately follow complete pagination and reject
malformed or truncated upstream results rather than silently exporting partial
data.

## Dashboard Failure Behavior

- Structured MCP errors are rendered inline in the relevant tab.
- Connection failures or thrown required-tool errors return a readable HTML
  `503` page with MCP state.
- Statistics failed-test details load lazily and keep errors inside the modal.
- Trending/Iterative details use already rendered data and make no later MCP
  request.
- Export endpoints return JSON errors with `400`, `502`, or `503`.
- Client startup continues when the server is down; a later request triggers a
  shared reconnect attempt.

## Common Failures

| Symptom | Likely cause | Action |
| --- | --- | --- |
| `/health` is 200, `/ready` is 503 | Loading, invalid settings, credentials, or missing required data. | Inspect `data.status`, `last_error`, and `configuration`. |
| Ready but optional tab is empty | Iterative/Coverage missing, disabled, or filtered out. | Inspect `data.datasets` and call the relevant catalog. |
| Telemetry has zero samples | Decode/parse failures, no source cells, or index limits. | Inspect `data.telemetry` counters and truncation. |
| Browser returns 503 | MCP connection or required tool raised. | Check client `/health`, then server `/ready` and logs. |
| Catalog selection becomes stale | Cache refresh changed available semantic IDs/options. | Re-run the catalog and use normalized filters/returned IDs. |
| Export returns 502 | Malformed or incomplete upstream pagination. | Check server logs and repeat the underlying MCP tool. |
| XLSX/CSV download is empty | Valid selection has no matching records. | Inspect the rendered tab and catalog/table response. |
| CORS/configuration failure | Invalid origin list or typed setting. | Read `data.configuration.errors` and restart after correction. |

## Useful Commands

```sh
docker compose ps
docker compose logs -f mcp-server
docker compose logs -f mcp-client
curl -s http://localhost:8000/ready
curl -s http://localhost:7860/health
curl -X POST http://localhost:8000/data/refresh
```
