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

"""Module defining LimitHandler class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .discrete_interval import DiscreteInterval
from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth
from .load_rounding import LoadRounding


@dataclass
class LimitHandler:
    """FIXME"""

    rounding: LoadRounding
    """FIXME"""
    debug: Callable[[str], None]
    """FIXME"""
    # Derived.
    min_load: DiscreteLoad = None
    """FIXME"""
    max_load: DiscreteLoad = None
    """FIXME"""

    def __post_init__(self):
        """FIXME"""
        from_float = DiscreteLoad.float_conver(rounding=self.rounding)
        self.min_load = from_float(self.rounding.min_load)
        self.max_load = from_float(self.rounding.max_load)

    def handle(
        self,
        load: DiscreteLoad,
        width_goal: DiscreteWidth,
        clo: Optional[DiscreteLoad],
        chi: Optional[DiscreteLoad],
    ) -> Optional[DiscreteLoad]:
        """Return new intended load after considering limits and bounds.

        Not only we want to avoid measuring outside minmax interval,
        we also want to avoid measuring too close to known limits and bounds.
        We either round or return None, depending on hints from bound loads.

        When rounding away from hard limits, we may end up being
        too close to an already measured bound.
        In this case, pick a midpoint between the bound and the limit.
        The caller should have chosen (unrounded) load far enough from bounds.

        The last two arguments are just loads (not full measurement result)
        to allow callers to exclude some load without measuring them.
        As a convenience, full results are also supported,
        so that callers do not need to care about None when extracting load.

        :param load: Intended load candidate from select_load.
        :param width_goal: Relative width goal, considered narrow enough.
        :param clo: Intended load of current tightest lower bound.
        :param chi: Intended load of current tightest upper bound.
        :type load: Optional[DiscreteLoad]
        :type width_goal: DiscreteWidth
        :type clo: Optional[Union[DiscreteLoad, ComparableMeasurementResult]]
        :type chi: Optional[Union[DiscreteLoad, ComparableMeasurementResult]]
        :return: Adjusted load to measure at, or None if narrow enough.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If unsupported corner case is detected.
        """
        if not load:
            raise RuntimeError("Got None load to handle.")
        load = load.rounded_down()
        min_load, max_load = self.min_load, self.max_load
        if clo and not clo.is_round:
            raise RuntimeError(f"Clo {clo} should have been round.")
        if chi and not chi.is_round:
            raise RuntimeError(f"Chi {chi} should have been round.")
        if not clo and not chi:
            load = self._handle_load_with_excludes(
                load, width_goal, min_load, max_load, min_ex=False, max_ex=False
            )
            return load
        if not clo:
            if chi <= min_load:
                # Expected when hitting the min load.
                return None
            if load >= chi:
                # This can happen e.g. when mrr2 forward rate is rounded to mrr2.
                return None
            load = self._handle_load_with_excludes(
                load, width_goal, min_load, chi, min_ex=False, max_ex=True
            )
            return load
        if not chi:
            if clo >= max_load:
                raise RuntimeError("Lower load expected.")
            if load <= clo:
                raise RuntimeError("Higher load expected.")
            load = self._handle_load_with_excludes(
                load, width_goal, clo, max_load, min_ex=True, max_ex=False
            )
            return load
        if load <= clo:
            raise RuntimeError("Higher load expected.")
        if load >= chi:
            raise RuntimeError("Lower load expected.")
        load = self._handle_load_with_excludes(
            load, width_goal, clo, chi, min_ex=True, max_ex=True
        )
        return load

    def _handle_load_with_excludes(
        self,
        load: DiscreteLoad,
        width_goal: DiscreteWidth,
        minimum: DiscreteLoad,
        maximum: DiscreteLoad,
        min_ex: bool,
        max_ex: bool,
    ) -> Optional[DiscreteLoad]:
        """Round load if too close to limits, respecting exclusions.

        Here, round means first rounding to int value (see DiscreteLoad),
        then avoiding getting too close (less than width goal)
        to maximum or minimum.

        This is a reusable block.
        Limits may come from previous bounds or from hard load limits.
        When coming from bounds, rounding to that is not allowed.
        When coming from hard limits, rounding to the limit value
        is allowed in general (given by the setting the _ex flag).

        :param load: The candidate intended load before accounting for limits.
        :param width_goal: Relative width of area around the limits to avoid.
        :param minimum: The lower limit to round around.
        :param maximum: The upper limit to round around.
        :param min_ex: If false, rounding to the minimum is allowed.
        :param max_ex: If false, rounding to the maximum is allowed.
        :type load: DiscreteLoad
        :type width_goal: DiscreteWidth
        :type minimum: DiscreteLoad
        :type maximum: DiscreteLoad
        :type min_ex: bool
        :type max_ex: bool
        :returns: Adjusted load value, or None if narrow enough.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If internal inconsistency is detected.
        """
        if not minimum <= load <= maximum:
            raise RuntimeError("Please do not call with irrelevant load.")
        width = maximum - minimum
        if width_goal >= width:
            self.debug("Warning: Handling called with wide goal.")
            if not min_ex:
                self.debug("Minimum not excluded, rounding to it.")
                return minimum
            if not max_ex:
                self.debug("Maximum not excluded, rounding to it.")
                return maximum
            self.debug("Both limits excluded, narrow enough.")
            return None
        soft_min = minimum + width_goal
        soft_max = maximum - width_goal
        if soft_min > soft_max:
            self.debug("Whole interval is less than two goals.")
            middle = DiscreteInterval(minimum, maximum).middle(width_goal)
            soft_min = soft_max = middle
        if load < soft_min:
            if min_ex:
                self.debug("Min excluded, rounding to soft min.")
                return soft_min
            self.debug("Min not excluded, rounding to minimum.")
            return minimum
        if load > soft_max:
            if max_ex:
                self.debug("Max excluded, rounding to soft max.")
                return soft_max
            self.debug("Max not excluded, rounding to maximum.")
            return maximum
        # Far enough from limits, no additional rounding is needed.
        return load
