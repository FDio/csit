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
class RefineHiStrategy(StrategyBase):
    """FIXME."""

    def nominate(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Nominate a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if not (load := self.initial_upper_load) or not self.initial_lower_load:
            return None
        if bounds.phi != load or (bounds.chi and bounds.chi <= load):
            return None
        tlo = bounds.plo if bounds.plo else bounds.clo
        if not tlo or not self.initial_lower_load <= tlo < load:
            return None
        wig = DiscreteInterval(
            low_end=tlo,
            high_end=load,
        ).width_in_goals(self.target.discrete_width)
        if wig > 1.0:
            return None
        self.debug(f"Upperbound refinement available: {load}")
        return load

    def keep_going(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """Return True if the selector should keep measuring the previous load.

        False can mean either an intended resolution
        (the previous load has become a new current bound),
        or an unexpected change of context
        (other strategy has invalidated an older bound).
        Either way, the selector should start entering strategies anew.

        FIXME.
        """
        if bounds.chi and bounds.chi == load:
            self.debug("Upper bound confirmed, refinement done successfully.")
            return False
        if bounds.clo and bounds.clo == load:
            self.debug("Upper bound invalidated, stopping refinement.")
            return False
        if bounds.clo and bounds.clo >= load:
            self.debug("Lower bound appeared high, aborting refinement.")
            return False
        if bounds.chi and bounds.chi <= load:
            self.debug("Upper bound appeared low, aborting refinement.")
            return False
        if not bounds.phi:
            self.debug("Phi disappeared, aborting refinement.")
            return False
        if bounds.phi > load:
            self.debug("Phi moved up, aborting refinement.")
            return False
        if bounds.phi < load:
            self.debug("Phi moved down, aborting refinement.")
            return False
        self.debug(f"Upperbound refinement continues at {load}")
        return True
