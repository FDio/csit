# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""Module defining TargetTracker class."""


from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from .action_enum import ActionEnum
from .discrete_interval import DiscreteInterval
from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth
from .limit_handler import LimitHandler
from .load_candidate import LoadCandidate
from .measurement_database import MeasurementDatabase
from .relevant_bounds import RelevantBounds
from .target_spec import TargetSpec


@dataclass
class TargetTracker:
    """FIXME"""

    target_spec: TargetSpec
    """FIXME"""
    database: MeasurementDatabase = field(repr=False)
    """FIXME"""
    handler: LimitHandler = field(repr=False)
    """FIXME"""
    debug: Callable[[str], None] = field(repr=False)
    """FIXME"""
    # Primary above, derived below.
    halved: bool = False
    """FIXME"""
    refined_lo: bool = False
    """FIXME"""
    refined_hi: bool = False
    """FIXME"""
    prev_candidate: Optional[DiscreteLoad] = None
    """FIXME"""
    prev_action: ActionEnum = ActionEnum.WAIT
    """FIXME"""
    prev_width: DiscreteWidth = None
    """FIXME"""
    bounds: RelevantBounds = None
    """FIXME"""
    winner: bool = False
    """FIXME"""

    def __post_init__(self):
        """FIXME"""
        self.prev_width = self.target_spec.discrete_width
        if not self.target_spec.coarser:
            self.halved = True
            self.refined_hi = True
            self.refined_lo = True

    def candidate_after(
        self, measured: Optional[DiscreteLoad]
    ) -> LoadCandidate:
        """FIXME"""
        if self.prev_action == ActionEnum.DONE:
            self.debug("Already done.")
            return LoadCandidate(load=None, duration=0.0)
        self.winner = (
            measured and measured.discrete_load == self.prev_candidate
            if self.prev_candidate
            else False
        )
        self.bounds = RelevantBounds.from_database(
            database=self.database,
            current_target=self.target_spec,
        )
        self._update_flags()
        load, action, handle = self.select_load()
        if handle:
            load = self.handler.handle(
                load=load,
                width_goal=self.target_spec.discrete_width,
                clo=self.bounds.clo1,
                chi=self.bounds.chi1,
            )
        self.prev_candidate, self.prev_action = load, action
        return LoadCandidate(
            load=load,
            duration=self.target_spec.single_duration_whole,
        )

    def _update_flags(self) -> None:
        """FIXME"""
        if not self.winner:
            return

        if self.prev_action == ActionEnum.REFINE_MIN:
            self.refined_lo = True
            return
        if self.prev_action == ActionEnum.REFINE_MAX:
            self.refined_hi = True
            return
        if self.prev_action == ActionEnum.HALVE:
            if self.bounds.clo1 and self.prev_candidate <= self.bounds.clo1:
                self.halved = True
                self.refined_lo = True
            elif self.bounds.chi1 and self.prev_candidate >= self.bounds.chi1:
                self.halved = True
                self.refined_hi = True
            return
        self.halved = True

        if self.prev_action == ActionEnum.REFINE_LO:
            if self.prev_candidate in (self.bounds.clo1, self.bounds.chi1):
                self.refined_lo = True
            return
        self.refined_lo = True
        if self.prev_action == ActionEnum.REFINE_HI:
            if self.prev_candidate in (self.bounds.clo1, self.bounds.chi1):
                self.refined_hi = True
            return
        self.refined_hi = True

        if self.prev_action == ActionEnum.EXT_LO:
            if self.prev_candidate >= self.bounds.chi1:
                self.prev_width *= self.target_spec.expansion_coefficient
                return
        if self.prev_action == ActionEnum.EXT_HI:
            if self.prev_candidate <= self.bounds.clo1:
                self.prev_width *= self.target_spec.expansion_coefficient
                return
        # Bisect or done or extended search continues here.

    def select_load(self) -> Tuple[DiscreteLoad, ActionEnum, bool]:
        """Return updated selection info with new load to measure at.

        Returning None load means either we have narrow enough valid interval
        for this phase, or we are hitting some other early return condition,
        (e.g. hitting min load or max load).

        Situations related to min and max load are expected in measurement
        results, but load candidates are not constrained here,
        so the handling can be centralized elsewhere.

        Note that the special re-measurements for hitting min or max load
        are unconditional (but they still disable further re-measurements).

        The implementation moves most of the logic to sub-methods.
        They also do most of logging, unless they lack the required context.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Relative width goal, considered narrow enough.
        :param selection: Object containing flags controlling one-time actions.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :type selection: SelectionInfo
        :returns: The next load rate to measure at, None to end phase;
            whether the load should be limit handled, whether to halve
            or refine next.
        :rtype: SelectionInfo
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
        if not self.bounds.clo1 and not self.bounds.chi1:
            self.debug("Doing nothing waiting for clo or chi.")
            return None, ActionEnum.WAIT, False
        if not self.bounds.clo1:
            if self.prev_action == ActionEnum.EXT_LO:
                if (load := self.prev_candidate) < self.bounds.chi1:
                    self.debug(f"Continue investigating extended lo: {load}")
                    return load, ActionEnum.EXT_LO, False
            if load := self._extend_down():
                self.debug(f"No current lower bound, extending down: {load}")
                return load, ActionEnum.EXT_LO, True
            # Hitting min load.
            return None, ActionEnum.DONE, False
        if self.prev_action == ActionEnum.EXT_HI and not self.bounds.chi1:
            if (load := self.prev_candidate) > self.bounds.clo1:
                self.debug(f"Continue investigating extended hi: {load}")
                return load, ActionEnum.EXT_HI, False
        if extend_load := self._extend_up():
            return extend_load, ActionEnum.EXT_HI, True
        if not (bisect_load := self._bisect()):
            self.prev_width = self.target_spec.discrete_width
            self.debug("Target achieved.")
            return None, ActionEnum.DONE, False
        if not self.bounds.chi2:
            self.debug(f"Not extending down, so doing bisect: {bisect_load}")
            return bisect_load, ActionEnum.BISECT, False
        # Not hitting min load, so extend_load cannot be None.
        if (extend_load := self._extend_down()) > bisect_load:
            self.debug(f"Preferring to extend down: {extend_load}.")
            return extend_load, ActionEnum.EXT_LO, True
        # There is no realistic scenario where extending up from clo1 is better.
        self.debug(f"Preferring to bisect: {bisect_load}.")
        return bisect_load, ActionEnum.BISECT, False

    def _min_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or min load refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if self.bounds.phi1 and not self.bounds.chi1:
            if (load := self.handler.min_load) == self.bounds.phi1:
                self.debug(f"Min load refinement available: {load}")
                return load
        return None

    def _max_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or max load refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if self.bounds.plo1 and not self.bounds.clo1:
            if (load := self.handler.max_load) == self.bounds.plo1:
                self.debug(f"Max load refinement available: {load}")
                return load
        return None

    def _halve(self) -> Optional[DiscreteLoad]:
        """Return None, or load for phase halving when detected.

        There is some overlap with last bisect, but we want to select
        the same load in both cases, regardless of tightest bounds duration.

        The decision is made based purely on interval width.

        :returns: Intended load for halving, or None if this is not halving.
        :rtype: Optional[DiscreteLoad]
        """
        plo, phi = self.bounds.plo1, self.bounds.phi1
        if not plo or not phi:
            return None
        interval = DiscreteInterval(plo, phi)
        wig = interval.width_in_goals(self.target_spec.discrete_width)
        if wig > 2.0:
            return None
        if wig > 1.0:
            load = interval.middle(self.target_spec.discrete_width)
            self.debug(f"Halving available: {load}")
            return load
        if self.bounds.clo1 or self.bounds.chi1:
            return None
        if not (load := self.prev_candidate) or not plo <= load <= phi:
            return None
        self.debug(f"Halving continues: {load}")
        return load

    def _lo_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or load for lowerbound refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if not self.bounds.chi1 or not (load := self.bounds.plo1):
            return None
        if self.bounds.clo1:
            if load == self.bounds.clo1:
                return None
            interval = DiscreteInterval(self.bounds.clo1, self.bounds.chi1)
            if interval.width_in_goals(self.target_spec.discrete_width) <= 1.0:
                self.debug("Not re-measuring low when narrow alrady.")
                return None
        interval = DiscreteInterval(load, self.bounds.chi1)
        if interval.width_in_goals(self.target_spec.discrete_width) > 1.0:
            # The previous phase tightest bound would not be this far.
            return None
        self.debug(f"Lowerbound re-measurement available: {load}")
        return load

    def _hi_refine(self) -> Optional[DiscreteLoad]:
        """Return None, or load for upperbound refinement when detected.

        :returns: Intended load for refinement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if not self.bounds.clo1 or not (load := self.bounds.phi1):
            return None
        if self.bounds.chi1:
            if load == self.bounds.chi1:
                return None
            interval = DiscreteInterval(self.bounds.clo1, self.bounds.chi1)
            if interval.width_in_goals(self.target_spec.discrete_width) <= 1.0:
                self.debug("Not re-measuring high when narrow alrady.")
                return None
        interval = DiscreteInterval(self.bounds.clo1, load)
        if interval.width_in_goals(self.target_spec.discrete_width) > 1.0:
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
        if self.bounds.chi1 <= self.handler.min_load:
            self.debug("Hitting min load, exit early.")
            return None
        #        if not self.bounds.chi2:
        #            if self.bounds.chi1 < self.handler.max_load:
        #                raise RuntimeError(f"Extending down without chi2: {self.bounds!r}")
        #            self.prev_width = self.target_spec.discrete_width
        #            load = self.bounds.chi1 - self.prev_width
        #            self.debug(f"Max load got refined as high, extending down: {load}")
        #            return load
        self.prev_width = (
            self.prev_width
            if self.prev_width
            else self.target_spec.discrete_width
        )
        load = self.bounds.chi1 - self.prev_width
        # Not emitting a comment to debug here, caller knows two cases.
        return load

    def _extend_up(self) -> Optional[DiscreteLoad]:
        """Return extended width above.

        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if self.bounds.chi1:
            return None
        if self.bounds.clo1 >= self.handler.max_load:
            self.debug("Hitting max rate, we can exit.")
            return None
        #        if not self.bounds.clo2:
        #            if self.bounds.clo1 > self.handler.min_load:
        #                raise RuntimeError(f"Extending up without clo2: {self.bounds!r}")
        #            self.prev_width = self.target_spec.discrete_width
        #            load = self.bounds.clo1 + self.prev_width
        #            self.debug(f"Min load re-measured low, extending up: {load}")
        #            return load
        self.prev_width = (
            self.prev_width
            if self.prev_width
            else self.target_spec.discrete_width
        )
        load = self.bounds.clo1 + self.prev_width
        self.debug(f"No current upper bound, extending up: {load}")
        return load

    def _bisect(self) -> Optional[DiscreteLoad]:
        """Return middle rate or None if width is narrow enough.

        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        interval = DiscreteInterval(self.bounds.clo1, self.bounds.chi1)
        if (
            goals := interval.width_in_goals(self.target_spec.discrete_width)
        ) <= 1.0:
            return None
        load = interval.middle(self.target_spec.discrete_width)
        # Limit future width.
        width_lo = DiscreteInterval(self.bounds.clo1, load).discrete_width
        width_hi = DiscreteInterval(load, self.bounds.chi1).discrete_width
        self.prev_width = min(self.prev_width, max(width_lo, width_hi))
        # Not emitting a comment to debug here, caller knows two cases.
        return load
