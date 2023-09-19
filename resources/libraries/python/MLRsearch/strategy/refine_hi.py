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

"""Module defining RefineHiStrategy class."""


from dataclasses import dataclass
from typing import Optional, Tuple

from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class RefineHiStrategy(StrategyBase):
    """FIXME."""

    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate a load candidate if the conditions activate this strategy.

        FIXME.
        """
        if not (load := self.initial_upper_load):
            return None, None
        if self.not_worth(bounds=bounds, load=load):
            return None, None
        self.debug(f"Upperbound refinement available: {load}")
        # TODO: Limit to possibly smaller than target width?
        return load, self.target.discrete_width
