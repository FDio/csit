"""Custom HTTP route registration for the CSIT MCP server."""

from fastapi import Request
from fastapi.responses import JSONResponse

from .services.data_cache import DataCacheService


def register_routes(mcp, data_cache: DataCacheService) -> None:
    """Register custom HTTP routes on the FastMCP app."""

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        """Return a JSON health response for service readiness checks."""

        return JSONResponse(
            {"status": "healthy", "service": "mcp-server"}, status_code=200
        )

    @mcp.custom_route("/ready", methods=["GET"])
    async def readiness_check(request: Request) -> JSONResponse:
        """Return data readiness status for service dependency checks."""

        status_code = 200 if data_cache.is_serving_ready else 503
        return JSONResponse(
            {
                "service": "mcp-server",
                "data": data_cache.status_snapshot(),
            },
            status_code=status_code
        )

    @mcp.custom_route("/data/refresh", methods=["POST"])
    async def refresh_data(request: Request) -> JSONResponse:
        """Start a background data refresh if one is not already running."""

        if data_cache.start_refresh():
            return JSONResponse(
                {
                    "status": "refresh_started",
                    "service": "mcp-server",
                    "data": data_cache.status_snapshot(),
                },
                status_code=202
            )

        return JSONResponse(
            {
                "status": "refresh_in_progress",
                "service": "mcp-server",
                "data": data_cache.status_snapshot(),
            },
            status_code=409
        )
