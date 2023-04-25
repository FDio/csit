# Copyright (c) 2022 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module defining MeasurementDatabase class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .discrete_load import DiscreteLoad
from .discrete_interval import DiscreteInterval
from .load_stats import LoadStats
from .target_spec import TargetSpec
from .trial_measurement.measurement_result import MeasurementResult

MaybeLoad = Optional[LoadStats]


@dataclass
class MeasurementDatabase:
    """Structure holding measurement results for multiple durations.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.

    The constructor uses shallow copy, so users should not edit
    the measurement results afterwards.
    """

    target_specs: List[TargetSpec] = None
    """FIXME"""
    load_to_stats: Dict[DiscreteLoad, LoadStats] = None
    """FIXME"""

    def __post_init__(self) -> None:
        """Store (shallow copy of) measurement results and normalize them."""
        if not self.target_specs:
            raise ValueError(
                f"Database needs target specs: {self.target_specs!r}"
            )
        if not self.load_to_stats:
            self.load_to_stats = dict()
        self._sort()

    def _sort(self) -> None:
        """Sort."""
        self.load_to_stats = dict(sorted(self.load_to_stats.items()))

    def __getitem__(self, key: DiscreteLoad) -> LoadStats:
        """FIXME"""
        return self.load_to_stats[key.hashable()]

    def add(self, measurement: MeasurementResult) -> None:
        """Add measurement.

        :param measurement: Measurement result to add to the database.
        :type measurement: MeasurementResult
        """
        discrete_load = measurement.discrete_load.hashable()
        if not discrete_load.is_round:
            raise ValueError(f"Not round: {discrete_load!r}")
        if discrete_load not in self.load_to_stats:
            self.load_to_stats[discrete_load] = LoadStats.new_empty(
                load=discrete_load,
                specs=self.target_specs,
            )
            self._sort()
        self.load_to_stats[discrete_load].add(measurement)

    def get_valid_bounds(
        self, target_spec: TargetSpec
    ) -> Tuple[MaybeLoad, MaybeLoad]:
        """Return None or a valid measurement for tightest bounds.

        A load is valid only if both optimistic and pessimistic estimates agree.

        Both lower and upper bounds are returned.
        If some value is not available, None is returned instead.

        :param ratio: Target ratio, valid has to be lower or equal.
        :param min_duration: Consider results with at least this duration [s].
        :type ratio: float
        :type min_duration: float
        :returns: Tightest lower bound, tightest upper bound.
        :rtype: 2-tuple of Optional[ComparableMeasurementResult]
        """
        lower_bound, upper_bound = None, None
        for load_stats in self.load_to_stats.values():
            opt, pes = load_stats.satisfied(target_spec)
            if opt != pes:
                continue
            if not opt:
                upper_bound = load_stats
                break
            if upper_bound is None:
                lower_bound = load_stats
        return lower_bound, upper_bound

    def get_interval(self, target_spec: TargetSpec) -> DiscreteInterval:
        """Return interval for given target spec.

        Attempt to construct valid intervals. If a valid bound is missing,
        use smallest/biggest intended_load for lower/upper bound.
        This can result in degenerate intervals,
        but is expected e.g. if max load has zero loss.

        :param spec: FIXME
        :type spec: TargetSpec
        :returns: FIXME
        :rtype: DiscreteInterval
        """
        bounds = self.get_valid_bounds(target_spec=target_spec)
        lower_bound, upper_bound = bounds
        if lower_bound is None:
            lower_bound = list(self.load_to_stats.values())[0]
        if upper_bound is None:
            upper_bound = list(self.load_to_stats.values())[-1]
        return DiscreteInterval(lower_bound, upper_bound)
