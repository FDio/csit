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
from typing import Dict, Tuple

from .discrete_load import DiscreteLoad
from .discrete_result import DiscreteResult
from .load_stats import LoadStats
from .relevant_bounds import RelevantBounds
from .target_spec import TargetSpec
from .trimmed_stat import TrimmedStat


@dataclass
class MeasurementDatabase:
    """Structure holding measurement results for multiple durations and loads.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.

    While TargetStats can decide when a single load is a lower bound (or upper),
    it does not deal with loss inversion (higher load with less load).

    This class introduces the concept of relevant bounds.
    Relevant upper bound is simply the lowest load classified as an upper bound.
    But relevant lower bound is only chosen from lower bound loads
    strictly smaller than the relevant upper bound.
    This way any higher loads with good results are ignored,
    so relevant bound give conservative estimate of SUT true performance.
    """

    targets: Tuple[TargetSpec] = None
    """Targets to track stats for."""
    load_to_stats: Dict[DiscreteLoad, LoadStats] = None
    """Mapping from loads to stats."""

    def __post_init__(self) -> None:
        """Check and sort initial values.

        If no stats yet, initialize empty ones.

        :raises ValueError: If there are no targets.
        """
        if not self.targets:
            raise ValueError(f"Database needs targets: {self.targets!r}")
        if not self.load_to_stats:
            self.load_to_stats = {}
        self._sort()

    def _sort(self) -> None:
        """Sort keys from low to high load."""
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

    def get_relevant_bounds(self, target: TargetSpec) -> RelevantBounds:
        """Return None or a valid trimmed stat, for the two relevant bounds.

        A load is valid only if both optimistic and pessimistic estimates agree.

        If some value is not available, None is returned instead.
        The returned stats are trimmed to the argument target.

        The implementation starts from low loads
        and the search stops at lowest upper bound,
        thus conforming to the conservative definition of relevant bounds.

        :param target: Target to classify loads when finding bounds.
        :type target: TargetSpec
        :returns: Relevant lower bound, relevant upper bound.
        :rtype: RelevantBounds
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
            lower_bound = TrimmedStat.for_target(lower_bound, target)
        if upper_bound:
            upper_bound = TrimmedStat.for_target(upper_bound, target)
        return RelevantBounds(clo=lower_bound, chi=upper_bound)
