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

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .criteria import Criteria
from .criterion import Criterion
from .discrete_load import DiscreteLoad
from .discrete_interval import DiscreteInterval
from .load_stat import LoadStat

from robot.api import logger


MaybeLoad = Optional[LoadStat]


@dataclass
class MeasurementDatabase:
    """Structure holding measurement results for multiple durations.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.
    The replacement logic is benevolent both for higher loads
    (where effective loss ratio hides lucky long duration results),
    and for small loads (overridden ratio hides lucky short duration results).

    The constructor uses shallow copy, so users should not edit
    the measurement results afterwards.
    """

    criteria: Criteria
    """FIXME"""
    load_to_stat: Dict[int, LoadStat] = None
    """FIXME"""

    def __post_init__(self) -> None:
        """Store (shallow copy of) measurement results and normalize them."""
        if not self.load_to_stat:
            self.load_to_stat = dict()
        self._normalize()

    def _normalize(self) -> None:
        """Sort, remove obsoleted results, set effective and overridden ratios.

        MLRsearch algorithm needs several assumptions to ensure convergence,
        but real results may violate those assumptions.
        The main anomaly to deal with is when a measurement at higher load
        results in smaller loss ratio than at lower load.

        The normalization here restores the assumptions
        by selectively removing old measurement results,
        or overriding some loss ratios to safe "conservative" values.

        There are three specific situations which need to be addressed:

        1. If there are two trial measurements done at exactly the same
        intended load. In that case, the shorter duration one
        has no purpose, so is removed from database.

        2. If a longer duration trial has smaller loss rate than
        a shorter duration trial at lower load. In this case, the shorter
        duration can still become useful (e.g. when the longer gets deleted
        due to point 1 later), but its loss rate needs to be hidden.
        That is done by setting its overridden loss rate.

        3. If the same duration trial (other cases are handled
        by previous points) at lower load has higher loss rate.
        In this case, it is the higher load result that is deemed "lucky",
        so its effective loss ratio is increased.

        Keeping the list of results sorted allows all the points to be applied
        quickly by iterating in the correct direction.
        """
        self.load_to_stat = dict(sorted(self.load_to_stat.items()))

    def update(self, load_stat: LoadStat) -> None:
        """Add measurement and normalize.

        :param measurement: Measurement result to add to the database.
        :type measurement: MeasurementResult
        """
        self.load_to_stat[int(load_stat)] = load_stat
        self._normalize()

    def stat_for(self, load: DiscreteLoad, trial_duration: float):
        """FIXME"""
        int_load = int(load)
        if int_load in self.load_to_stat:
            stat = self.load_to_stat[int_load]
            if stat.intended_duration >= trial_duration:
                return stat
        return LoadStat.new_empty(load, trial_duration, self.criteria)

    def get_valid_bounds(
        self, criterion, min_duration
    ) -> Tuple[MaybeLoad, MaybeLoad, MaybeLoad, MaybeLoad]:
        """Return None or a valid measurement for two tightest bounds.

        Measurement results with smaller duration are ignored.

        The validity of a measurement to act as a bound is determined
        by comparing the argument ratio with measurement's effective loss ratio.

        Both lower and upper bounds are returned, both tightest and second
        tightest. If some value is not available, None is returned instead.

        :param ratio: Target ratio, valid has to be lower or equal.
        :param min_duration: Consider results with at least this duration [s].
        :type ratio: float
        :type min_duration: float
        :returns: Tightest lower bound, tightest upper bound,
            second tightest lower bound, second tightest upper bound.
        :rtype: 4-tuple of Optional[ComparableMeasurementResult]
        """
        logger.debug(f"gvb starting for d {min_duration} c {criterion}")
        lower_1, upper_1, lower_2, upper_2 = None, None, None, None
        for load_stat in self.load_to_stat.values():
            logger.debug(f"gvb looking at {load_stat}")
            if load_stat.intended_duration < min_duration:
                logger.debug("gvb skipping, too short trials")
                continue
            opt, pes = load_stat.satisfies(criterion, min_duration)
            if opt != pes:
                logger.debug("gvb skipping as not enough trials to decide")
                continue
            if not opt:
                if upper_1 is None:
                    upper_1 = load_stat
                    logger.debug("gvb setting as upper_1")
                    continue
                upper_2 = load_stat
                logger.debug("gvb upper_2, done")
                break
            logger.debug("gvb using as new tightest lower")
            lower_1, lower_2 = load_stat, lower_1
        return lower_1, upper_1, lower_2, upper_2

    def get_intervals(self) -> Dict[Criterion, DiscreteInterval]:
        """Return list of intervals for given ratios, at the duration.

        This assumes no trial had larger duration.

        Attempt to construct valid intervals. If a valid bound is missing,
        use smallest/biggest intended_load for lower/upper bound.
        This can result in degenerate intervals,
        but is expected e.g. if max load has zero loss.

        :param ratio_list: Ratios to create intervals for.
        :type ratio_list: Iterable[float]
        :returns: List of intervals.
        :rtype: List[DiscreteInterval]
        """
        ret_dict = dict()
        for criterion in self.criteria:
            bounds = self.get_valid_bounds(
                criterion=criterion,
                min_duration=criterion.trials_duration,
            )
            lower_bound, upper_bound, _, _ = bounds
            if lower_bound is None:
                lower_bound = list(self.load_to_stat.values())[0].discrete_load
            if upper_bound is None:
                upper_bound = list(self.load_to_stat.values())[-1].discrete_load
            ret_dict[criterion] = DiscreteInterval(lower_bound, upper_bound)
        return ret_dict
