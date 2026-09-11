"""Application lifecycle helpers for CSIT data services."""

import asyncio
from contextlib import asynccontextmanager, suppress

from .data_cache import DataCacheService


def make_data_cache_lifespan(data_cache: DataCacheService):
    """Create a FastMCP lifespan that starts background data loading."""

    @asynccontextmanager
    async def lifespan(server):
        scheduler_task = None
        data_cache.start_refresh(started_by="startup")
        if data_cache.refresh_interval_seconds > 0:
            scheduler_task = asyncio.create_task(
                _scheduled_refresh_loop(data_cache)
            )
        try:
            yield {"data_cache": data_cache}
        finally:
            if scheduler_task is not None:
                scheduler_task.cancel()
                with suppress(asyncio.CancelledError):
                    await scheduler_task
            await data_cache.shutdown()

    return lifespan


async def _scheduled_refresh_loop(data_cache: DataCacheService) -> None:
    """Run opt-in periodic refreshes until application shutdown."""

    while True:
        await asyncio.sleep(data_cache.refresh_interval_seconds)
        data_cache.start_refresh(started_by="scheduled")
