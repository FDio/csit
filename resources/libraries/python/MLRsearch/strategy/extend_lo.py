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

from ..discrete_load import DiscreteLoad
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class ExtendLoStrategy(StrategyBase):
    """FIXME."""

    old_chi: DiscreteLoad = None
    """FIXME."""

    def enter(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Enter a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if bounds.clo or not bounds.chi or bounds.chi <= self.handler.min_load:
            return None
        self.debug(
            f"Ext lo considering width {self.interval_expander.next_width}"
        )
        load = bounds.chi - self.interval_expander.next_width
        load = self.handler.handle(
            load=load,
            width=self.target.discrete_width,
            clo=bounds.clo,
            chi=bounds.chi,
        )
        if not load or load >= bounds.chi:
            return None
        self.old_chi = bounds.chi
        self.debug(f"No clo, extending down: {load}")
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
        if bounds.clo:
            if load == bounds.clo:
                self.debug("Extend found a valid lowerbound, stopping extend.")
                return False
            self.debug("Unexpected clo appeared, aborting extend down.")
            return False
        if bounds.chi:
            if load == bounds.chi:
                self.debug("Extend found another invalid lowerbound, aborting.")
                self.interval_expander.expand()
                return False
            if bounds.chi == self.old_chi:
                self.debug(
                    f"No change, continue examining extend down at {load}"
                )
                return True
            self.debug("Unexpected chi change, aborting extend down.")
            return False
        raise RuntimeError("Chi disappeared, internal error.")
