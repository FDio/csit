# Copyright (c) 2023 Cisco and/or its affiliates.
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

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .discrete_load import DiscreteLoad
from .discrete_interval import DiscreteInterval
from .load_stats import LoadStats
from .target_spec import TargetSpec
from .discrete_result import DiscreteResult


@dataclass
class MeasurementDatabase:
    """Structure holding measurement results for multiple durations and loads.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.

    The constructor uses shallow copy, so users should not edit
    the measurement results afterwards.
    """

    targets: Tuple[TargetSpec] = None
    """Targets to track stats for."""
    load_to_stats: Dict[DiscreteLoad, LoadStats] = None
    """Mapping from loads to stats."""

    def __post_init__(self) -> None:
        """Store (shallow copy of) measurement results and normalize them.

        If no stats yet, initialize empty ones.

        :raises ValueError: If there are no targets.
        """
        if not self.targets:
            raise ValueError(f"Database needs targets: {self.targets!r}")
        if not self.load_to_stats:
            self.load_to_stats = {}
        self._sort()

    def _sort(self) -> None:
        """Sort keys from low to high load.."""
        self.load_to_stats = dict(sorted(self.load_to_stats.items()))

    def __getitem__(self, key: DiscreteLoad) -> LoadStats:
        """Allow access to stats as if self was load_to_stats.

        This also accepts LoadStats as key, so callers do not need
        to care about hashability.

        :param key: The load to get stats for.
        :type key: DiscreteLoad
        :returns: Stats for the given load.
        :rtype LoadStats:
        """
        return self.load_to_stats[key.hashable()]

    def add(self, result: DiscreteResult) -> None:
        """Incorporate given trial measurement result.

        :param result: Measurement result to add to the database.
        :type result: DiscreteResult
        """
        discrete_load = result.discrete_load.hashable()
        if not discrete_load.is_round:
            raise ValueError(f"Not round load: {discrete_load!r}")
        if discrete_load not in self.load_to_stats:
            self.load_to_stats[discrete_load] = LoadStats.new_empty(
                load=discrete_load,
                targets=self.targets,
            )
            self._sort()
        self.load_to_stats[discrete_load].add(result)

    def get_valid_bounds(
        self, target: TargetSpec
    ) -> Tuple[Optional[LoadStats], Optional[LoadStats]]:
        """Return None or a valid laod stats, for the two tightest bounds.

        A load is valid only if both optimistic and pessimistic estimates agree.

        Both lower and upper bounds are returned.
        If some value is not available, None is returned instead.
        The returned stats are trimmed to the argument target.

        :param target: Target to classify loads when finding bounds.
        :type target: TargetSpec
        :returns: Tightest lower bound, tightest upper bound.
        :rtype: Tuple[Optional[LoadStats], Optional[LoadStats]]
        """
        lower_bound, upper_bound = None, None
        for load_stats in self.load_to_stats.values():
            opt, pes = load_stats.estimates(target)
            if opt != pes:
                continue
            if not opt:
                upper_bound = load_stats
                break
            lower_bound = load_stats
        if lower_bound:
            lower_bound = lower_bound.trimmed_to_target(target)
        if upper_bound:
            upper_bound = upper_bound.trimmed_to_target(target)
        return lower_bound, upper_bound

    def get_interval(self, target: TargetSpec) -> DiscreteInterval:
        """Return interval for given target spec.

        Attempt to construct valid intervals. If a valid bound is missing,
        use smallest/biggest intended_load for lower/upper bound.
        This can result in degenerate intervals,
        but is expected e.g. if max load has zero loss.

        :param target: Which target should the returned interval describe.
        :type target: TargetSpec
        :returns: Interval of lower and upper bound for the target.
        :rtype: DiscreteInterval
        """
        bounds = self.get_valid_bounds(target=target)
        lower_bound, upper_bound = bounds
        if lower_bound is None:
            lower_bound = list(self.load_to_stats.values())[0]
        if upper_bound is None:
            upper_bound = list(self.load_to_stats.values())[-1]
        return DiscreteInterval(
            low_end=lower_bound.trimmed_to_target(target),
            high_end=upper_bound.trimmed_to_target(target),
        )
