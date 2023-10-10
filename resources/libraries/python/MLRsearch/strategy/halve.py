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

"""Module defining HalveStrategy class."""


from dataclasses import dataclass
from typing import Optional, Tuple

from ..discrete_interval import DiscreteInterval
from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..relevant_bounds import RelevantBounds
from .base import StrategyBase


@dataclass
class HalveStrategy(StrategyBase):
    """First strategy to apply for a new current target.

    Pick a load between initial lower bound and initial upper bound,
    nominate it if it is (still) worth it.

    In a sense, this can be viewed as an extension of preceding target's
    bisect strategy. But as the current target may require a different
    trial duration, it is better to do it for the new target.

    Alternatively, this is a way to save one application
    od subsequent refine strategy, thus avoid risking triggering
    an external search (important time saver for highly unstable SUTs).
    Either way, minor time save is achieved by preceding target
    only needing to reach double of current target width.

    If the distance between initial bounds is already at or below
    current target width, the middle point is not nominated.
    The reasoning is that in this case external search is likely
    to get triggered by the subsequent refine strategies,
    so attaining a relevant bound here is not as likely to help.
    """

    def nominate(
        self, bounds: RelevantBounds
    ) -> Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]:
        """Nominate the middle between initial lower and upper bound.

        The returned width is the target width, even if initial bounds
        happened to be closer together.

        :param bounds: Freshly updated bounds relevant for current target.
        :type bounds: RelevantBounds
        :returns: Two nones or candidate intended load and duration.
        :rtype: Tuple[Optional[DiscreteLoad], Optional[DiscreteWidth]]
        """
        if not self.initial_lower_load or not self.initial_upper_load:
            return None, None
        interval = DiscreteInterval(
            lower_bound=self.initial_lower_load,
            upper_bound=self.initial_upper_load,
        )
        wig = interval.width_in_goals(self.target.discrete_width)
        if wig > 2.0:
            # Can happen for initial target.
            return None, None
        if wig <= 1.0:
            # Already was narrow enough, refinements shall be sufficient.
            return None, None
        load = interval.middle(self.target.discrete_width)
        if self.not_worth(bounds, load):
            return None, None
        self.debug(f"Halving available: {load}")
        # TODO: Report possibly smaller width?
        self.expander.limit(self.target.discrete_width)
        return load, self.target.discrete_width
