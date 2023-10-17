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

"""Module defining RefineLoStrategy class."""


from dataclasses import dataclass
from typing import Optional, Tuple

from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class RefineLoStrategy(StrategyBase):
    """If initial lower bound is still worth it, nominate it.

    This usually happens when halving resulted in relevant upper bound,
    or if there was no halving.
    This ensures a relevant bound (upper or lower) for the current target
    exists.
    """

    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate the initial lower bound.

        :param bounds: Freshly updated bounds relevant for current target.
        :type bounds: RelevantBounds
        :returns: Two nones or candidate intended load and duration.
        :rtype: Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]
        """
        if not (load := self.initial_lower_load):
            return None, None
        if self.not_worth(bounds=bounds, load=load):
            return None, None
        self.debug(f"Lowerbound refinement available: {load}")
        # TODO: Limit to possibly smaller than target width?
        self.expander.limit(self.target.discrete_width)
        return load, self.target.discrete_width
