"""Memory accounting and compact dataframe representation helpers."""

from __future__ import annotations

from collections.abc import Mapping
import sys
from typing import Any, Iterable

import pandas as pd


def dataframe_memory_bytes(data: pd.DataFrame) -> int:
    """Return the best available owned memory estimate for one dataframe."""

    if not isinstance(data, pd.DataFrame) or data.empty and not len(data.columns):
        return 0
    try:
        return int(data.memory_usage(index=True, deep=True).sum())
    except (TypeError, ValueError):
        return int(data.memory_usage(index=True).sum())


def dataframe_mapping_memory(
        frames: Mapping[str, pd.DataFrame],
    ) -> dict[str, Any]:
    """Return per-frame and total memory estimates."""

    datasets = {
        str(name): dataframe_memory_bytes(frame)
        for name, frame in frames.items()
    }
    return {"total_bytes": sum(datasets.values()), "datasets": datasets}


def compact_semantic_frame(
        data: pd.DataFrame,
        *,
        categorical_columns: Iterable[str] = (),
    ) -> pd.DataFrame:
    """Dictionary-encode repeated semantic dimensions in an owned dataframe."""

    if data.empty:
        return data
    for column in categorical_columns:
        if column not in data.columns:
            continue
        series = data[column]
        try:
            candidate = series.astype("category")
            candidate_size = candidate.memory_usage(index=False, deep=True)
            source_size = series.memory_usage(index=False, deep=True)
            if candidate_size < source_size:
                data[column] = candidate
        except (TypeError, ValueError):
            continue
    return data


def component_memory_payload(**components: Any) -> dict[str, Any]:
    """Return a normalized component-memory status block."""

    normalized: dict[str, Any] = {}
    total = 0
    for name, value in components.items():
        if isinstance(value, pd.DataFrame):
            size = dataframe_memory_bytes(value)
            normalized[name] = size
            total += size
        elif isinstance(value, Mapping):
            item = dataframe_mapping_memory(value)
            normalized[name] = item
            total += int(item["total_bytes"])
        elif isinstance(value, int):
            normalized[name] = value
            total += value
    return {"estimated_bytes": total, "components": normalized}


def estimated_python_heap_bytes(value: Any) -> int:
    """Estimate retained Python heap for JSON-like cache values."""

    seen: set[int] = set()

    def size(item: Any) -> int:
        item_id = id(item)
        if item_id in seen:
            return 0
        seen.add(item_id)
        total = sys.getsizeof(item)
        if isinstance(item, Mapping):
            total += sum(size(key) + size(child) for key, child in item.items())
        elif isinstance(item, (list, tuple, set, frozenset)):
            total += sum(size(child) for child in item)
        return total

    return size(value)
