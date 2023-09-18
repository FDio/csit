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
class BisectStrategy(StrategyBase):
    """FIXME."""

    old_clo: DiscreteLoad = None
    """FIXME."""
    old_chi: DiscreteLoad = None
    """FIXME."""
    expand_on_clo: bool = False
    """FIXME."""
    expand_on_chi: bool = False
    """FIXME."""

    def nominate(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Nominate a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if not bounds.clo or bounds.clo >= self.handler.max_load:
            return None
        if not bounds.chi or bounds.chi <= self.handler.min_load:
            return None
        self.old_clo, self.old_chi = bounds.clo, bounds.chi
        interval = DiscreteInterval(bounds.clo, bounds.chi)
        if interval.width_in_goals(self.target.discrete_width) <= 1.0:
            return None
        load = interval.middle(self.target.discrete_width)
        if load_ext := self._enter_lo(bounds, load):
            load = load_ext
            self.expand_on_clo, self.expand_on_chi = False, True
            self.debug(f"Preferring to extend down: {load}")
        elif load_ext := self._enter_hi(bounds, load):
            load = load_ext
            self.expand_on_clo, self.expand_on_chi = True, False
            self.debug(f"Preferring to extend up: {load}")
        else:
            self.expand_on_clo, self.expand_on_chi = False, False
            self.debug(f"Preferring to bisect: {load}")
        width_lo = DiscreteInterval(bounds.clo, load).discrete_width
        width_hi = DiscreteInterval(load, bounds.chi).discrete_width
        self.interval_expander.limit(min(width_lo, width_hi))
        return load

    def _enter_lo(
        self, bounds: RelevantBounds, load: DiscreteLoad
    ) -> Optional[DiscreteLoad]:
        """FIXME."""
        if not self.initial_upper_load:
            self.debug("No enter lo: No initial upper load.")
            return None
        if load >= self.initial_upper_load:
            self.debug("No enter lo: Bisect load not below hi initial.")
            return None
        self.debug(
            f"Enter lo considering width {self.interval_expander.next_width}"
        )
        new_load = bounds.chi - self.interval_expander.next_width
        self.debug(f"Enter lo raw load: {new_load}")
        new_load = self.handler.handle(
            load=new_load,
            width=self.target.discrete_width,
            clo=bounds.clo,
            chi=bounds.chi,
        )
        self.debug(f"Enter lo rounded load: {new_load}")
        if not new_load:
            self.debug("No enter lo: Load rounded to None.")
            return None
        if new_load <= load:
            self.debug("No enter lo: Rounded load not higher than bisect.")
            return None
        if new_load >= self.initial_upper_load:
            self.debug("No enter lo: Rounded load higher than init hi.")
            return None
        return new_load

    def _enter_hi(
        self, bounds: RelevantBounds, load: DiscreteLoad
    ) -> Optional[DiscreteLoad]:
        """FIXME."""
        if not self.initial_lower_load:
            self.debug("No enter hi: No initial lower load.")
            return None
        if load <= self.initial_lower_load:
            self.debug("No enter hi: Bisect load not above lo initial.")
            return None
        self.debug(
            f"Enter hi considering width {self.interval_expander.next_width}"
        )
        new_load = bounds.clo + self.interval_expander.next_width
        self.debug(f"Enter hi raw load: {new_load}")
        new_load = self.handler.handle(
            load=new_load,
            width=self.target.discrete_width,
            clo=bounds.clo,
            chi=bounds.chi,
        )
        self.debug(f"Enter hi rounded load: {new_load}")
        if not new_load:
            self.debug("No enter hi: Load rounded to None.")
            return None
        if new_load >= load:
            self.debug("No enter hi: Rounded load not lower than bisect.")
            return None
        if new_load <= self.initial_lower_load:
            self.debug("No enter hi: Rounded load lower than init lo.")
            return None
        return new_load

    def keep_going(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """Return True if the selector should keep measuring the previous load.

        False can mean either an intended resolution
        (the previous load has become a new current bound),
        or an unexpected change of context
        (other strategy has invalidated an older bound).
        Either way, the selector should start entering strategies anew.

        FIXME.
        """
        if not bounds.clo:
            raise RuntimeError("Clo disappeared, internal error.")
        if not bounds.chi:
            raise RuntimeError("Clo disappeared, internal error.")
        if bounds.clo == self.old_clo and bounds.chi == self.old_chi:
            self.debug(f"No change, keep doing the bounded thing at {load}")
            return True
        if load not in (bounds.clo, bounds.chi):
            self.debug("Unexpected movement, aborting.")
            return False
        if bounds.clo == load:
            self.debug("Found better clo, successful stop.")
            if self.expand_on_clo:
                self.interval_expander.expand()
        else:
            self.debug("Found better chi, successful stop.")
            if self.expand_on_chi:
                self.interval_expander.expand()
        # No need to expand, limit in enter already set correct value.
        return False
