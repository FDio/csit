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


from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from .discrete_load import DiscreteLoad
from .limit_handler import LimitHandler
from .measurement_database import MeasurementDatabase
from .relevant_bounds import RelevantBounds
from .target_spec import TargetSpec
from .strategy import IntervalExpander, StrategyBase, STRATEGY_CLASSES


@dataclass
class Selector:
    """FIXME."""

    final_target: TargetSpec
    """The target this selector is trying to ultimately achieve."""
    initial_lower_load: DiscreteLoad
    """Smaller of the two loads distinguished at instance creation.
    During generation, this value is reused to store previous target bound."""
    initial_upper_load: DiscreteLoad
    """Larger of the two loads distinguished at instance creation.
    During generation, this value is reused to store previous target bound."""
    database: MeasurementDatabase = field(repr=False)
    """Reference to a database used by all selectors."""
    handler: LimitHandler = field(repr=False)
    """Reference to the class used to avoid too narrow intervals."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""
    # Primary above, derived below.
    current_target: TargetSpec = None
    """The target the selector is focusing on currently."""
    target_stack: List[TargetSpec] = None
    """Stack of targets. When current target is achieved, next is popped."""
    fallback_stack: List[Tuple[DiscreteLoad, DiscreteLoad]] = None
    """If a later target got a false progress and needs to be reverted,
    it is important the initial load values are restored properly from here."""
    strategies: Tuple[StrategyBase] = None
    """Instances implementing particular selection strategies."""
    current_strategy: Optional[StrategyBase] = None
    """Reference to strategy used on last enter, needed by keep_going."""
    # Cache.
    bounds: RelevantBounds = None
    """New relevant bounds for this round of candidate selection."""

    def __post_init__(self) -> None:
        """Initialize derived values."""
        self.fallback_stack = []
        self.target_stack = [self.final_target]
        while preceding_target := self.target_stack[-1].preceding:
            self.target_stack.append(preceding_target)
        self.current_target = self.target_stack.pop()
        self._recreate_strategies()

    def _recreate_strategies(self):
        """Recreate strategies after targets have changed."""
        interval_expander = IntervalExpander(
            target=self.current_target,
            initial_lower_load=self.initial_lower_load,
            initial_upper_load=self.initial_upper_load,
            handler=self.handler,
            debug=self.debug,
        )
        self.strategies = tuple(
            cls(
                target=self.current_target,
                initial_lower_load=self.initial_lower_load,
                initial_upper_load=self.initial_upper_load,
                interval_expander=interval_expander,
                handler=self.handler,
                debug=self.debug,
            )
            for cls in STRATEGY_CLASSES
        )
        self.current_strategy = None
        self.debug(f"Created strategies for: {self.current_target}")

    def _update_bounds(self) -> None:
        """Before each iteration, call this to update bounds cache."""
        self.bounds = RelevantBounds.from_database(
            database=self.database, target=self.current_target
        )

    def nominate(self) -> Tuple[Optional[DiscreteLoad], float]:
        """Find first strategy that wants to nominate, return trial inputs.

        Returned load is None if no strategy wants to nominate.

        Current target may be rotated in any diration to find nomination.

        :returns: Nominated load and current target duration in seconds.
        :rtype: Tuple[Optional[DiscreteLoad], float]
        :raises RuntimeError: When internal inconsistency is detected.
        """
        self._update_bounds()
        self.current_strategy = None
        while 1:
            for strategy in self.strategies:
                if load := strategy.nominate(self.bounds):
                    self.current_strategy = strategy
                    return load, self.current_target.trial_duration
            # Perhaps regression to shorter trials needed?
            if not self.bounds.clo and not self.bounds.chi:
                if self.current_target.preceding:
                    # Yes, shorter trials are needed.
                    self.target_stack.append(self.current_target)
                    self.current_target = self.current_target.preceding
                    pair = self.fallback_stack.pop()
                    self.initial_lower_load, self.initial_upper_load = pair
                    self._update_bounds()
                    self._recreate_strategies()
                    continue
                raise RuntimeError("No current bounds for initial target.")
            # Perhaps final target is reached?
            if not self.target_stack:
                return None, self.current_target.trial_duration
            # Everything is ready for next target in the chain.
            fallback_pair = (self.initial_lower_load, self.initial_upper_load)
            self.fallback_stack.append(fallback_pair)
            self.current_target = self.target_stack.pop()
            # Debug logs look better if we forget bounds are LoadStats.
            # Abuse rounding (if not None) to convert to pure DiscreteLoad.
            clo, chi = self.bounds.clo, self.bounds.chi
            self.initial_lower_load = clo.rounded_down() if clo else clo
            self.initial_upper_load = chi.rounded_down() if chi else chi
            self._update_bounds()
            self._recreate_strategies()

    def keep_going(self, load: DiscreteLoad) -> bool:
        """Return whether current strategy wants another trial at the same load.

        Only call when previous enter nominaten non-None load.

        :param load: The load previously nominated by current strategy.
        :type load: DiscreteLoad
        :returns: Yes if the same load should be measured again.
        :rtype: bool
        """
        self._update_bounds()
        return self.current_strategy.keep_going(bounds=self.bounds, load=load)
