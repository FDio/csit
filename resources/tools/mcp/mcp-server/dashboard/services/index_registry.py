"""Generation-aware ownership for dashboard semantic indexes."""

from __future__ import annotations

from typing import Any

from .comparison import ComparisonService
from .coverage import CoverageService
from .iterative import IterativeService
from .memory import component_memory_payload
from .statistics import StatisticsService
from .trending import TrendingService


class DerivedIndexRegistry:
    """Own all lazily built semantic indexes for the active cache generation."""

    def __init__(self) -> None:
        self.trending = TrendingService()
        self.iterative = IterativeService()
        self.coverage = CoverageService()
        self.comparison = ComparisonService()
        self.statistics = StatisticsService()

    def clear(self) -> None:
        """Release every derived index after a cache generation change."""

        for service in self._services().values():
            service.clear()

    def memory_snapshot(self) -> dict[str, Any]:
        """Return estimated retained memory for all derived indexes."""

        return component_memory_payload(**{
            name: service.memory_usage_bytes()
            for name, service in self._services().items()
        })

    def _services(self) -> dict[str, Any]:
        return {
            "trending": self.trending,
            "iterative": self.iterative,
            "coverage": self.coverage,
            "comparison": self.comparison,
            "statistics": self.statistics,
        }
