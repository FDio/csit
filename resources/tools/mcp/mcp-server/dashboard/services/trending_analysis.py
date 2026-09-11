"""Jumpavg-backed trend and anomaly analysis for semantic CSIT series."""

from __future__ import annotations

import math
from importlib.metadata import version
from typing import Any

import pandas as pd
from jumpavg import classify


ANALYSIS_METRICS = ("throughput", "bandwidth", "latency")
METRIC_DIRECTIONS = {
    "throughput": "higher",
    "bandwidth": "higher",
    "latency": "lower",
}
ANALYSIS_ENGINE = "jumpavg"
ANALYSIS_VERSION = version(ANALYSIS_ENGINE)


def analyze_trending_points(
        points: pd.DataFrame,
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Decorate semantic points with full-history jumpavg classifications."""

    analyzed = points.copy()
    for metric in ANALYSIS_METRICS:
        analyzed[f"{metric}_analysis"] = pd.Series(
            [None] * len(analyzed), index=analyzed.index, dtype="object",
        )

    metadata: dict[str, Any] = {
        "engine": ANALYSIS_ENGINE,
        "version": ANALYSIS_VERSION,
        "classified_series_metrics": 0,
        "skipped_series_metrics": 0,
        "errors": [],
    }
    if analyzed.empty or "series_id" not in analyzed.columns:
        return analyzed, metadata

    for series_id, series_points in analyzed.groupby(
            "series_id", sort=False, dropna=False,
        ):
        for metric in ANALYSIS_METRICS:
            value_column = f"{metric}_value"
            unit_column = f"{metric}_unit"
            if value_column not in series_points.columns:
                continue
            candidates = _metric_candidates(
                series_points, value_column=value_column,
                unit_column=unit_column,
            )
            for unit, unit_points in candidates.groupby(
                    "_analysis_unit", sort=False, dropna=False,
                ):
                unit_points = _sort_points(unit_points)
                try:
                    group_list = classify(unit_points["_analysis_value"].tolist())
                    decorations = _group_decorations(
                        group_list,
                        preferred_direction=METRIC_DIRECTIONS[metric],
                    )
                    if len(decorations) != len(unit_points):
                        raise ValueError(
                            "jumpavg returned a classification of unexpected length"
                        )
                except Exception as err:  # Keep data available if jumpavg rejects a sequence.
                    metadata["skipped_series_metrics"] += 1
                    metadata["errors"].append({
                        "series_id": str(series_id),
                        "metric": metric,
                        "unit": None if pd.isna(unit) else str(unit),
                        "message": str(err),
                    })
                    continue

                analysis_column = f"{metric}_analysis"
                for row_index, decoration in zip(
                        unit_points.index, decorations, strict=True,
                    ):
                    analyzed.at[row_index, analysis_column] = decoration
                metadata["classified_series_metrics"] += 1

    return analyzed, metadata


def _metric_candidates(
        points: pd.DataFrame,
        *,
        value_column: str,
        unit_column: str,
    ) -> pd.DataFrame:
    candidates = points.copy()
    candidates["_analysis_value"] = candidates[value_column].map(_finite_float)
    candidates = candidates.loc[candidates["_analysis_value"].notna()].copy()
    if candidates.empty:
        return candidates.assign(_analysis_unit=pd.Series(dtype="object"))
    if unit_column in candidates.columns:
        candidates["_analysis_unit"] = candidates[unit_column].map(_unit)
    else:
        candidates["_analysis_unit"] = None
    return candidates


def _sort_points(points: pd.DataFrame) -> pd.DataFrame:
    ordered = points.copy()
    ordered["_analysis_time"] = pd.to_datetime(
        ordered.get("start_time"), errors="coerce", utc=True,
    )
    ordered["_analysis_build"] = pd.to_numeric(
        ordered.get("build"), errors="coerce",
    )
    ordered["_analysis_order"] = range(len(ordered))
    return ordered.sort_values(
        ["_analysis_time", "_analysis_build", "_analysis_order"],
        kind="stable",
        na_position="last",
    )


def _group_decorations(
        group_list: Any,
        *,
        preferred_direction: str,
    ) -> list[dict[str, Any]]:
    decorations: list[dict[str, Any]] = []
    for group in group_list:
        trend = _finite_float(group.stats.avg)
        stdev = _finite_float(group.stats.stdev)
        if trend is None or stdev is None:
            raise ValueError("jumpavg returned non-finite trend statistics")
        classification = _performance_classification(
            str(group.comment or "normal"),
            preferred_direction=preferred_direction,
        )
        for offset in range(len(group)):
            decorations.append({
                "trend": trend,
                "stdev": stdev,
                "classification": classification if offset == 0 else "normal",
            })
    return decorations


def _performance_classification(
        classification: str,
        *,
        preferred_direction: str,
    ) -> str:
    """Translate JumpAvg's numeric direction into performance direction."""

    if preferred_direction == "lower":
        return {
            "progression": "regression",
            "regression": "progression",
        }.get(classification, classification)
    return classification


def _finite_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _unit(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    normalized = str(value).strip()
    return normalized or None
