import asyncio
import sys
import unittest

from fastapi.middleware.cors import CORSMiddleware

from dashboard.data.data import Data
from dashboard.services.data_cache import DataCacheService
from dashboard.services.lifecycle import make_data_cache_lifespan

from tests.test_data_cache import SlowDataReader, make_settings


class FakeLifecycleCache:
    def __init__(self, refresh_interval_seconds=0):
        self.refresh_interval_seconds = refresh_interval_seconds
        self.starts = []
        self.shutdown_called = False
        self.snapshot_enabled = False

    def start_refresh(self, started_by="manual"):
        self.starts.append(started_by)
        return True

    async def shutdown(self):
        self.shutdown_called = True


class FakeSnapshotLifecycleCache(FakeLifecycleCache):
    def __init__(self):
        super().__init__()
        self.snapshot_enabled = True
        self.restored = False

    def restore_snapshot(self):
        self.restored = True
        return True


class DataLifecycleTests(unittest.TestCase):
    def test_lifespan_restores_snapshot_before_remote_refresh(self):
        async def run_lifespan():
            cache = FakeSnapshotLifecycleCache()
            lifespan = make_data_cache_lifespan(cache)

            async with lifespan(None):
                for _ in range(20):
                    if cache.starts:
                        break
                    await asyncio.sleep(0.005)
                self.assertTrue(cache.restored)
                self.assertEqual(cache.starts, ["startup"])

        asyncio.run(run_lifespan())

    def test_lifespan_starts_and_stops_refresh(self):
        async def run_lifespan():
            cache = FakeLifecycleCache()
            lifespan = make_data_cache_lifespan(cache)

            async with lifespan(None):
                self.assertEqual(cache.starts, ["startup"])
                self.assertFalse(cache.shutdown_called)

            self.assertTrue(cache.shutdown_called)

        asyncio.run(run_lifespan())

    def test_lifespan_runs_scheduled_refresh_when_enabled(self):
        async def run_lifespan():
            cache = FakeLifecycleCache(refresh_interval_seconds=0.01)
            lifespan = make_data_cache_lifespan(cache)

            async with lifespan(None):
                for _ in range(20):
                    if "scheduled" in cache.starts:
                        break
                    await asyncio.sleep(0.005)

                self.assertEqual(cache.starts[0], "startup")
                self.assertIn("scheduled", cache.starts)

            self.assertTrue(cache.shutdown_called)

        asyncio.run(run_lifespan())

    def test_lifespan_schedules_loading_without_blocking_context_entry(self):
        async def run_lifespan():
            cache = DataCacheService(
                settings=make_settings(),
                data_reader_cls=SlowDataReader,
            )
            lifespan = make_data_cache_lifespan(cache)

            async with lifespan(None):
                self.assertEqual(cache.status, "loading")
                while cache.is_loading:
                    await asyncio.sleep(0.01)
                self.assertEqual(cache.status, "ready")
                self.assertEqual(
                    cache.status_snapshot()["last_refresh_started_by"],
                    "startup",
                )

            self.assertEqual(cache.status, "ready")

        asyncio.run(run_lifespan())

    def test_importing_server_app_does_not_read_data(self):
        original_read_all_data = Data.read_all_data
        calls = []

        def fail_if_called(self, days=None):
            calls.append(days)
            raise AssertionError("importing server.app must not load data")

        Data.read_all_data = fail_if_called
        sys.modules.pop("server", None)
        try:
            import server

            self.assertEqual(server.app.title, "CSIT FastAPI server")
            self.assertEqual(calls, [])
            cors_middleware = next(
                item for item in server.app.user_middleware
                if item.cls is CORSMiddleware
            )
            self.assertEqual(cors_middleware.kwargs["allow_origins"], ["*"])
        finally:
            Data.read_all_data = original_read_all_data


if __name__ == "__main__":
    unittest.main()
