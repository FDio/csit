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
    """FIXME."""

    target: TargetSpec
    """The target this strategy is focusing on."""
    expander: TargetedExpander
    """FIXME."""
    initial_lower_load: Optional[DiscreteLoad]
    """Smaller of the two loads distinguished at instance creation.
    Can be None if upper bound is the min load."""
    initial_upper_load: Optional[DiscreteLoad]
    """Larger of the two loads distinguished at instance creation.
    Can be None if lower bound is the max load."""
    handler: LimitHandler = field(repr=False)
    """FIXME."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""

    @abstractmethod
    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate a load candidate if the conditions activate this strategy.

        FIXME.
        """
        return None, None

    def done(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """Return True if the selector should keep measuring the previous load.

        False can mean either an intended resolution
        (the previous load has become a new current bound),
        or an unexpected change of context
        (other strategy has invalidated an older bound).
        Either way, the selector should start entering strategies anew.

        FIXME.
        """
        return self.clo_or_chi_created(bounds=bounds, load=load)

    def clo_or_chi_created(
        self, bounds: RelevantBounds, load: DiscreteLoad
    ) -> bool:
        """FIXME"""
        strategy_name = self.__class__.__name__
        if bounds.clo and bounds.clo == load:
            self.debug(f"Load become clo, stopping {strategy_name}.")
            return True
        if bounds.chi and bounds.chi == load:
            self.debug(f"Load become chi, stopping {strategy_name}.")
            return True
        if bounds.clo and bounds.clo > load:
            raise RuntimeError("Lower bound appeared high, internal error.")
        if bounds.chi and bounds.chi < load:
            raise RuntimeError("Upper bound appeared low, internal error.")
        self.debug(f"Continuing {strategy_name} at {load}")
        return False

    def not_worth(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """A check on bounds common for multiple strategies.
        FIXME."""
        if bounds.clo and bounds.clo >= load:
            return True
        if bounds.chi and bounds.chi <= load:
            return True
        # We are not hitting min nor max load.
        # Measuring at this load will create or improve clo or chi.
        # The only reason not to nominate is if interval is narrow already.
        if bounds.clo and bounds.chi:
            wig = DiscreteInterval(
                low_end=bounds.clo,
                high_end=bounds.chi,
            ).width_in_goals(self.target.discrete_width)
            if wig <= 1.0:
                return True
        return False
