# Build And Deployment

## Images

Both [`Dockerfile`](../../mcp-server/Dockerfile) files use the Python 3.13
Trixie slim `uv` image. They:

1. copy `.python-version`, `pyproject.toml`, and `uv.lock`;
2. run `uv sync --locked --no-install-project`;
3. copy application source;
4. run with `uv run --no-sync`.

This makes dependency layers reproducible and source-change friendly. The
server temporarily installs a compiler toolchain for dependency installation
and removes it in the same layer.

Runtime entrypoints:

| Image | Entrypoint |
| --- | --- |
| Server | `fastapi run server.py --host 0.0.0.0 --port 8000` |
| Client | `app.py`, which starts Uvicorn on port 7860 |

Each service has a `.dockerignore` excluding virtual environments, bytecode,
test/cache artifacts, and local noise while retaining runtime source and
fixtures.

## Compose

[`docker-compose.yaml`](../../docker-compose.yaml) defines:

| Service | Published port | Health/start behavior |
| --- | ---: | --- |
| `mcp-server` | `8000` | Health check calls `/ready`; long S3 start period. |
| `mcp-client` | `7860` | Starts after the server process starts, not after readiness; reconnects lazily. |

The external network `mcp` must already exist:

```sh
docker network create mcp
docker compose up --build
```

[`docker-compose.fixture.yaml`](../../docker-compose.fixture.yaml) sets fixture
mode and a shorter health-check start period:

```sh
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml up --build
```

## Runtime Identity

Compose preserves host file ownership with `user: "${UID}:${GID}"`. Images
create world-writable runtime locations:

- `HOME=/home/csit-mcp`
- `UV_CACHE_DIR=/tmp/uv-runtime-cache`

The build cache and runtime cache are separate, avoiding root-owned cache files
when containers run as an arbitrary host identity.

## AWS Credentials

S3 mode mounts host `$HOME/.aws` read-only at `/home/csit-mcp/.aws` and sets:

- `AWS_SHARED_CREDENTIALS_FILE=/home/csit-mcp/.aws/credentials`
- `AWS_CONFIG_FILE=/home/csit-mcp/.aws/config`

Fixture mode does not use AWS. Credentials are runtime secrets and are not
copied into the image.

## Build And Validate

```sh
docker compose config
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml config
docker compose build mcp-server
docker compose build mcp-client
```

After startup:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:7860/health
```

## Process And Persistence Model

- One server process owns the active in-memory cache and optional scheduler.
- Targeted telemetry decoding runs in short-lived child processes with a
  configurable Linux address-space limit; worker failure does not terminate the
  server process.
- One client process owns an in-memory MCP connection state.
- Base Compose mounts `csit-mcp-cache` and stores an Arrow-native generation at
  `/home/csit-mcp/cache/data`: public result frames, private telemetry sidecars,
  and compact locators. Checksums and round-trip validation protect promotion;
  generation IDs, row counts, file/schema hashes, and the previous valid
  generation support validated fallback.
- Refresh history, sampled telemetry indexes, client connection metadata, and
  generated exports are not persisted.
- S3 streaming reads use bounded adaptive retries. A failed refresh preserves
  the restored or previously successful generation.
- Export responses are generated in memory and returned immediately.
- Horizontal replicas do not share cache state or refresh history.

## CI/CD

No CI workflow or deployment manifest beyond Docker Compose is checked into
this repository. Production registry, orchestration, rollout, and secret
management are therefore external to the documented codebase.
