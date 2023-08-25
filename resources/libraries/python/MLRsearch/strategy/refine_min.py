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
class RefineMinStrategy(StrategyBase):
    """FIXME."""

    def enter(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Enter a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if bounds.phi and not bounds.chi:
            if bounds.phi == (load := self.handler.min_load):
                self.debug(f"Min load refinement available: {load}")
                return load
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
        if bounds.chi:
            self.debug("Chi appeared, deactivating min refinement.")
            return False
        if bounds.phi != load:
            self.debug("Phi changed, deactivating min refinement.")
            return False
        self.debug(f"Min load refinement continues: {load}")
        return True
