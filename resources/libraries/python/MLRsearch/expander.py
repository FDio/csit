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

"""Module defining TargetExpander class."""


from dataclasses import dataclass, field
from typing import Callable, Optional

from .dataclass import secondary_field
from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth
from .global_width import GlobalWidth
from .limit_handler import LimitHandler
from .target_spec import TargetSpec


@dataclass
class TargetedExpander:
    """Utility class to track expanding width during external search.

    One instance per selector but takes into consideration global current width.

    Generally, many strategies may limit next_width immediately,
    but next_width expands only after measurement
    when external search fails to find its bound (global width is also bumped).
    See strategy classes for specific details on external and internal search.
    """

    target: TargetSpec
    """The target this strategy is focusing on."""
    global_width: GlobalWidth
    """Reference to the global width tracking instance."""
    initial_lower_load: Optional[DiscreteLoad]
    """Smaller of the two loads distinguished at instance creation.
    Can be None if initial upper bound is the min load."""
    initial_upper_load: Optional[DiscreteLoad]
    """Larger of the two loads distinguished at instance creation.
    Can be None if initial lower bound is the max load."""
    handler: LimitHandler = field(repr=False)
    """Reference to the class used to avoid too narrow intervals."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""
    # Primary above, derived below.
    next_width: DiscreteWidth = secondary_field()
    """This will be used in next search step if no strategy intervenes."""

    def __post_init__(self) -> None:
        """Prepare next width."""
        self.next_width = self.target.discrete_width
        if self.initial_lower_load and self.initial_upper_load:
            interval_width = self.initial_upper_load - self.initial_lower_load
            self.next_width = max(self.next_width, interval_width)
        self.expand(bump_global=False)

    def expand(self, bump_global: bool = True) -> None:
        """Multiply next width by expansion coefficient.

        The global current width should be bumped when external search
        is done but load is not the bound we were looking for.

        For global width shrinking, set the field directly.

        :param bump_global: False if called from limit or post init.
        :type bump_global: bool
        """
        self.next_width *= self.target.expansion_coefficient
        if bump_global:
            self.global_width.width = self.next_width

    def get_width(self) -> DiscreteWidth:
        """Return next width corrected by global current width.

        :returns: The width to use, see GlobalWidth.
        :rtype: DiscreteWidth
        """
        return self.global_width.or_larger(self.next_width)

    def limit(self, last_width: DiscreteWidth) -> None:
        """Decrease the prepared next width.

        This is called by other strategies when bounds are getting narrower.

        Global current width is not updated yet,
        as the other strategy may not end up becoming the winner
        and we want to avoid interfering with other selector strategies.

        :param last_width: As applied by other strategy, smaller of two halves.
        :type last_width: DiscreteWidth
        """
        self.next_width = max(last_width, self.target.discrete_width)
        self.expand(bump_global=False)
