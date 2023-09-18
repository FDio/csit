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

"""Module defining CandidateSelector class."""


from dataclasses import dataclass
from typing import Callable, Optional

from ..discrete_interval import DiscreteInterval
from ..discrete_load import DiscreteLoad
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class HalveStrategy(StrategyBase):
    """FIXME."""

    previous_load: Optional[DiscreteLoad] = None
    """Nomination logic is simpler with this cache."""

    def remember(self, load: Optional[DiscreteLoad]) -> Optional[DiscreteLoad]:
        """Shortcut to avoid frequent two-liner.
        FIXME.
        """
        self.previous_load = load
        return load

    def create_debug(self, suppress_debug: bool) -> Callable[[str], None]:
        """FIXME"""

        def my_debug(text):
            """FIXME"""
            if not suppress_debug:
                self.debug(text)

        return my_debug

    def nominate(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Nominate a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if load := self.previous_load:
            if self.keep_going(bounds, load, suppress_debug=True):
                self.debug(f"Stick to previous halving decision: {load}")
                return load
        if not self.initial_lower_load or not self.initial_upper_load:
            return self.remember(None)
        if self.initial_lower_load not in (bounds.plo, bounds.clo):
            return self.remember(None)
        if self.initial_upper_load not in (bounds.phi, bounds.chi):
            return self.remember(None)
        interval = DiscreteInterval(
            low_end=self.initial_lower_load,
            high_end=self.initial_upper_load,
        )
        wig = interval.width_in_goals(self.target.discrete_width)
        if wig > 2.0:
            return self.remember(None)
        if wig > 1.0:
            load = interval.middle(self.target.discrete_width)
            self.debug(f"Halving available: {load}")
            return self.remember(load)
        # Already narrow enough.
        return self.remember(None)

    def keep_going(
        self, bounds: RelevantBounds, load: DiscreteLoad, suppress_debug=False
    ) -> bool:
        """Return True if the selector should keep measuring the previous load.

        False can mean either an intended resolution
        (the previous load has become a new current bound),
        or an unexpected change of context
        (other strategy has invalidated an older bound).
        Either way, the selector should start entering strategies anew.

        FIXME.
        """
        debug = self.create_debug(suppress_debug)
        if bounds.clo and bounds.clo > self.initial_lower_load:
            debug("Clo appeared up, deactivating halving as success.")
            return False
        if bounds.chi and bounds.chi < self.initial_upper_load:
            debug("Chi appeared down, deactivating halving as success.")
            return False
        if self.initial_lower_load not in (bounds.plo, bounds.clo):
            if load != bounds.plo:
                debug("Lower bound surprise, halving aborted.")
                return False
        if self.initial_upper_load not in (bounds.phi, bounds.chi):
            if load != bounds.phi:
                debug("Upper bound surprise, halving aborted.")
                return False
        debug(f"Halving continues at {load}")
        return True
