# Data Model And Storage

There is no database. Source data is loaded into an in-memory dataframe cache
owned by [`DataCacheService`](../../mcp-server/dashboard/services/data_cache.py).
The cache and refresh history disappear on process restart.

## Source Datasets

| Key | Readiness | Content |
| --- | --- | --- |
| `statistics` | Required | Job, build, start time, and duration. |
| `trending` | Required | Current time-series results, run metadata, pass state, and embedded telemetry. |
| `iterative` | Optional | Release-tagged repeated samples used by Iterative and Comparison. |
| `coverage` | Optional | Release-tagged NDR/PDR rates, bandwidth, and latency histograms. |

[`data.yaml`](../../mcp-server/dashboard/data/data.yaml) is the source
specification for S3 prefixes, partitions, releases, Arrow schemas, and selected
columns. [`data.py`](../../mcp-server/dashboard/data/data.py) reads parquet
through AWS Wrangler. The time window applies only to Statistics and Trending;
Iterative and Coverage load their configured release data.

[`fixture_data.py`](../../mcp-server/dashboard/data/fixture_data.py) reads one
JSON list per dataset from [`fixtures/`](../../mcp-server/dashboard/data/fixtures/).
It applies the same time-window rule and is intended for development/tests.

## Cache-Boundary Normalization

Each loaded dataframe is copied before publication. Normalization converts:

- every `start_time` to a UTC ISO-8601 string or null;
- `build` to nullable integer;
- `passed` to nullable boolean;
- `test_id`, `job`, `release`, `dut_type`, and `test_type` to compatible strings;
- numeric `result_*` columns with Pandas numeric coercion;
- Arrow/list/tuple/set host values to `list[str]` while retaining scalar host
  strings as strings.

Reads do not mutate the cache. Per-dataset status records the status, required
and enabled flags, configured state, row/column metadata, normalization time,
and telemetry status. Empty required data fails the first load; a later failed
refresh leaves the previous successful cache serving in degraded state.

## Result Metadata

[`result_metadata.yaml`](../../mcp-server/dashboard/data/result_metadata.yaml)
maps known `result_*` columns to:

- display name;
- fixed unit or unit-column reference;
- scale;
- preferred direction: higher, lower, or neutral;
- comparable dimensions;
- short description.

Discovery adds this metadata to `columns(dataset)` and `schema(dataset)`.
Generic analysis uses preferred direction when the caller does not override it.

## Telemetry Model

Telemetry source cells contain one or more base64/zlib-encoded OpenMetrics text
documents. [`telemetry.py`](../../mcp-server/dashboard/services/telemetry.py)
parses metric samples, labels, optional timestamps, comments, `HELP`, `TYPE`,
`UNIT`, and EOF markers into long-form dataframes.

Each sample carries source context such as dataset, job, build, time, test and
DUT dimensions, hosts, pass state, plus metric name, label dictionary,
normalized label key, value, timestamp, type, unit, and help text.

Result rows gain small decode metadata, including metric count and parse error.
Malformed telemetry is reported by status counters and does not invalidate the
result dataframe. Indexing is bounded per dataset by source-row and sample
limits; truncation is explicit.

## Semantic Result Series

[`result_series.py`](../../mcp-server/dashboard/services/result_series.py)
extracts topology, architecture, NIC, driver, area, frame size, core count, and
logical test type from CSIT test IDs. It also maps source result fields into:

- throughput value and unit;
- bandwidth value and unit;
- latency value and unit.

Trending and Iterative stable series IDs exclude hosts/testbed, so host changes
do not split one logical test. The first host remains a selectable testbed.
NDR/PDR rows expand into two logical series.

### Trending

Only passed rows become Trending points. [`trending_analysis.py`](../../mcp-server/dashboard/services/trending_analysis.py)
runs `jumpavg.classify()` over complete chronological series grouped by series
ID, metric, and unit. Each sample receives group trend/stdev and only the first
sample of a changed group is marked progression or regression. Lower latency is
progression; higher throughput/bandwidth is progression.

### Iterative

Only passed rows become Iterative points. The client groups finite non-negative
values by selected series and computes linear Q1/median/Q3, theoretical
1.5-IQR fences, observed whiskers, and outliers.

### Coverage

[`coverage.py`](../../mcp-server/dashboard/services/coverage.py) keeps passed
rows, derives suite/accordion/test labels, converts packet rates to MPPS and
bandwidth to Gbps, and decodes six forward/reverse PDR HDR Histograms. P50, P90,
and P99 are integer microseconds. Missing or malformed histograms leave empty
cells and increment decode-error metadata.

Coverage test names link to FD.io result artifacts using job, build, and the
slash-normalized test ID.

### Comparison

[`comparison.py`](../../mcp-server/dashboard/services/comparison.py) builds from
Iterative source rows. It normalizes DUT versions by removing architecture
suffixes and trailing Git hashes while preserving meaningful qualifiers.

Summary records use passed finite samples:

- arithmetic mean;
- sample standard deviation;
- optional independent Tukey 1.5-IQR removal for each side;
- relative mean: `(comparison - reference) / reference * 100`;
- propagated relative stdev from each side's stdev/mean ratio.

Candidate values require at least one overlapping canonical test and matching
normalized units. `comparison_data` retains matching passed and failed source
rows for raw export.

## Statistics Join

[`statistics.py`](../../mcp-server/dashboard/services/statistics.py) parses DUT,
test type, cadence, and testbed from job names. It joins Statistics to Trending
by exact job and normalized build and adds pass/fail/total counts, DUT versions,
and first-seen deduplicated hosts. Unmatched runs remain available with missing
result metadata.

## Status Model

`status_snapshot()` exposes:

- `status` and serving-ready boolean;
- attempt/success timestamps and cache age;
- last error and refresh source;
- load duration and row counts;
- per-dataset metadata;
- per-dataset telemetry metadata;
- normalized configuration and validation errors;
- up to 10 completed refresh-history entries.

This same snapshot appears in `/ready`, refresh responses, `server://info`,
discovery status, and cache-error payloads.
