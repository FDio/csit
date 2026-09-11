"""Print repeatable cache and semantic-index memory checkpoints as JSON."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import resource
import statistics
import sys
from time import perf_counter

import pyarrow as pa

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dashboard.services.data_cache import DataCacheService
from dashboard.services.index_registry import DerivedIndexRegistry
from dashboard.services.observability import (
    cgroup_memory_status,
    process_rss_bytes,
)
from dashboard.settings import get_settings


def checkpoint(name, cache, indexes, started):
    status = cache.status_snapshot()
    return {
        "checkpoint": name,
        "elapsed_seconds": round(perf_counter() - started, 3),
        "rss_bytes": process_rss_bytes(),
        "peak_rss_bytes": _peak_rss_bytes(),
        "arrow_allocated_bytes": pa.total_allocated_bytes(),
        "cgroup": cgroup_memory_status(),
        "cache": status["memory"]["cache"],
        "derived_indexes": indexes.memory_snapshot(),
        "row_counts": status["row_counts"],
    }


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _latency_summary(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)
    p95_index = max(
        0,
        min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1),
    )
    return {
        "p50_ms": round(statistics.median(ordered) * 1000, 3),
        "p95_ms": round(ordered[p95_index] * 1000, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fixture", "s3"), default="fixture")
    parser.add_argument("--days", type=int, default=60)
    arguments = parser.parse_args()
    environment = dict(os.environ)
    environment["CSIT_DATA_MODE"] = arguments.mode
    environment["CSIT_TIME_PERIOD"] = str(arguments.days)
    settings = get_settings(environment)
    cache = DataCacheService(settings=settings)
    indexes = DerivedIndexRegistry()
    cache.register_generation_listener(indexes.clear)
    cache.register_memory_reporter("derived_indexes", indexes.memory_snapshot)
    started = perf_counter()
    results = [checkpoint("startup", cache, indexes, started)]
    cache.load(started_by="benchmark")
    results.append(checkpoint("cache_loaded", cache, indexes, started))

    status = cache.status_snapshot()
    indexes.statistics.enriched_data(
        cache.data["statistics"], cache.data["trending"], status,
    )
    indexes.trending.catalog_payload(cache.data["trending"], status)
    indexes.iterative.catalog_payload(cache.data["iterative"], status)
    indexes.coverage.catalog_payload(cache.data["coverage"], status)
    indexes.comparison.catalog_payload(cache.data["iterative"], status)
    warm_checkpoint = checkpoint("indexes_warm", cache, indexes, started)
    timings: dict[str, list[float]] = {
        "statistics": [], "trending": [], "iterative": [],
        "coverage": [], "comparison": [],
    }
    callbacks = {
        "statistics": lambda: indexes.statistics.enriched_data(
            cache.data["statistics"], cache.data["trending"], status,
        ),
        "trending": lambda: indexes.trending.catalog_payload(
            cache.data["trending"], status,
        ),
        "iterative": lambda: indexes.iterative.catalog_payload(
            cache.data["iterative"], status,
        ),
        "coverage": lambda: indexes.coverage.catalog_payload(
            cache.data["coverage"], status,
        ),
        "comparison": lambda: indexes.comparison.catalog_payload(
            cache.data["iterative"], status,
        ),
    }
    for name, callback in callbacks.items():
        for _ in range(10):
            call_started = perf_counter()
            callback()
            timings[name].append(perf_counter() - call_started)
    warm_checkpoint["warm_latency"] = {
        name: _latency_summary(samples) for name, samples in timings.items()
    }
    results.append(warm_checkpoint)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
