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
from typing import Optional

from ..discrete_interval import DiscreteInterval
from ..discrete_load import DiscreteLoad
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class HalveStrategy(StrategyBase):
    """FIXME."""

    def enter(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Enter a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if not self.initial_lower_load or not self.initial_upper_load:
            return None
        if self.initial_lower_load not in (bounds.plo, bounds.clo):
            return None
        if self.initial_upper_load not in (bounds.phi, bounds.chi):
            return None
        interval = DiscreteInterval(
            low_end=self.initial_lower_load,
            high_end=self.initial_upper_load,
        )
        wig = interval.width_in_goals(self.target.discrete_width)
        if wig > 2.0:
            return None
        if wig > 1.0:
            load = interval.middle(self.target.discrete_width)
            self.debug(f"Halving available: {load}")
            return load
        # Already narrow enough.
        return None

    def keep_going(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """Return True if the selector should keep measuring the previous load.

        False can mean either an intended resolution
        (the previous load has become a new current bound),
        or an unexpected change of context
        (other strategy has invalidated an older bound).
        Either way, the selector should start entering strategies anew.

        FIXME.
        """
        if bounds.clo and bounds.clo > self.initial_lower_load:
            self.debug("Clo appeared up, deactivating halving as success.")
            return False
        if bounds.chi and bounds.chi < self.initial_upper_load:
            self.debug("Chi appeared down, deactivating halving as success.")
            return False
        if self.initial_lower_load not in (bounds.plo, bounds.clo):
            if load != bounds.plo:
                self.debug("Lower bound surprise, halving aborted.")
                return False
        if self.initial_upper_load not in (bounds.phi, bounds.chi):
            if load != bounds.phi:
                self.debug("Upper bound surprise, halving aborted.")
                return False
        self.debug(f"Halving continues at {load}")
        return True
