# APIs And Interfaces

Source of truth:

- MCP: [`mcp_tools.py`](../../mcp-server/dashboard/mcp_tools.py)
- Server HTTP: [`routes.py`](../../mcp-server/dashboard/routes.py)
- Client HTTP: [`app.py`](../../mcp-client/app.py)

## Server HTTP

| Method | Path | Status | Response |
| --- | --- | --- | --- |
| `GET` | `/health` | `200` | `{"status":"healthy","service":"mcp-server"}` |
| `GET` | `/ready` | `200` or `503` | Service name plus `data_cache.status_snapshot()`. |
| `POST` | `/data/refresh` | `202` or `409` | `refresh_started` or `refresh_in_progress`, plus data status. |
| MCP | `/mcp` | protocol-dependent | FastMCP Streamable HTTP endpoint. |

`/health` is process liveness. `/ready` is the dependency signal used by the
server Compose health check.

## MCP Resources

| URI | Visibility | Contract |
| --- | --- | --- |
| `server://info` | Public | Name, version, 27-tool count/list, one public resource, private resource list, and full data status. |
| `data://parquet/{query}` | Private/internal | JSON preview for `statistics`, `trending`, `iterative`, `coverage`, or `all`. |

The parquet resource caps each preview at 1,000 records and reports
`total_row_count`, `returned_count`, `has_more`, and `truncated`. Use public
tools for normal queries.

## Discovery Tools

| Tool | Signature | Result |
| --- | --- | --- |
| `datasets` | `()` | Dataset/cache/telemetry status, row counts, freshness, and configured partitions. |
| `columns` | `(dataset)` | Configured and cached columns, dtype/count flags, and result metadata. |
| `values` | `(dataset, column, limit=100)` | Common JSON-safe values and counts; list-valued hosts include a normalized key. |
| `schema` | `(dataset)` | `data.yaml` entries, configured/result columns, and result metadata. |

`datasets` and `schema` work from configuration/status without requiring a
ready dataframe. `columns` can return configuration-only metadata before
readiness. `values` requires cached data.

## Generic Data Tools

`trending`, `iterative`, and `coverage` share this shape:

```text
(
  test_type=None, dut_type=None, passed=None, job=None, release=None,
  hosts=None, test_id=None, build=None, offset=0, aggregation="none",
  sort_by=None, sort_order="desc", columns=None, limit=1000
)
```

`limit` is 1..10,000 and `offset` is non-negative. `hosts` accepts a string or
list of strings. Aggregation is `none`, `hosts`, `test_id`, or
`hosts_by_test_id`. Aggregated records include row/pass/fail counts and
min/mean/max summaries for numeric `result_*` columns.

`job_statistics`:

```text
(days=None, job=None, limit=1000, dut=None, test_type=None,
 cadence=None, testbed=None, select_defaults=False)
```

With `select_defaults=false`, this remains a broad statistics query. With
`true`, it normalizes the cascading dashboard selections, joins Trending by
exact job and normalized build, and adds counts, DUT version, and hosts.

## Generic Analysis Tools

These accept only `trending`, `iterative`, or `coverage`:

| Tool | Signature summary |
| --- | --- |
| `compare_hosts` | `(dataset, result_column, test_id=None, test_type=None, dut_type=None, job=None, release=None, build=None, passed=None, preferred_direction=None)` |
| `trend_summary` | `(dataset, result_column, test_id=None, test_type=None, dut_type=None, job=None, release=None, hosts=None, passed=None, order_by="build", recent_count=3, baseline_count=3)` |
| `find_regressions` | `(dataset, result_column, group_by="test_id", filters..., order_by="build", recent_count=3, baseline_count=3, threshold_percent=10.0, preferred_direction=None, limit=20)` |
| `find_anomalies` | `(dataset, result_column, group_by=None, filters..., threshold=2.0, limit=20)` |
| `top_failures` | `(dataset, group_by="test_id", filters..., build=None, limit=20)` |

Responses are compact analysis envelopes with `schema_version`, `analysis`,
`dataset`, normalized filters, source row count, freshness, data status,
summary, records, and explanation. Result metadata supplies preferred direction
unless explicitly overridden.

## Telemetry Tools

| Tool | Signature summary |
| --- | --- |
| `telemetry_metrics` | `(dataset, metric_name=None, label_key=None, result filters..., offset=0, limit=100)` |
| `telemetry_metric_values` | `(dataset, metric_name, group_by="metric_name", label_key=None, filters..., limit=20)` |
| `telemetry_trend_summary` | `(dataset, metric_name, group_by="metric_name", label_key=None, filters..., order_by="build", recent_count=3, baseline_count=3, limit=20)` |
| `telemetry_anomalies` | `(dataset, metric_name, group_by="metric_name", label_key=None, filters..., threshold=2.0, limit=20)` |

Supported telemetry sources are result datasets with indexed telemetry.
Telemetry tools query long-form samples, not the encoded source cells.

## Dashboard-Oriented Tools

### Trending

```text
trending_catalog(
  dut=None, area=None, test=None, infra=None, testbed=None,
  framesize=None, cores=None, test_type=None,
  select_defaults=False, offset=0, limit=1000
)
trending_series(series: list[str], offset=0, limit=1000)
```

The catalog returns cascading options and stable host-independent logical
series IDs. Series output contains passed-only semantic throughput, bandwidth,
and latency points. NDR/PDR source rows expand into separate series. Additive
JumpAvg analysis is calculated over complete chronological history before
pagination; latency reverses progression/regression direction because lower is
better.

### Iterative

```text
iterative_catalog(
  release=None, dut=None, dut_version=None, area=None, test=None,
  infra=None, testbed=None, framesize=None, cores=None, test_type=None,
  select_defaults=False, offset=0, limit=1000
)
iterative_series(series: list[str], offset=0, limit=1000)
```

The catalog includes release and DUT version in its cascade and stable series
identity. Series output is passed-only and supplies semantic points for client
box plots.

### Coverage

```text
coverage_catalog(
  release=None, dut=None, dut_version=None, area=None, infra=None
)
coverage_tables(
  release, dut, dut_version, area, infra, offset=0, limit=1000
)
```

Nothing is selected automatically. `coverage_tables` requires a complete valid
selection and returns passed-only flattened accordion rows, MPPS/Gbps values,
decoded latency percentiles, result URLs, and direction-availability flags.

### Comparison

```text
comparison_catalog(
  release=None, dut=None, dut_version=None, infra=None,
  framesize=None, cores=None, test_type=None, parameter=None, value=None
)
comparison_table(
  release, dut, dut_version, infra, framesize, cores, test_type,
  parameter, value, remove_extreme_outliers=False,
  offset=0, limit=1000
)
comparison_data(
  release, dut, dut_version, infra, framesize, cores, test_type,
  parameter, value, offset=0, limit=1000
)
```

The catalog limits candidates to values with overlapping canonical tests and
matching normalized units. Summary data uses passed finite samples and sample
stdev. Raw data contains matching passed and failed source rows. DUT version
comparison candidates may cross releases.

### Legacy Dashboard

`dashboard()` returns a Prefab app built from the Statistics dataframe. The
browser client does not use this tool.

## Pagination And Errors

Paginated tools use:

```json
{
  "row_count": 2500,
  "returned_count": 500,
  "offset": 0,
  "limit": 500,
  "has_more": true,
  "next_offset": 500,
  "records": []
}
```

Common MCP error names:

| Error | Meaning |
| --- | --- |
| `validation_error` | Invalid arguments, dataset, field, group, or incomplete selection. |
| `data_unavailable` | Required cache/telemetry state cannot currently serve the call. |
| `dataset_not_found` | Requested cached dataset does not exist. |
| `response_too_large` | JSON exceeded the 1,000,000-byte boundary. |

MCP handlers return JSON strings for structured tools/resources. The Prefab
`dashboard` tool is the exception.

## Client HTTP

| Method | Path | Inputs | Behavior |
| --- | --- | --- | --- |
| `GET` | `/` | `dataset` plus tab-specific query parameters | Renders the dashboard; `303` canonical redirects are used for Trending/Iterative add/remove actions. |
| `GET` | `/health` | none | Always `200`; nested `mcp` block reports dependency state. |
| `GET` | `/api/statistics/run-details` | `job`, non-negative `build` | Paginated failed-test IDs with canonical display names. |
| `GET` | `/api/statistics/export` | format/name and Statistics filters | Fresh CSV/XLSX snapshot plus failed tests. |
| `GET` | `/api/trending/export` | format/name and repeated `series` | Complete selected-series export. |
| `GET` | `/api/iterative/export` | format/name and repeated `series` | Complete selected-series export. |
| `GET` | `/api/coverage/export` | format/name and complete Coverage filters | Complete filtered table export. |
| `GET` | `/api/comparison/export` | `view=table|data`, format/name, complete selection | Summary or raw-data export. |

Client API errors are JSON:

- `400`: invalid or incomplete request arguments.
- `502`: malformed, truncated, or inconsistent MCP pagination/payload.
- `503`: MCP connection, data availability, or tool-call failure.

The HTML page renders structured MCP errors inline when possible. Connection
or thrown required-tool failures return the readable HTTP `503` status page.
