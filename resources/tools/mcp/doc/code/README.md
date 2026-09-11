# CSIT MCP Source Code Guide

This guide is for a backend or full-stack engineer joining CSIT MCP. It
documents the implemented code, not roadmap proposals.

CSIT MCP has two Python 3.13 services:

- [`mcp-server`](../../mcp-server/) loads and analyzes FD.io CSIT data, exposes
  29 read-only MCP tools, and serves operational HTTP routes.
- [`mcp-client`](../../mcp-client/) maintains a resilient MCP connection and
  renders the five-tab CSIT Dashboard.

## Start Here

1. Read [Architecture](architecture.md) for boundaries and request flows.
2. Follow [Setup](setup.md) and start fixture mode.
3. Use [APIs and interfaces](api.md) for MCP and HTTP contracts.
4. Read [Data model](data-model.md) before changing cache or analysis code.
5. Use [Testing](testing.md) and [Operations](operations.md) while developing.

## Guide

| Document | Contents |
| --- | --- |
| [Architecture](architecture.md) | Services, modules, data lifecycle, and dashboard flow. |
| [Setup](setup.md) | Tools, installation, local runs, and common workflows. |
| [APIs](api.md) | 29 MCP tools, resources, server routes, client routes, pagination, and errors. |
| [Data model](data-model.md) | Dataframes, normalization, telemetry, semantic indexes, and statistics. |
| [Configuration](configuration.md) | Server, client, container, CORS, and AWS settings. |
| [Integration](integration.md) | Codex, Claude Code, Claude Desktop, and discovery-first usage. |
| [Testing](testing.md) | Test suites, commands, categories, and limits. |
| [Deployment](deployment.md) | Docker images, Compose, identity, credentials, and process model. |
| [Operations](operations.md) | Health, readiness, refreshes, logging, payload safety, and troubleshooting. |
| [Open questions](open-questions.md) | Facts that cannot be established from this repository. |

## Runtime Summary

| Surface | Address | Source |
| --- | --- | --- |
| MCP | `http://localhost:8000/mcp` | [`dashboard/__init__.py`](../../mcp-server/dashboard/__init__.py) |
| Server liveness | `GET http://localhost:8000/health` | [`routes.py`](../../mcp-server/dashboard/routes.py) |
| Server readiness | `GET http://localhost:8000/ready` | [`routes.py`](../../mcp-server/dashboard/routes.py) |
| Dashboard | `GET http://localhost:7860/` | [`app.py`](../../mcp-client/app.py) |
| Client liveness | `GET http://localhost:7860/health` | [`app.py`](../../mcp-client/app.py) |

Fixture mode is the fastest no-AWS development path:

```sh
docker network create mcp
docker compose -f docker-compose.yaml -f docker-compose.fixture.yaml up --build
```

## Technology

- FastAPI and FastMCP on the server.
- Starlette and Uvicorn on the client.
- Pandas, NumPy, PyArrow, and AWS SDK tooling for result data.
- JumpAvg 0.4.2 for Trending group-change analysis.
- hdrhistogram 0.10.7 for Coverage latency percentiles.
- XlsxWriter for client XLSX exports.
- Standard-library `unittest`; no frontend framework or build tool.

## Source Reading Order

Server:

1. [`server.py`](../../mcp-server/server.py)
2. [`dashboard/__init__.py`](../../mcp-server/dashboard/__init__.py)
3. [`services/data_cache.py`](../../mcp-server/dashboard/services/data_cache.py)
4. [`services/refresh_worker.py`](../../mcp-server/dashboard/services/refresh_worker.py)
   and [`services/index_registry.py`](../../mcp-server/dashboard/services/index_registry.py)
5. [`mcp_tools.py`](../../mcp-server/dashboard/mcp_tools.py)
6. Dataset-specific modules under
   [`services/`](../../mcp-server/dashboard/services/)

Client:

1. [`app.py`](../../mcp-client/app.py)
2. [`dashboard.py`](../../mcp-client/dashboard.py)
3. Dataset renderers such as
   [`trending_dashboard.py`](../../mcp-client/trending_dashboard.py)
4. [`templates/`](../../mcp-client/templates/) and
   [`static/`](../../mcp-client/static/)
5. Export builders such as
   [`comparison_export.py`](../../mcp-client/comparison_export.py)
