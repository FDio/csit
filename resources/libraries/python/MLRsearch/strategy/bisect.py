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

"""Module defining BisectStrategy class."""


from dataclasses import dataclass
from typing import Optional, Tuple

from ..discrete_interval import DiscreteInterval
from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class BisectStrategy(StrategyBase):
    """Strategy to use when both bounds relevant to curent target are present.

    Primarily, this strategy is there to perform internal search.
    As powers of two are fiendly to binary search,
    this strategy relies on the splitting logic described in DiscreteInterval.

    The main reason why this class is so long is that a mere existence
    of a valid bound for the current target does not imply
    that bound is a good approximation of the final conditional throughput.
    The bound might become valid due to efforts of a strategy
    focusing on an entirely different search goal.

    On the other hand, initial bounds may be better approximations,
    but they also may be bad approximations (for example
    when SUT behavior strongly depends on trial duration).

    Based on comparison of existing current bounds to intial bounds,
    this strategy also mimics what would external search do
    (if the one current bound was missing and other initial bound was current).
    In case that load value is closer to appropriate inital bound
    (compared to how far the simple bisect between current bounds is),
    that load is nominated.

    It turns out those "conditional" external search nominations
    are quite different from unconditional ones,
    at least when it comes to handling limits
    and tracking when width expansion should be applied.
    That is why that logic is here
    and not in some generic external search class.
    """

    expand_on_clo: bool = False
    """If extending up, width should be expanded when load becomes clo."""
    expand_on_chi: bool = False
    """If extending down, width should be expanded when load becomes chi."""

    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate a load candidate between bounds or extending from them.

        The external search logic is offloaded into private methods.
        If they return a truthy load, that is returned from here as well.

        Only if the actual bisect is selected,
        the per-selector expander is limited to the (smaller) new width.

        :param bounds: Freshly updated bounds relevant for current target.
        :type bounds: RelevantBounds
        :returns: Two nones or candidate intended load and duration.
        :rtype: Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]
        """
        if not bounds.clo or bounds.clo >= self.handler.max_load:
            return None, None
        if not bounds.chi or bounds.chi <= self.handler.min_load:
            return None, None
        interval = DiscreteInterval(bounds.clo, bounds.chi)
        if interval.width_in_goals(self.target.discrete_width) <= 1.0:
            return None, None
        bisect_load = interval.middle(self.target.discrete_width)
        load, width = self._extend_lo(bounds, bisect_load)
        if load:
            self.expand_on_clo, self.expand_on_chi = False, True
            self.debug(f"Preferring to extend down: {load}")
            return load, width
        load, width = self._extend_hi(bounds, bisect_load)
        if load:
            self.expand_on_clo, self.expand_on_chi = True, False
            self.debug(f"Preferring to extend up: {load}")
            return load, width
        load = bisect_load
        if self.not_worth(bounds=bounds, load=load):
            return None, None
        self.expand_on_clo, self.expand_on_chi = False, False
        self.debug(f"Preferring to bisect: {load}")
        width_lo = DiscreteInterval(bounds.clo, load).discrete_width
        width_hi = DiscreteInterval(load, bounds.chi).discrete_width
        width = min(width_lo, width_hi)
        self.expander.limit(width)
        return load, width

    def _extend_lo(
        self, bounds: RelevantBounds, bisect_load: DiscreteLoad
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Compute load as if extending down, return it if preferred.

        :param bounds: Freshly updated bounds relevant for current target.
        :param bisect_load: Load when bisection is preferred.
        :type bounds: RelevantBounds
        :type bisect_load: DiscreteLoad
        :returns: Two nones or candidate intended load and duration.
        :rtype: Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]
        :raises RuntimeError: If an internal inconsistency is detected.
        """
        # TODO: Simplify all the conditions or explain them better.
        if not self.initial_upper_load:
            return None, None
        if bisect_load >= self.initial_upper_load:
            return None, None
        width = self.expander.get_width()
        load = bounds.chi - width
        load = self.handler.handle(
            load=load,
            width=self.target.discrete_width,
            clo=bounds.clo,
            chi=bounds.chi,
        )
        if not load:
            return None, None
        if load <= bisect_load:
            return None, None
        if load >= self.initial_upper_load:
            return None, None
        if self.not_worth(bounds=bounds, load=load):
            raise RuntimeError(f"Load not worth: {load}")
        return load, width

    def _extend_hi(
        self, bounds: RelevantBounds, bisect_load: DiscreteLoad
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Compute load as if extending up, return it if preferred.

        :param bounds: Freshly updated bounds relevant for current target.
        :param bisect_load: Load when bisection is preferred.
        :type bounds: RelevantBounds
        :type bisect_load: DiscreteLoad
        :returns: Two nones or candidate intended load and duration.
        :rtype: Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]
        :raises RuntimeError: If an internal inconsistency is detected.
        """
        # TODO: Simplify all the conditions or explain them better.
        if not self.initial_lower_load:
            return None, None
        if bisect_load <= self.initial_lower_load:
            return None, None
        width = self.expander.get_width()
        load = bounds.clo + width
        load = self.handler.handle(
            load=load,
            width=self.target.discrete_width,
            clo=bounds.clo,
            chi=bounds.chi,
        )
        if not load:
            return None, None
        if load >= bisect_load:
            return None, None
        if load <= self.initial_lower_load:
            return None, None
        if self.not_worth(bounds=bounds, load=load):
            raise RuntimeError(f"Load not worth: {load}")
        return load, width

    def won(self, bounds: RelevantBounds, load: DiscreteLoad) -> None:
        """Expand width when appropriate.

        :param bounds: Freshly updated bounds relevant for current target.
        :param load: The current load, so strategy does not need to remember.
        :type bounds: RelevantBounds
        :type load: DiscreteLoad
        """
        if self.expand_on_clo and load == bounds.clo:
            self.expander.expand()
        elif self.expand_on_chi and load == bounds.chi:
            self.expander.expand()
