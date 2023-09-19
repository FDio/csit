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

"""Module defining StrategyBase class."""


from dataclasses import dataclass, field
from typing import Callable, Optional

from ..discrete_load import DiscreteLoad
from ..discrete_width import DiscreteWidth
from ..limit_handler import LimitHandler
from ..target_spec import TargetSpec
from .current_width import CurrentWidth


@dataclass
class TargetedExpander:
    """FIXME."""

    target: TargetSpec
    """The target this strategy is focusing on."""
    current_width: CurrentWidth
    """Reference to the global width tracking instance."""
    initial_lower_load: Optional[DiscreteLoad]
    """Smaller of the two loads distinguished at instance creation.
    Can be None if upper bound is the min load."""
    initial_upper_load: Optional[DiscreteLoad]
    """Larger of the two loads distinguished at instance creation.
    Can be None if lower bound is the max load."""
    handler: LimitHandler = field(repr=False)
    """Reference to the class used to avoid too narrow intervals."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""
    # Primary above, derived below.
    next_width: DiscreteWidth = None
    """FIXME."""

    def __post_init__(self) -> None:
        """FIXME."""
        self.next_width = self.target.discrete_width
        if self.initial_lower_load and self.initial_upper_load:
            interval_width = self.initial_upper_load - self.initial_lower_load
            self.next_width = max(self.next_width, interval_width)
        self.expand(bump_current=False)

    def expand(self, bump_current: bool = True) -> None:
        """FIXME."""
        self.next_width *= self.target.expansion_coefficient
        if bump_current:
            self.current_width.width = self.next_width

    def get_width(self) -> DiscreteWidth:
        """FIXME"""
        ret = self.current_width.or_larger(self.next_width)
        self.debug(f"DEBUG: nw {self.next_width} cw {self.current_width.width}")
        return ret

    def limit(self, last_width) -> None:
        """FIXME."""
        self.next_width = max(last_width, self.target.discrete_width)
        self.expand(bump_current=False)
