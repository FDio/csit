"""
Initialize CSIT FastMCP app.
"""

import logging

from .settings import get_settings


settings = get_settings()
_mcp = None
_mcp_app = None
_data_cache = None


def create_mcp_server():
    """Create and cache the configured FastMCP server objects."""

    global _mcp, _mcp_app, _data_cache

    if _mcp_app is not None:
        return _mcp, _mcp_app, _data_cache

    from fastmcp import FastMCP
    from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
    from fastmcp.server.middleware.timing import DetailedTimingMiddleware

    from .mcp_tools import register_mcp_tools
    from .routes import register_routes
    from .services.data_cache import DataCacheService
    from .services.lifecycle import make_data_cache_lifespan
    from .services.observability import cgroup_memory_status, log_event

    logging.basicConfig(
        format=settings.log_format,
        datefmt=settings.log_date_format,
        level=settings.log_level
    )
    for error in settings.validation_errors:
        logging.error(
            "Invalid configuration for %s=%r: %s",
            error["field"],
            error["value"],
            error["message"],
        )
    memory = cgroup_memory_status()
    log_event(
        "runtime_memory_startup",
        memory=memory,
        prior_oom_kill_count=memory.get("events", {}).get("oom_kill", 0),
    )

    _data_cache = DataCacheService(settings=settings)
    _mcp = FastMCP(
        name=settings.server_name,
        lifespan=make_data_cache_lifespan(_data_cache)
    )
    _mcp.enable(tags=set(settings.public_tags))
    _mcp.add_middleware(StructuredLoggingMiddleware())
    _mcp.add_middleware(DetailedTimingMiddleware())

    register_mcp_tools(mcp=_mcp, data_cache=_data_cache, settings=settings)
    register_routes(mcp=_mcp, data_cache=_data_cache)

    _mcp_app = _mcp.http_app(path=settings.mcp_path)

    return _mcp, _mcp_app, _data_cache


def __getattr__(name: str):
    """Lazily expose assembled FastMCP objects for package consumers."""

    if name == "mcp":
        mcp, _, _ = create_mcp_server()
        return mcp
    if name == "mcp_app":
        _, mcp_app, _ = create_mcp_server()
        return mcp_app
    if name == "data_cache":
        _, _, data_cache = create_mcp_server()
        return data_cache
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["mcp", "mcp_app", "data_cache", "settings", "create_mcp_server"]
