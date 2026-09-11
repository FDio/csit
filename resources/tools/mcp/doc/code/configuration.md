# Configuration

Settings are resolved once during server/client startup. Sources are
[`settings.py`](../../mcp-server/dashboard/settings.py),
[`constants.py`](../../mcp-server/dashboard/utils/constants.py), and
[`app.py`](../../mcp-client/app.py).

## Server Settings

| Variable | Default | Rules |
| --- | --- | --- |
| `CSIT_DATA_MODE` | `s3` | Must be `s3` or `fixture`. |
| `CSIT_TIME_PERIOD` | `200` | Positive integer; capped by the fixed 200-day maximum. |
| `CSIT_REFRESH_INTERVAL_SECONDS` | `0` | Integer; positive schedules refresh, zero/negative disables it. |
| `CSIT_CORS_ALLOW_ORIGINS` | `*` | Wildcard alone, or comma-separated HTTP(S) origins. |
| `CSIT_MAX_POOL_SIZE` | `30` | Positive integer. |
| `CSIT_TELEMETRY_MAX_SOURCE_ROWS` | `500` | Positive integer per source dataset. |
| `CSIT_TELEMETRY_MAX_SAMPLES` | `100000` | Positive integer per source dataset. |
| `CSIT_START_TRENDING` | `true` | Boolean-compatible validated flag. |
| `CSIT_START_STATISTICS` | `true` | Boolean-compatible validated flag. |
| `CSIT_START_REPORT` | `true` | Controls Iterative optional-dataset readiness semantics. |
| `CSIT_START_COVERAGE` | `true` | Controls Coverage optional-dataset readiness semantics. |
| `CSIT_START_FAILURES` | `true` | Validated compatibility flag. |
| `CSIT_AWS_ENDPOINT_URL` | empty | Optional S3-compatible endpoint used by the reader. |

Boolean values are case-insensitive `true/yes/y/1` or `false/no/n/0`.

`CSIT_MAX_TIME_PERIOD` appears in status metadata but is not an environment
setting; the code fixes it at 200 days. The server MCP path is also fixed at
`/mcp`.

Invalid validated values are collected in `AppSettings.validation_errors`.
The process remains alive, but loading fails before a reader is constructed,
`/ready` returns `503`, and the status `configuration` block contains normalized
effective values and field-level errors.

## Data Specification

[`data.yaml`](../../mcp-server/dashboard/data/data.yaml) controls S3 paths,
partitions, releases, schema files, and selected columns. It is source
configuration, not runtime environment. [`result_metadata.yaml`](../../mcp-server/dashboard/data/result_metadata.yaml)
controls result-column semantics.

## Client Settings

| Variable | Default | Purpose |
| --- | --- | --- |
| `MCP_SERVER_URL` | `http://mcp-server:8000` | MCP server base URL. |
| `MCP_PATH` | `/mcp` | Path appended to the server URL. |

Direct local execution normally sets `MCP_SERVER_URL=http://localhost:8000`.

## Container Settings

Compose sets:

| Variable | Value |
| --- | --- |
| `HOME` | `/home/csit-mcp` |
| `UV_CACHE_DIR` | `/tmp/uv-runtime-cache` |
| `AWS_SHARED_CREDENTIALS_FILE` | `/home/csit-mcp/.aws/credentials` |
| `AWS_CONFIG_FILE` | `/home/csit-mcp/.aws/config` |

Both services run as the host `UID:GID`. The server AWS mount is read-only.
Do not bake credentials into images or commit them.

## CORS

[`server.py`](../../mcp-server/server.py) applies FastAPI `CORSMiddleware`.
Allowed methods are GET, POST, and OPTIONS. Allowed request headers are MCP
protocol/session headers, Authorization, and Content-Type; the MCP session ID
response header is exposed.

The default wildcard is intended for trusted local use. Production deployments
should provide explicit origins. A wildcard mixed with named origins or a
non-HTTP(S) origin is invalid configuration.

## Compose Overrides

The base [`docker-compose.yaml`](../../docker-compose.yaml) is S3-backed.
It sets `CSIT_TIME_PERIOD=20` and `CSIT_START_REPORT=False`, which differ from
the corresponding code defaults. It also sets the other documented start flags
to true.
[`docker-compose.fixture.yaml`](../../docker-compose.fixture.yaml) sets
`CSIT_DATA_MODE=fixture` and shortens the readiness start period. Compose
environment values override image defaults.
