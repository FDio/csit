# Setup And Local Development

## Prerequisites

- Python 3.13.
- [`uv`](https://docs.astral.sh/uv/) capable of reading the committed lockfiles.
- Docker Engine with Compose v2 for the container workflow.
- AWS credentials only for S3 mode.

Both manifests declare Python `>=3.13`; the exact dependency sets are in
[`mcp-server/pyproject.toml`](../../mcp-server/pyproject.toml) and
[`mcp-client/pyproject.toml`](../../mcp-client/pyproject.toml).

## Install Locally

```sh
cd mcp-server
uv sync --locked

cd ../mcp-client
uv sync --locked
```

## Fixture Compose Workflow

Fixture mode is deterministic and does not require AWS:

```sh
docker network create mcp
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml up --build
```

The network command is needed only once. Open:

- Dashboard: `http://localhost:7860`
- Client health: `http://localhost:7860/health`
- Server readiness: `http://localhost:8000/ready`
- MCP endpoint: `http://localhost:8000/mcp`

Stop with:

```sh
docker compose down
```

## S3 Compose Workflow

The base Compose file uses S3 mode and mounts host credentials read-only:

```sh
docker compose up --build
```

If `UID` and `GID` are not exported:

```sh
env UID=$(id -u) GID=$(id -g) docker compose up --build
```

AWS files are read from `$HOME/.aws` on the host and appear at
`/home/csit-mcp/.aws` in the server container.

## Run Services Directly

Start the server from `mcp-server/`:

```sh
CSIT_DATA_MODE=fixture uv run --locked fastapi run server.py \
  --host 0.0.0.0 --port 8000
```

Start the client from `mcp-client/` in another terminal:

```sh
MCP_SERVER_URL=http://localhost:8000 MCP_PATH=/mcp \
  uv run --locked app.py
```

The fixture reader resolves files relative to the server package, so run the
server with `mcp-server/` as the working directory.

## Common Commands

```sh
# Server tests and import smoke
cd mcp-server
uv run --locked python -m unittest discover
uv run --locked python -c "import server; assert server.app"

# Client tests
cd ../mcp-client
uv run --locked python -m unittest discover

# Compose validation
cd ..
docker compose config
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml config

# Documentation and whitespace checks
xmllint --noout doc/diagrams/*.drawio doc/diagrams/*.svg \
  doc/code/diagrams/*.drawio doc/code/diagrams/*.svg
git diff --check
```

## Development Notes

- Server settings are resolved once at import; restart after environment
  changes.
- `POST /data/refresh` refreshes data, not configuration.
- The client can start before the server is ready and reconnects lazily.
- Use fixture mode for tests and UI work; use S3 mode when validating actual
  schemas and production-scale payload behavior.
- Dashboard selections live in URLs. There is no session or saved-view store.
