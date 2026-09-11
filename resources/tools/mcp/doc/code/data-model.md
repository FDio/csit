# Data Model And Storage

There is no database. Source data is loaded into an in-memory dataframe cache
owned by [`DataCacheService`](../../mcp-server/dashboard/services/data_cache.py).
Refresh history is process-local. When `CSIT_CACHE_SNAPSHOT_PATH` is set, the
last complete cache generation survives restarts in Arrow-native parquet files.
Its manifest records a generation ID, row counts, file hashes, and schema
hashes; restore falls back to the retained previous generation when validation
of the current one fails.

## Source Datasets

| Key | Readiness | Content |
| --- | --- | --- |
| `statistics` | Required | Job, build, start time, and duration. |
| `trending` | Required | Current time-series results, run metadata, and pass state; encoded telemetry is detached privately. |
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

Each loaded dataframe is owned by the cache and normalized before publication.
The raw telemetry column is detached first so generic filtering, projection,
pagination, and preview serialization cannot copy or return encoded blobs.
Normalization converts:

- every `start_time` to an Arrow-backed UTC timestamp or null, converted to
  ISO-8601 only at serialization boundaries;
- `build` to nullable integer;
- `passed` to nullable boolean;
- text dimensions to Arrow-backed strings;
- numeric `result_*` columns with Pandas numeric coercion;
- list-valued hosts to Arrow `list<string>` while retaining scalar host strings.

Reads do not mutate the cache. Per-dataset status records the status, required
and enabled flags, configured state, row/column metadata, normalization time,
and telemetry status. Empty required data fails the first load; a later failed
refresh leaves the previous successful cache serving in degraded state.
On a cold load, Statistics and Trending are read and published first. Optional
Iterative and Coverage reads then continue while required data is serving-ready.
Partition frames are released as soon as each combined source dataset is owned.

Derived Statistics, Trending, Iterative, Coverage, and Comparison indexes are
owned by a generation-aware registry. They are built lazily, dictionary-encode
repeated dimensions when beneficial, and are cleared on a generation swap.
Comparison retains projected references to canonical Iterative columns rather
than a second Python `list[dict]` copy. Statistics run enrichment is computed
once per generation.

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
`UNIT`, and EOF markers into long-form dataframes. Label parsing accepts
standard double quotes and the unquoted or single-quoted CSIT dialect, then
normalizes values before building `label_key` or applying query filters.

Each sample carries source context such as dataset, job, build, time, test and
DUT dimensions, hosts, pass state, plus metric name, label dictionary,
normalized label key, value, timestamp, type, unit, and help text.

Result rows gain small decode metadata, including metric count and parse error.
Malformed telemetry is reported by status counters and does not invalidate the
result dataframe. Indexing is bounded per dataset by source-row and sample
limits; truncation is explicit. This representative index is intended for
discovery and diagnostics, not authoritative historical analysis. Legacy
telemetry tool responses include an `index` block identifying that scope and
its indexed versus total source-row coverage.

[`telemetry_locator.py`](../../mcp-server/dashboard/services/telemetry_locator.py)
builds a compact passed-row mapping from logical Trending series to private
source-row IDs without running JumpAvg or copying result metrics.
[`telemetry_query.py`](../../mcp-server/dashboard/services/telemetry_query.py)
uses that locator to filter the time window and testbed before reading the raw
sidecar, applies encoded and decoded byte limits, and caches decoded metric
subsets by cache generation. Selected cells are handed to
[`telemetry_worker.py`](../../mcp-server/dashboard/services/telemetry_worker.py),
which performs decode and parsing in a disposable process with a deadline and
Linux memory limit. Its
responses report completeness and explicitly state that the representative
index was not used. Selection diagnostics distinguish absent source metrics,
missing requested nodes, and semantic-policy rejection. The semantic
cycles-per-packet selector accepts production DUT/rate labels, prefers direct
`clocks_per_packets`, permits active `runtime.clocks` as a fallback, and keeps
thread identity explicit. Completed responses are also cached with entry and
internal 8 MB total-size bounds.

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
- private raw-sidecar and locator row counts;
- snapshot generation, restore time, and validation errors;
- normalized configuration and validation errors;
- cgroup, canonical cache, derived-index, and telemetry-query memory estimates;
- the latest refresh-admission skip reason;
- up to 10 completed refresh-history entries.

This same snapshot appears in `/ready`, refresh responses, `server://info`,
discovery status, and cache-error payloads.
