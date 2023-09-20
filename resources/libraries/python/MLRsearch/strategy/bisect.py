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
from typing import Optional, Tuple

from ..discrete_interval import DiscreteInterval
from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class BisectStrategy(StrategyBase):
    """FIXME."""

    expand_on_clo: bool = False
    """FIXME."""
    expand_on_chi: bool = False
    """FIXME."""

    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if not bounds.clo or bounds.clo >= self.handler.max_load:
            return None, None
        if not bounds.chi or bounds.chi <= self.handler.min_load:
            return None, None
        interval = DiscreteInterval(bounds.clo, bounds.chi)
        if interval.width_in_goals(self.target.discrete_width) <= 1.0:
            return None, None
        load = interval.middle(self.target.discrete_width)
        load_ext, width = self._enter_lo(bounds, load)
        if load_ext:
            load = load_ext
            self.expand_on_clo, self.expand_on_chi = False, True
            self.debug(f"Preferring to extend down: {load}")
            return load, width
        load_ext, width = self._enter_hi(bounds, load)
        if load_ext:
            load = load_ext
            self.expand_on_clo, self.expand_on_chi = True, False
            self.debug(f"Preferring to extend up: {load}")
            return load, width
        if self.not_worth(bounds=bounds, load=load):
            return None, None
        self.expand_on_clo, self.expand_on_chi = False, False
        self.debug(f"Preferring to bisect: {load}")
        width_lo = DiscreteInterval(bounds.clo, load).discrete_width
        width_hi = DiscreteInterval(load, bounds.chi).discrete_width
        width = min(width_lo, width_hi)
        self.expander.limit(width)
        return load, width

    def _enter_lo(
        self, bounds: RelevantBounds, load: DiscreteLoad
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """FIXME."""
        if not self.initial_upper_load:
            self.debug("No enter lo: No initial upper load.")
            return None, None
        if load >= self.initial_upper_load:
            self.debug("No enter lo: Bisect load not below hi initial.")
            return None, None
        width = self.expander.get_width()
        new_load = bounds.chi - width
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
            return None, None
        if new_load <= load:
            self.debug("No enter lo: Rounded load not higher than bisect.")
            return None, None
        if new_load >= self.initial_upper_load:
            self.debug("No enter lo: Rounded load higher than init hi.")
            return None, None
        if self.not_worth(bounds=bounds, load=load):
            raise RuntimeError(f"Load not worth: {load}")
        return new_load, width

    def _enter_hi(
        self, bounds: RelevantBounds, load: DiscreteLoad
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """FIXME."""
        if not self.initial_lower_load:
            self.debug("No enter hi: No initial lower load.")
            return None, None
        if load <= self.initial_lower_load:
            self.debug("No enter hi: Bisect load not above lo initial.")
            return None, None
        width = self.expander.get_width()
        new_load = bounds.clo + width
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
            return None, None
        if new_load >= load:
            self.debug("No enter hi: Rounded load not lower than bisect.")
            return None, None
        if new_load <= self.initial_lower_load:
            self.debug("No enter hi: Rounded load lower than init lo.")
            return None, None
        if self.not_worth(bounds=bounds, load=load):
            raise RuntimeError(f"Load not worth: {load}")
        return new_load, width

    def done(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """Return True if the selector should keep measuring the previous load.

        False can mean either an intended resolution
        (the previous load has become a new current bound),
        or an unexpected change of context
        (other strategy has invalidated an older bound).
        Either way, the selector should start entering strategies anew.

        FIXME.
        """
        if not self.clo_or_chi_created(bounds=bounds, load=load):
            return False
        if self.expand_on_clo and load == bounds.clo:
            self.expander.expand()
        elif self.expand_on_chi and load == bounds.chi:
            self.expander.expand()
        return True
