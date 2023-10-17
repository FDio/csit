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

"""Module defining Selector class."""


from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from .dataclass import secondary_field
from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth
from .expander import TargetedExpander
from .global_width import GlobalWidth
from .limit_handler import LimitHandler
from .measurement_database import MeasurementDatabase
from .relevant_bounds import RelevantBounds
from .target_spec import TargetSpec
from .strategy import StrategyBase, STRATEGY_CLASSES


@dataclass
class Selector:
    """A selector is an abstraction that focuses on only one of search goals.

    While lower-level logic is hidden in strategy classes,
    the code in this class is responsible for initializing strategies
    and shifting targets towards the final target.

    While the public methods have the same names and meaning as the ones
    in strategy classes, their signature is different.
    Selector adds the current target trial duration to the output of nominate(),
    and adds the current bounds to the input of won().

    The nominate method does not return a complete Candidate instance,
    as we need to avoid circular dependencies
    (candidate will refer to selector).
    """

    final_target: TargetSpec
    """The target this selector is trying to ultimately achieve."""
    global_width: GlobalWidth
    """Reference to the global width tracking instance."""
    initial_lower_load: DiscreteLoad
    """Smaller of the two loads distinguished at instance creation.
    During operation, this field is reused to store preceding target bound."""
    initial_upper_load: DiscreteLoad
    """Larger of the two loads distinguished at instance creation.
    During operation, this field is reused to store preceding target bound."""
    database: MeasurementDatabase = field(repr=False)
    """Reference to the common database used by all selectors."""
    handler: LimitHandler = field(repr=False)
    """Reference to the class used to avoid too narrow intervals."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""
    # Primary above, derived below.
    current_target: TargetSpec = secondary_field()
    """The target the selector is focusing on currently."""
    target_stack: List[TargetSpec] = secondary_field()
    """Stack of targets. When current target is achieved, next is popped."""
    strategies: Tuple[StrategyBase] = secondary_field()
    """Instances implementing particular selection strategies."""
    current_strategy: Optional[StrategyBase] = secondary_field()
    """Reference to strategy used for last nomination, needed for won()."""
    # Cache.
    bounds: RelevantBounds = secondary_field()
    """New relevant bounds for this round of candidate selection."""

    def __post_init__(self) -> None:
        """Initialize derived values."""
        self.target_stack = [self.final_target]
        while preceding_target := self.target_stack[-1].preceding:
            self.target_stack.append(preceding_target)
        self.current_target = self.target_stack.pop()
        self._recreate_strategies()

    def _recreate_strategies(self) -> None:
        """Recreate strategies after current target has changed.

        Width expander is recreated as target width is now smaller.
        For convenience, strategies get injectable debug
        which prints also the current target.
        """
        expander = TargetedExpander(
            target=self.current_target,
            global_width=self.global_width,
            initial_lower_load=self.initial_lower_load,
            initial_upper_load=self.initial_upper_load,
            handler=self.handler,
            debug=self.debug,
        )

        def wrapped_debug(text: str) -> None:
            """Call self debug with current target info prepended.

            :param text: Message to log at debug level.
            :type text: str
            """
            self.debug(f"Target {self.current_target}: {text}")

        self.strategies = tuple(
            cls(
                target=self.current_target,
                expander=expander,
                initial_lower_load=self.initial_lower_load,
                initial_upper_load=self.initial_upper_load,
                handler=self.handler,
                debug=wrapped_debug,
            )
            for cls in STRATEGY_CLASSES
        )
        self.current_strategy = None
        self.debug(f"Created strategies for: {self.current_target}")

    def _update_bounds(self) -> None:
        """Before each iteration, call this to update bounds cache."""
        self.bounds = self.database.get_relevant_bounds(self.current_target)

    def nominate(
        self,
    ) -> Tuple[Optional[DiscreteLoad], float, Optional[DiscreteWidth]]:
        """Find first strategy that wants to nominate, return trial inputs.

        Returned load is None if no strategy wants to nominate.

        Current target is shifted when (now preceding) target is reached.
        As each strategy never becomes done before at least one
        bound relevant to the current target becomes available,
        it is never needed to revert to the preceding target after the shift.

        As the initial trials had inputs relevant to all initial targets,
        the only way for this not to nominate a load
        is when the final target is reached (including hitting min or max load).
        The case of hitting min load raises, so search fails early.

        :returns: Nominated load, duration, and global width to set if winning.
        :rtype: Tuple[Optional[DiscreteLoad], float, Optional[DiscreteWidth]]
        :raises RuntimeError: If internal inconsistency is detected,
            or if min load becomes an upper bound.
        """
        self._update_bounds()
        self.current_strategy = None
        while 1:
            for strategy in self.strategies:
                load, width = strategy.nominate(self.bounds)
                if load:
                    self.current_strategy = strategy
                    return load, self.current_target.trial_duration, width
            if not self.bounds.clo and not self.bounds.chi:
                raise RuntimeError("Internal error: no clo nor chi.")
            if not self.target_stack:
                if not self.bounds.clo and self.current_target.fail_fast:
                    raise RuntimeError(f"No lower bound: {self.bounds.chi}")
                self.debug(f"Goal {self.current_target} reached: {self.bounds}")
                return None, self.current_target.trial_duration, None
            # Everything is ready for next target in the chain.
            self.current_target = self.target_stack.pop()
            # Debug logs look better if we forget bounds are TrimmedStat.
            # Abuse rounding (if not None) to convert to pure DiscreteLoad.
            clo, chi = self.bounds.clo, self.bounds.chi
            self.initial_lower_load = clo.rounded_down() if clo else clo
            self.initial_upper_load = chi.rounded_down() if chi else chi
            self._update_bounds()
            self._recreate_strategies()

    def won(self, load: DiscreteLoad) -> None:
        """Update any private info when candidate became a winner.

        :param load: The load previously nominated by current strategy.
        :type load: DiscreteLoad
        """
        self._update_bounds()
        self.current_strategy.won(bounds=self.bounds, load=load)
