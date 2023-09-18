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


@dataclass
class IntervalExpander:
    """FIXME."""

    target: TargetSpec
    """The target this strategy is focusing on."""
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

    def __post_init__(self):
        """FIXME."""
        self.next_width = self.target.discrete_width
        if self.initial_lower_load and self.initial_upper_load:
            self.limit(self.initial_upper_load - self.initial_lower_load)
        self.expand()

    def expand(self):
        """FIXME."""
        self.next_width *= self.target.expansion_coefficient

    def limit(self, last_width):
        """FIXME."""
        self.next_width = max(last_width, self.target.discrete_width)
