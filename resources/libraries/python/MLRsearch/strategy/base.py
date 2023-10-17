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

"""Module defining StrategyBase class."""


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from ..discrete_interval import DiscreteInterval
from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..expander import TargetedExpander
from ..limit_handler import LimitHandler
from ..relevant_bounds import RelevantBounds
from ..target_spec import TargetSpec


@dataclass
class StrategyBase(ABC):
    """Abstract class encompassing data common to most strategies.

    A strategy is one piece of logic a selector may use
    when nominating a candidate according to its current target.

    The two initial bound arguments may not be bounds at all.
    For initial targets, the two values are usually mrr and mrr2.
    For subsequent targets, the initial values are usually
    the relevant bounds of the preceding target,
    but one of them may be None if hitting min or max load.

    The initial values are mainly used as stable alternatives
    to relevant bounds of preceding target,
    because those bounds may have been unpredictably altered
    by nominations from unrelated search goals.
    This greatly simplifies reasoning about strategies making progress.
    """

    target: TargetSpec
    """The target this strategy is focusing on."""
    expander: TargetedExpander
    """Instance to track width expansion during search (if applicable)."""
    initial_lower_load: Optional[DiscreteLoad]
    """Smaller of the two loads distinguished at instance creation.
    Can be None if upper bound is the min load."""
    initial_upper_load: Optional[DiscreteLoad]
    """Larger of the two loads distinguished at instance creation.
    Can be None if lower bound is the max load."""
    handler: LimitHandler = field(repr=False)
    """Reference to the limit handler instance."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""

    @abstractmethod
    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate a load candidate if the conditions activate this strategy.

        A complete candidate refers also to the nominating selector.
        To prevent circular dependence (selector refers to nominating strategy),
        this function returns only duration and width.

        Width should only be non-None if global current width should be updated
        when the candidate based on this becomes winner.
        But currently all strategies return non-None width
        if they return non-None load.

        :param bounds: Freshly updated bounds relevant for current target.
        :type bounds: RelevantBounds
        :returns: Two nones or candidate intended load and duration.
        :rtype: Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]
        """
        return None, None

    def won(self, bounds: RelevantBounds, load: DiscreteLoad) -> None:
        """Notify the strategy its candidate became the winner.

        Most strategies have no use for this information,
        but some strategies may need to update their private information.

        :param bounds: Freshly updated bounds relevant for current target.
        :param load: The current load, so strategy does not need to remember.
        :type bounds: RelevantBounds
        :type load: DiscreteLoad
        """
        return

    def not_worth(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """A check on bounds common for multiple strategies.

        The load is worth measuring only if it can create or improve
        either relevant bound.

        Each strategy is designed to create a relevant bound for current target,
        which is only needed if that (or better) bound does not exist yet.
        Conversely, if a strategy does not nominate, it is because
        the load it would nominate (if any) is found not worth by this method.

        :param bounds: Current relevant bounds.
        :param load: Load of a possible candidate.
        :type bounds: RelevantBounds
        :type load: DiscreteLoad
        :returns: True if the load should NOT be nominated.
        :rtype: bool
        """
        if bounds.clo and bounds.clo >= load:
            return True
        if bounds.chi and bounds.chi <= load:
            return True
        if bounds.clo and bounds.chi:
            # We are not hitting min nor max load.
            # Measuring at this load will create or improve clo or chi.
            # The only reason not to nominate is if interval is narrow already.
            wig = DiscreteInterval(
                lower_bound=bounds.clo,
                upper_bound=bounds.chi,
            ).width_in_goals(self.target.discrete_width)
            if wig <= 1.0:
                return True
        return False
