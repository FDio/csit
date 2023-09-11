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


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional

from ..discrete_load import DiscreteLoad
from ..limit_handler import LimitHandler
from ..relevant_bounds import RelevantBounds
from ..target_spec import TargetSpec
from .expander import IntervalExpander


@dataclass
class StrategyBase(ABC):
    """FIXME."""

    target: TargetSpec
    """The target this strategy is focusing on."""
    initial_lower_load: Optional[DiscreteLoad]
    """Smaller of the two loads distinguished at instance creation.
    Can be None if upper bound is the min load."""
    initial_upper_load: Optional[DiscreteLoad]
    """Larger of the two loads distinguished at instance creation.
    Can be None if lower bound is the max load."""
    interval_expander: IntervalExpander
    """FIXME."""
    handler: LimitHandler = field(repr=False)
    """FIXME."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""

    @abstractmethod
    def enter(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Enter a load candidate if the conditions activate this strategy.

        FIXME.
        """
        return None

    @abstractmethod
    def keep_going(self, bounds: RelevantBounds, load: DiscreteLoad) -> bool:
        """Return True if the selector should keep measuring the previous load.

        False can mean either an intended resolution
        (the previous load has become a new current bound),
        or an unexpected change of context
        (other strategy has invalidated an older bound).
        Either way, the selector should start entering strategies anew.

        FIXME.
        """
        return False
