"""Shared admission control for memory-intensive dataframe queries."""

from __future__ import annotations

import threading
from time import perf_counter
from typing import Any, Callable

from .observability import cgroup_memory_status, log_event


class QueryAdmissionController:
    """Serialize large in-process queries and reject work under pressure."""

    def __init__(self, settings) -> None:
        self._settings = settings
        self._semaphore = threading.BoundedSemaphore(
            settings.query_max_concurrent
        )
        self._lock = threading.Lock()
        self._active = 0

    def run(
            self,
            *,
            tool: str,
            dataset: str,
            row_count: int,
            callback: Callable[[], dict[str, Any]],
        ) -> dict[str, Any]:
        """Run a heavy query under bounded concurrency and memory pressure."""

        if row_count < self._settings.query_heavy_row_threshold:
            return callback()
        admission_started = perf_counter()
        memory = cgroup_memory_status()
        used_percent = memory.get("used_percent")
        if (
            used_percent is not None and
            used_percent >= self._settings.query_memory_soft_limit_percent
        ):
            return self._rejected(
                tool=tool,
                dataset=dataset,
                reason="memory_pressure",
                memory=memory,
                queue_duration_seconds=0.0,
            )
        acquired = self._semaphore.acquire(
            timeout=self._settings.query_queue_timeout_seconds
        )
        if not acquired:
            return self._rejected(
                tool=tool,
                dataset=dataset,
                reason="concurrency_limit",
                memory=memory,
                queue_duration_seconds=round(
                    perf_counter() - admission_started, 3
                ),
            )
        queue_duration = round(perf_counter() - admission_started, 3)
        started = perf_counter()
        with self._lock:
            self._active += 1
            active = self._active
        log_event(
            "heavy_query_started",
            tool=tool,
            dataset=dataset,
            row_count=row_count,
            active_queries=active,
            queue_duration_seconds=queue_duration,
            memory=memory,
        )
        outcome = "exception"
        try:
            payload = callback()
            outcome = str(payload.get("error") or "success")
            return payload
        finally:
            with self._lock:
                self._active -= 1
                active = self._active
            self._semaphore.release()
            log_event(
                "heavy_query_completed",
                tool=tool,
                dataset=dataset,
                row_count=row_count,
                active_queries=active,
                outcome=outcome,
                duration_seconds=round(perf_counter() - started, 3),
                memory=cgroup_memory_status(),
            )

    def status_snapshot(self) -> dict[str, Any]:
        with self._lock:
            active = self._active
        return {
            "active_queries": active,
            "max_concurrent": self._settings.query_max_concurrent,
            "queue_timeout_seconds": self._settings.query_queue_timeout_seconds,
            "heavy_row_threshold": self._settings.query_heavy_row_threshold,
            "memory_soft_limit_percent": (
                self._settings.query_memory_soft_limit_percent
            ),
            "memory": cgroup_memory_status(),
        }

    def _rejected(
            self,
            *,
            tool: str,
            dataset: str,
            reason: str,
            memory: dict[str, Any],
            queue_duration_seconds: float,
        ) -> dict[str, Any]:
        log_event(
            "heavy_query_rejected",
            tool=tool,
            dataset=dataset,
            reason=reason,
            active_queries=self.status_snapshot()["active_queries"],
            queue_duration_seconds=queue_duration_seconds,
            memory=memory,
        )
        return {
            "error": "server_busy",
            "message": (
                "The server is protecting the active cache from overlapping "
                "memory-intensive queries. Retry this request shortly."
            ),
            "reason": reason,
            "retry_after_seconds": 2,
            "dataset": dataset,
        }
