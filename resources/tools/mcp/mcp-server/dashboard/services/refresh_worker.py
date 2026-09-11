"""Disposable process used to build S3-backed cache generations."""

from __future__ import annotations

import multiprocessing
from pathlib import Path
from time import perf_counter
from typing import Any

from ..settings import AppSettings
from .observability import log_event


def run_cache_refresh_worker(
        settings: AppSettings,
        *,
        timeout_seconds: int,
    ) -> dict[str, Any]:
    """Build one snapshot outside the serving process."""

    context = multiprocessing.get_context("spawn")
    parent_connection, child_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=_worker_entry,
        args=(child_connection, settings),
        name="csit-cache-refresh",
        daemon=True,
    )
    started = perf_counter()
    process.start()
    child_connection.close()
    log_event("data_refresh_worker_started", worker_pid=process.pid)
    try:
        if not parent_connection.poll(max(timeout_seconds, 1)):
            _stop_process(process)
            return {
                "status": "timeout",
                "message": "Cache refresh worker exceeded its deadline.",
                "worker_pid": process.pid,
                "duration_seconds": round(perf_counter() - started, 3),
            }
        try:
            result = parent_connection.recv()
        except (EOFError, OSError) as err:
            result = {
                "status": "failed",
                "message": "Cache refresh worker exited without a result.",
                "error": repr(err),
            }
        process.join(timeout=5)
        if process.is_alive():
            _stop_process(process)
        result["worker_pid"] = process.pid
        result["worker_exit_code"] = process.exitcode
        result["duration_seconds"] = round(perf_counter() - started, 3)
        log_event("data_refresh_worker_completed", **result)
        return result
    finally:
        parent_connection.close()
        if process.is_alive():
            _stop_process(process)


def _worker_entry(connection, settings: AppSettings) -> None:
    """Load S3 data and atomically write the configured snapshot."""

    try:
        from .data_cache import DataCacheService

        service = DataCacheService(
            settings=settings,
            allow_refresh_worker=False,
        )
        service.load(started_by="worker")
        snapshot = service.status_snapshot()
        snapshot_path = Path(settings.cache_snapshot_path)
        if service.is_serving_ready and (snapshot_path / "manifest.json").is_file():
            result = {
                "status": "ready",
                "data_status": snapshot["status"],
                "row_counts": snapshot["row_counts"],
                "generation_id": snapshot["snapshot"]["generation_id"],
            }
        else:
            result = {
                "status": "failed",
                "message": snapshot.get("last_error") or (
                    "Cache refresh worker did not publish a snapshot."
                ),
                "data_status": snapshot.get("status"),
            }
    except BaseException as err:  # Parent always receives a bounded failure.
        result = {
            "status": "failed",
            "message": "Cache refresh worker failed.",
            "error": repr(err),
        }
    try:
        connection.send(result)
    finally:
        connection.close()


def _stop_process(process: multiprocessing.Process) -> None:
    process.terminate()
    process.join(timeout=2)
    if process.is_alive() and hasattr(process, "kill"):
        process.kill()
        process.join(timeout=2)
