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

"""Module defining ExtendHiStrategy class."""


from dataclasses import dataclass
from typing import Optional, Tuple

from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class ExtendHiStrategy(StrategyBase):
    """This strategy is applied when there is no relevant upper bound.

    Typically this is needed after RefineHiStrategy turned initial upper bound
    into a current relevant lower bound.
    """

    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate current relevant lower bound plus expander width.

        This performs external search in upwards direction,
        until a valid upper bound for the current target is found,
        or until max load is hit.
        Limit handling is used to avoid nominating too close
        (or above) the max rate.

        Width expansion is only applied if the candidate becomes a lower bound,
        so that is detected in done method.

        :param bounds: Freshly updated bounds relevant for current target.
        :type bounds: RelevantBounds
        :returns: Two nones or candidate intended load and duration.
        :rtype: Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]
        """
        if bounds.chi or not bounds.clo or bounds.clo >= self.handler.max_load:
            return None, None
        width = self.expander.get_width()
        load = self.handler.handle(
            load=bounds.clo + width,
            width=self.target.discrete_width,
            clo=bounds.clo,
            chi=bounds.chi,
        )
        if self.not_worth(bounds=bounds, load=load):
            return None, None
        self.debug(f"No chi, extending up: {load}")
        return load, width

    def done(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """Return what the base class says, expand width if still no upperbound.

        :param bounds: Freshly updated bounds relevant for current target.
        :param load: The current load, so strategy does not need to remember.
        :type bounds: RelevantBounds
        :type load: DiscreteLoad
        :returns: True only if the current load became a bound.
        :rtype: bool
        """
        if load == bounds.clo:
            self.expander.expand()
        return super().done(bounds=bounds, load=load)
