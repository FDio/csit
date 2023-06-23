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


from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from .action_enum import ActionEnum
from .discrete_interval import DiscreteInterval
from .discrete_load import DiscreteLoad
from .discrete_result import DiscreteResult
from .discrete_width import DiscreteWidth
from .limit_handler import LimitHandler
from .load_candidate import LoadCandidate
from .measurement_database import MeasurementDatabase
from .relevant_bounds import RelevantBounds
from .target_spec import TargetSpec


@dataclass
class CandidateSelector:
    """Class for selecting new trial input candidate for a particular target.

    Basically just one method is important for the caller,
    but it needs fairly complicated internal state,
    and logic is split into multiple internal methods.
    """

    target: TargetSpec
    """the target this selector is trying to achieve."""
    database: MeasurementDatabase = field(repr=False)
    """Reference to a database used by all selectors."""
    handler: LimitHandler = field(repr=False)
    """Reference to the class used to avoid too narrow intervals."""
    debug: Callable[[str], None] = field(repr=False)
    """Injectable function for debug logging."""
    # Primary above, derived below.
    halved: bool = False
    """Whether this selector already suceeded in the halving action."""
    refined_lo: bool = False
    """Whether this selector already succeeded in refine down action."""
    refined_hi: bool = False
    """Whether this selector already succeeded in refine up action."""
    prev_load: Optional[DiscreteLoad] = None
    """Load of candidate this selector nominated in the last call (if any)."""
    prev_action: ActionEnum = ActionEnum.WAIT
    """The action that motivated the last candidate nomination."""
    prev_width: DiscreteWidth = None
    """The width of interval previously applied in external search."""
    bounds: RelevantBounds = None
    """New relevant bounds for this round of candidate selection."""
    winner: bool = False
    """Whether the previous candidate was actually measured."""

    def __post_init__(self):
        """Initialize width. Initial target skips first three actions."""
        self.prev_width = self.target.discrete_width
        if not self.target.preceding:
            self.halved = True
            self.refined_hi = True
            self.refined_lo = True

    def candidate_after(
        self, measured: Optional[DiscreteResult]
    ) -> LoadCandidate:
        """Update state after newest measurement, nominate new candidate.

        This is the main entry point.

        :param measured: The trial result measured after last call (if any).
        :type measured: Optional[DiscreteResult]
        :returns: New candidate (falsy if no further trial is needed).
        :rtype: LoadCandidate
        """
        if self.prev_action == ActionEnum.DONE:
            self.debug("Already done.")
            return LoadCandidate(load=None, duration=0.0)
        self.winner = (
            measured and measured.discrete_load == self.prev_load
            if self.prev_load
            else False
        )
        self.bounds = RelevantBounds.from_database(
            database=self.database,
            target=self.target,
        )
        self.debug(f"{'winner, ' if self.winner else ''}bounds {self.bounds}")
        self._update_flags()
        load, action, handle = self._select_load()
        if handle:
            load = self.handler.handle(
                load=load,
                width=self.target.discrete_width,
                clo=self.bounds.clo,
                chi=self.bounds.chi,
            )
        self.prev_load, self.prev_action = load, action
        return LoadCandidate(
            load=load,
            duration=self.target.trial_duration,
        )

    def _update_flags(self) -> None:
        """Update internal state based on newest trial result.

        Some changes to state should be done only when candidate got measured,
        others only when the measurement changed relevant bonds.

        Here is the common logic for that,
        as it is somewhat independent from the actual candiate selection.
        """
        if not self.winner:
            return

        if self.prev_action == ActionEnum.REFINE_MIN:
            self.refined_lo = True
            return
        if self.prev_action == ActionEnum.REFINE_MAX:
            self.refined_hi = True
            return
        if self.prev_action == ActionEnum.HALVE:
            if self.bounds.clo and self.prev_load <= self.bounds.clo:
                self.halved = True
                self.refined_lo = True
            elif self.bounds.chi and self.prev_load >= self.bounds.chi:
                self.halved = True
                self.refined_hi = True
            return
        self.halved = True

        if self.prev_action in (ActionEnum.REFINE_LO, ActionEnum.EXT_LO):
            if self.prev_load >= self.bounds.chi:
                self.prev_width *= self.target.expansion_coefficient
        if self.prev_action in (ActionEnum.REFINE_HI, ActionEnum.EXT_HI):
            if self.prev_load <= self.bounds.clo:
                self.prev_width *= self.target.expansion_coefficient

        if self.prev_action == ActionEnum.REFINE_LO:
            if self.prev_load in (self.bounds.clo, self.bounds.chi):
                self.refined_lo = True
            return
        self.refined_lo = True
        if self.prev_action == ActionEnum.REFINE_HI:
            if self.prev_load in (self.bounds.clo, self.bounds.chi):
                self.refined_hi = True
            return
        self.refined_hi = True
        # Bisect or done or external search continues here.

    def _select_load(self) -> Tuple[DiscreteLoad, ActionEnum, bool]:
        """Return info about the new nomination decision.

        Returning None load means either we have narrow enough valid interval
        for the current goal, or we are hitting some other
        early return condition, (e.g. hitting min load or max load),
        or there is not enough data in measurement database
        (the current selector is waiting for the preceding selector).

        Situations related to min and max load are expected in measurement
        results, but load candidates are not constrained here,
        so the handling is centralized elsewhere.

        Note that the special re-measurements for hitting min or max load
        are unconditional (but they still disable further re-measurements).

        The implementation moves most of the logic to sub-methods.
        They also do most of logging, unless they lack the required context.

        :returns: The next load rate to measure at (or None when done);
            what action has motivated the nomination;
            and whether the load should be limit handled.
        :rtype: Tuple[DiscreteLoad, ActionEnum, bool]
        :raises RuntimeError: If internal logic error is detected.
        """
        if load := self._min_refine():
            return load, ActionEnum.REFINE_MIN, False
        if load := self._max_refine():
            return load, ActionEnum.REFINE_MAX, False
        if not self.halved:
            if load := self._halve():
                return load, ActionEnum.HALVE, False
        if not self.refined_lo:
            if load := self._lo_refine():
                return load, ActionEnum.REFINE_LO, False
        if not self.refined_hi:
            if load := self._hi_refine():
                return load, ActionEnum.REFINE_HI, False
        if not self.bounds.clo and not self.bounds.chi:
            self.debug("Doing nothing waiting for clo or chi.")
            return None, ActionEnum.WAIT, False
        if not self.bounds.clo:
            if self.prev_action == ActionEnum.EXT_LO:
                if (load := self.prev_load) < self.bounds.chi:
                    self.debug(f"Continue investigating extended lo: {load}")
                    return load, ActionEnum.EXT_LO, False
            if load := self._extend_down():
                self.debug(f"No current lower bound, extending down: {load}")
                return load, ActionEnum.EXT_LO, True
            # Hitting min load.
            return None, ActionEnum.DONE, False
        if self.prev_action == ActionEnum.EXT_HI and not self.bounds.chi:
            if (load := self.prev_load) > self.bounds.clo:
                self.debug(f"Continue investigating extended hi: {load}")
                return load, ActionEnum.EXT_HI, False
        if extend_load := self._extend_up():
            return extend_load, ActionEnum.EXT_HI, True
        if not (bisect_load := self._bisect()):
            self.prev_width = self.target.discrete_width
            self.debug("Target achieved.")
            return None, ActionEnum.DONE, False
        # Not hitting min load, so extend_load cannot be None.
        if (extend_load := self._extend_down()) > bisect_load:
            self.debug(f"Preferring to extend down: {extend_load}.")
            return extend_load, ActionEnum.EXT_LO, True
        # There is no realistic scenario where extending up from clo is better.
        self.debug(f"Preferring to bisect: {bisect_load}.")
        return bisect_load, ActionEnum.BISECT, False

    def _min_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or min load refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if self.bounds.phi and not self.bounds.chi:
            if (load := self.handler.min_load) == self.bounds.phi:
                self.debug(f"Min load refinement available: {load}")
                return load
        return None

    def _max_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or max load refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if self.bounds.plo and not self.bounds.clo:
            if (load := self.handler.max_load) == self.bounds.plo:
                self.debug(f"Max load refinement available: {load}")
                return load
        return None

    def _halve(self) -> Optional[DiscreteLoad]:
        """Return None, or load for halving action when detected.

        There is some overlap with last bisect, but we want to select
        the same load in both cases, regardless of tightest bounds duration sum.

        The decision is made based purely on interval width.

        :returns: Intended load for halving, or None if this is not halving.
        :rtype: Optional[DiscreteLoad]
        """
        plo, phi = self.bounds.plo, self.bounds.phi
        if not plo or not phi:
            return None
        interval = DiscreteInterval(plo, phi)
        wig = interval.width_in_goals(self.target.discrete_width)
        if wig > 2.0:
            return None
        if wig > 1.0:
            load = interval.middle(self.target.discrete_width)
            self.debug(f"Halving available: {load}")
            return load
        if (load := self.prev_load) and plo <= load <= phi:
            if self.prev_action == ActionEnum.HALVE:
                self.debug(f"Halving continues: {load}")
                return load
            # Otherwise it is refinement.
        return None

    def _lo_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or load for lowerbound refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if not self.bounds.chi or not (load := self.bounds.plo):
            return None
        if self.bounds.clo:
            if load == self.bounds.clo:
                return None
            interval = DiscreteInterval(self.bounds.clo, self.bounds.chi)
            if interval.width_in_goals(self.target.discrete_width) <= 1.0:
                self.debug("Not re-measuring low when narrow alrady.")
                return None
        interval = DiscreteInterval(load, self.bounds.chi)
        if interval.width_in_goals(self.target.discrete_width) > 1.0:
            # The previous phase tightest bound would not be this far.
            return None
        self.debug(f"Lowerbound re-measurement available: {load}")
        return load

    def _hi_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or load for upperbound refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if not self.bounds.clo or not (load := self.bounds.phi):
            return None
        if self.bounds.chi:
            if load == self.bounds.chi:
                return None
            interval = DiscreteInterval(self.bounds.clo, self.bounds.chi)
            if interval.width_in_goals(self.target.discrete_width) <= 1.0:
                self.debug("Not re-measuring high when narrow alrady.")
                return None
        interval = DiscreteInterval(self.bounds.clo, load)
        if interval.width_in_goals(self.target.discrete_width) > 1.0:
            # The previous phase tightest bound would not be this far.
            return None
        self.debug(f"Upperbound refinement available: {load}")
        return load

    def _extend_down(self) -> Optional[DiscreteLoad]:
        """Return extended width below.

        The only case when this returns None is when hitting min load already.

        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if self.bounds.chi <= self.handler.min_load:
            self.debug("Hitting min load, exit early.")
            return None
        self.prev_width = (
            self.prev_width if self.prev_width else self.target.discrete_width
        )
        load = self.bounds.chi - self.prev_width
        # Not emitting a comment to debug here, caller knows two cases.
        return load

    def _extend_up(self) -> Optional[DiscreteLoad]:
        """Return extended width above.

        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if self.bounds.chi:
            return None
        if self.bounds.clo >= self.handler.max_load:
            self.debug("Hitting max rate, we can exit.")
            return None
        self.prev_width = (
            self.prev_width if self.prev_width else self.target.discrete_width
        )
        load = self.bounds.clo + self.prev_width
        self.debug(f"No current upper bound, extending up: {load}")
        return load

    def _bisect(self) -> Optional[DiscreteLoad]:
        """Return middle rate or None if width is narrow enough.

        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        interval = DiscreteInterval(self.bounds.clo, self.bounds.chi)
        if interval.width_in_goals(self.target.discrete_width) <= 1.0:
            return None
        load = interval.middle(self.target.discrete_width)
        # Limit future width.
        width_lo = DiscreteInterval(self.bounds.clo, load).discrete_width
        width_hi = DiscreteInterval(load, self.bounds.chi).discrete_width
        self.prev_width = min(self.prev_width, max(width_lo, width_hi))
        # Not emitting a comment to debug here, caller knows two cases.
        return load
