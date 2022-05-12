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

"""Module defining MultipleLossRatioSearch class."""

import logging
import time

from typing import Callable, List, Optional, Union

from .trial_measurement.abstract_measurer import AbstractMeasurer
from .config import Config
from .comparable_measurement_result import ComparableMeasurementResult as Result
from .duration_and_width_scaling import DurationAndWidthScaling
from .measurement_database import MeasurementDatabase
from .measurement_interval import MeasurementInterval
from .relevant_bounds import RelevantBounds
from .selection_info import SelectionInfo
from .width_arithmetics import (
    step_down, step_up, multiple_step_down, multiple_step_up,
    half_step_down, strict_half_step_down,
)


class MultipleLossRatioSearch:
    """Optimized binary search algorithm for finding bounds for multiple ratios.

    FIXME: Update.

    Traditional binary search algorithm needs initial interval
    (lower and upper bound), and returns final interval after bisecting
    (until some exit condition is met).
    The exit condition is usually related to the interval width,
    (upper bound value minus lower bound value).

    The optimized algorithm contains several improvements
    aimed to reduce overall search time.

    One improvement is searching for multiple intervals at once.
    The intervals differ by the target loss ratio. Lower bound
    has to have equal or smaller loss ratio, upper bound has to have larger.

    Next improvement is that the initial interval does not need to be valid.
    Imagine initial interval (10, 11) where loss at 11 is smaller
    than the searched ratio.
    The algorithm will try (11, 13) interval next, and if 13 is still smaller,
    (13, 17) and so on, doubling width until the upper bound is valid.
    The part when interval expands is called external search,
    the part when interval is bisected is called internal search.

    Next improvement is that trial measurements at small trial duration
    can be used to find a reasonable interval for full trial duration search.
    This results in more trials performed, but smaller overall duration
    in general.

    Next improvement is bisecting in logarithmic quantities,
    so that exit criteria can be independent of measurement units.

    Next improvement is basing the initial interval on receive rates.

    Final improvement is exiting early if the minimal value
    is not a valid lower bound.

    The complete search consist of several phases,
    each phase performing several trial measurements.
    Initial phase creates initial interval based on receive rates
    at maximum rate and at maximum receive rate (MRR).
    Final phase and preceding intermediate phases are performing
    external and internal search steps,
    each resulting interval is the starting point for the next phase.
    The resulting intervals of final phase is the result of the whole algorithm.

    Each non-initial phase uses its own trial duration.
    Any non-initial phase stops searching (for all ratios independently)
    when minimum is not a valid lower bound (at current duration),
    or all of the following is true:
    Both bounds are valid, bounds are measured at the current phase
    trial duration, interval width is less than the width goal
    for current phase.

    TODO: Review and update this docstring according to rst docs.
    """

    def __init__(self, config: Config):
        """Store the configuration and declare dynamic fields.

        The user is allowed to mutate configuration after it is stored,
        but not when search is running.

        :param config: Structure holding multiple configuration values.
        :type config: config.Config
        """
        self.config = config
        self.measurer = None
        self.debug = None
        self.scaling = dict()
        self.database = None
        self.stop_time = None

    def search(
        self,
        measurer: AbstractMeasurer,
        debug: Optional[Callable[[str], None]] = None,
    ) -> List[MeasurementInterval]:
        """Perform initial phase, create state object, proceed with next phases.

        Stateful arguments (measurer and debug) are stored.
        Derived objects are constructed from config.

        :param measurer: Rate provider to use by this search object.
        :param debug: Callable to optionally use instead of logging.debug().
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :type measurer: AbstractMeasurer
        :type debug: Optional[Callable[[str], None]]
        :rtype: List[MeasurementInterval]
        :raises RuntimeError: If total duration is larger than timeout.
        """
        self.measurer = measurer
        self.debug = logging.debug if debug is None else debug
        for index, ratio in enumerate(self.config.target_loss_ratios):
            self.scaling[ratio] = DurationAndWidthScaling(
                intermediate_phases=self.config.number_of_intermediate_phases,
                initial_duration=self.config.initial_trial_duration,
                final_duration=self.config.final_trial_duration,
                final_width=self.config.final_relative_width[index],
            )
        self.stop_time = time.monotonic() + self.config.max_search_duration
        self.database = MeasurementDatabase(self.do_initial_measurements())
        self.ndrpdr_root()
        return self.database.get_intervals(
            ratio_list=self.config.target_loss_ratios,
            duration=self.config.final_trial_duration,
        )

    def measure(self, duration: float, intended_load: float) -> Result:
        """Call measurer and cast the result to be comparable.

        :param duration: Trial duration [s].
        :param intended_load: Intended rate of transactions (packets) [tps].
        :type duration: float
        :type intended_load: float
        :returns: Structure detailing the result of the measurement.
        :rtype: comparable_measurement_result.ComparableMeasurementResult
        """
        result = self.measurer.measure(duration, intended_load)
        return Result.from_result(result)


    def do_initial_measurements(self) -> List[Result]:
        """Perform measurements to get enough data for full logic.

        Measurements are done with first intermediate phase in mind,
        so initial duration is used, and width goal (for phase 0)
        for first ratio is used to avoid wastefully narrow intervals.

        Forwarding rate is used as a hint for next intended load,
        the relative quantity in case load has different units.
        When the first ratio is non-zero, correction is needed
        (forwarding rate is only good hint for zero ratio).
        The correction is conservative (all increase in load turns to losses),
        so the same logic (step_up) as for aiming at interval width can be used.

        :returns: Measurement results to consider next.
        :rtype: List[ComparableMeasurementResult]
        """
        max_load = self.config.max_load
        ratio = self.config.target_loss_ratios[0]
        width_goal = self.scaling[ratio].width_goal(phase=0)
        duration = self.scaling[ratio].duration(phase=0)
        measurements = list()
        self.debug(f"First measurement at max rate: {max_load}")
        measured = self.measure(duration=duration, intended_load=max_load)
        measurements.append(measured)
        corrected_rr = step_up(measured.relative_forwarding_rate, ratio)
        if corrected_rr >= max_load:
            self.debug(u"Small loss, no other initial measurements are needed.")
            return measurements
        mrr = self.handle_load_limits(
            corrected_rr, width_goal, None, max_load
        )
        if mrr is None:
            self.debug(u"Warning: limits too close or goal too wide?")
            return measurements
        self.debug(f"Second measurement at (corrected) mrr: {mrr}")
        measured = self.measure(duration=duration, intended_load=mrr)
        measurements.append(measured)
        # Attempt to get narrower width.
        if measured.loss_ratio > ratio:
            corrected_rr2 = step_up(measured.relative_forwarding_rate, ratio)
            # TODO: Assert corrected_rr2 > mrr?
            mrr2 = self.handle_load_limits(
                corrected_rr2, width_goal, None, mrr
            )
        else:
            mrr2 = step_up(mrr, width_goal)
            if mrr2 < max_load:
                mrr2 = self.handle_load_limits(
                    mrr2, width_goal, mrr, max_load
                )
            else:
                # TODO: Were we safe against rounding errors?
                self.debug(u"Mrr2 would be max rate again.")
                mrr2 = None
        if mrr2 is None:
            self.debug(u"Warning: NDR too close to max rate?")
            return measurements
        self.debug(f"Third measurement at (corrected) mrr2: {mrr2}")
        measured = self.measure(duration=duration, intended_load=mrr2)
        measurements.append(measured)
        # If mrr2 > mrr and mrr2 got zero loss,
        # it is better to do external search from mrr2 up.
        # To prevent bisection between mrr2 and max_load,
        # we simply remove the max_load measurement.
        # Similar logic applies to higher loss ratio goals.
        # Overall, with mrr2 measurement done, we never need
        # the first measurement done at max rate.
        measurements = measurements[1:]
        return measurements

    def ndrpdr_root(self) -> None:
        """Iterate search over ratios and phases.

        :raises RuntimeError: If total duration is larger than timeout.
        """
        for ratio in self.config.target_loss_ratios:
            self.debug(f"Focusing on ratio {ratio} now.")
            scaling = self.scaling[ratio]
            for phase in range(scaling.intermediate_phases + 1):
                self.ndrpdr_iteration(ratio, phase)
        self.debug(u"All ratios done.")

    def ndrpdr_iteration(self, ratio: float, phase: int) -> None:
        """Search for narrow enough bounds for this ratio at this phase.

        :param ratio: Target loss ratio the bounds should encompass.
        :param phase: Current phase number, implies duration and width goal.
        :type ratio: float
        :type phase: int
        """
        scaling = self.scaling[ratio]
        width_goal = scaling.width_goal(phase)
        current_duration = scaling.duration(phase)
        previous_duration = scaling.duration(phase - 1) if phase else None
        self.debug(
            f"Starting phase for ratio {ratio} with duration {current_duration}"
            f" and relative width goal {width_goal}."
        )
        selection = SelectionInfo(halve=True, remeasure=True)
        while time.monotonic() < self.stop_time:
            bounds = RelevantBounds.from_database(
                self.database, ratio, current_duration, previous_duration
            )
            selection = self.select_load(bounds, width_goal, selection)
            load = selection.load
            if selection.handle:
                load = self.handle_load_limits(
                    load, width_goal, bounds.clo1, bounds.chi1
                )
            if load is None:
                self.debug(u"Phase done.")
                break
            # We have transmit rate to measure at.
            # We do not check duration versus stop_time here,
            # as some measurers can be unpredictably faster
            # than what duration suggests.
            measurement = self.measure(
                duration=current_duration,
                intended_load=load,
            )
            self.database.add(measurement)
        else:
            # Time is up.
            raise RuntimeError(u"Optimized search takes too long.")

    def handle_load_limits(
        self,
        load: Optional[float],
        width_goal: float,
        clotr: Optional[Union[float, Result]],
        chitr: Optional[Union[float, Result]],
    ) -> Optional[float]:
        """Return new target transmit rate after considering min and max rate.

        Not only we want to avoid measuring outside minmax interval,
        we also want to avoid measuring too close to limits and bounds.
        We either round or return None, depending on hints from bound loads.

        When rounding away from hard limits, we may end up being
        too close to already measured bound.
        In this case, pick a midpoint between the bound and the limit.
        The caller should have chosen (unrounded) load far enough from bounds.

        The last two arguments are just loads (not full measurement result)
        to allow callers to exclude come load without measuring them.
        As a convenience full results are also supported,
        so that callers do not need to care about None when extracting load.

        :param load: Target transmit rate candidate from select_load.
        :param width_goal: Relative width goal, considered narrow enough.
        :param clotr: Target TR of current tightest lower bound.
        :param chitr: Target TR of current tightest upper bound.
        :type load: Optional[float]
        :type width_goal: float
        :type clotr: Optional[Union[float, ComparableMeasurementResult]]
        :type chitr: Optional[Union[float, ComparableMeasurementResult]]
        :return: Adjusted load to measure at, or None if narrow enough.
        :rtype: Optional[float]
        :raises RuntimeError: If unsupported corner case is detected.
        """
        if load is None:
            raise RuntimeError(u"Got None load to handle.")
        min_load, max_load = self.config.min_load, self.config.max_load
        load = max(min_load, min(max_load, load))
        if hasattr(clotr, u"intended_load"):
            clotr = clotr.intended_load
        if hasattr(chitr, u"intended_load"):
            chitr = chitr.intended_load
        if clotr is None and chitr is None:
            load = self._handle_load_with_excludes(
                load, width_goal, min_load, max_load, min_ex=False, max_ex=False
            )
            return load
        if clotr is None:
            if chitr <= min_load:
                # Expected when hitting the min load.
                return None
            if load >= chitr:
                raise RuntimeError(u"Lower load expected.")
            load = self._handle_load_with_excludes(
                load, width_goal, min_load, chitr, min_ex=False, max_ex=True
            )
            return load
        if chitr is None:
            if clotr >= max_load:
                # Expected when hitting the max load.
                return None
            if load <= clotr:
                raise RuntimeError(u"Higher load expected.")
            load = self._handle_load_with_excludes(
                load, width_goal, clotr, max_load, min_ex=True, max_ex=False
            )
            return load
        if load <= clotr:
            raise RuntimeError(u"Higher load expected.")
        if load >= chitr:
            raise RuntimeError(u"Lower load expected.")
        load = self._handle_load_with_excludes(
            load, width_goal, clotr, chitr, min_ex=True, max_ex=True
        )
        return load

    def _handle_load_with_excludes(
        self,
        load: float,
        width_goal: float,
        minimum: float,
        maximum: float,
        min_ex: bool,
        max_ex: bool,
    ) -> Optional[float]:
        """Round load if too close to limits, respecting exclusions.

        This is a reusable block. Limits may come from previous bounds
        or from hard load limits. When coming from hard limits,
        rounding to the limit value us allowed. When coming from bounds,
        rounding to that is not allowed (given by the setting the _ex flag).

        :param load: The candidate intended load before accounting for limits.
        :param width_goal: Relative width of area around the limits to avoid.
        :param minimum: The lower limit to round around.
        :param maximum: The upper limit to round around.
        :param min_ex: If false, rounding to the minimum is allowed.
        :param max_ex: If false, rounding to the maximum is allowed.
        :type load: float
        :type width_goal: float
        :type minimum: float
        :type maximum: float
        :type min_ex: bool
        :type max_ex: bool
        :returns: Adjusted load value, or None if narrow enough.
        :rtype: Optional[float]
        :raises RuntimeError: If internal inconsistency is detected.
        """
        if not minimum <= load <= maximum:
            raise RuntimeError(u"Please do not call with irrelevant load.")
        width = (maximum - minimum) / maximum
        if width <= width_goal:
            self.debug(u"Warning: Handling called with wide goal.")
            if not min_ex:
                self.debug(u"Minimum not excluded, rounding to it.")
                return minimum
            if not max_ex:
                self.debug(u"Maximum not excluded, rounding to it.")
                return maximum
            self.debug(u"Both limits excluded, narrow enough.")
            return None
        # Using multiple_* versions to apply rounding constant.
        soft_min = multiple_step_up(minimum, width_goal, 1.0)
        soft_max = multiple_step_down(maximum, width_goal, 1.0)
        if soft_min > soft_max:
            self.debug(u"Whole interval is less than two goals.")
            soft_min = soft_max = strict_half_step_down(maximum, width)
        if load < soft_min:
            if min_ex:
                self.debug(u"Min excluded, rounding to soft min.")
                return soft_min
            self.debug(u"Min not excluded, rounding to minimum.")
            return minimum
        if load > soft_max:
            if max_ex:
                self.debug(u"Max excluded, rounding to soft max.")
                return soft_max
            self.debug(u"Max not excluded, rounding to maximum.")
            return maximum
        # Far enough from limits, rounding not needed.
        return load

    def select_load(
        self,
        bounds: RelevantBounds,
        width_goal: float,
        selection: SelectionInfo,
    ) -> SelectionInfo:
        """Return updated selection info with new load to measure at.

        Returning None load means either we have narrow enough valid interval
        for this phase, or we are hitting some other early return condition,
        (e.g. hitting min load or max load).

        Situations related to min and max rate are expected in measurement
        results, but load candidates are not constrained here,
        so the handling can be centralized elsewhere.

        Note that the special re-measurements for hitting min or max load
        are unconditional (but they still disable further re-measurements).

        The implementation moves most of the logic to sub-methods.
        They also do most of logging, unless they lack the required context.
        The core alre relies on every (non-None) load being positive.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Relative width goal, considered narrow enough.
        :param selection: Object containing flags controlling one-time actions.
        :type bounds: RelevantBounds
        :type width_goal: float
        :type selection: SelectionInfo
        :returns: The next load rate to measure at, None to end phase;
            whether the load should be limit handled, whether to halve
            or remeasure next.
        :rtype: SelectionInfo
        :raises RuntimeError: If internal logic error is detected.
        """
        if load := self._min_remeas_load(bounds):
            return SelectionInfo(load=load)
        if load := self._max_remeas_load(bounds):
            return SelectionInfo(load=load)
        if selection.halve:
            if load := self._halving_load(bounds, width_goal):
                return SelectionInfo(load=load, remeasure=selection.remeasure)
        if selection.remeasure:
            if load := self._lo_remeas_load(bounds, width_goal):
                return SelectionInfo(load=load)
            if load := self._hi_remeas_load(bounds, width_goal):
                return SelectionInfo(load=load)
        if bounds.clo1 is None:
            if load := self._extend_down(bounds, width_goal):
                self.debug(f"No current lower bound, extending down: {load}")
                return SelectionInfo(load=load, handle=True)
            # Hitting min load.
            return SelectionInfo(load=None)
        if bounds.chi1 is None:
            load = self._extend_up(bounds, width_goal)
            return SelectionInfo(load=load, handle=load is not None)
        if not (bisect_load := self._bisect(bounds, width_goal)):
            return SelectionInfo(load=None)
        if bounds.chi2 is None:
            self.debug(f"Not extending down, so doing bisect: {bisect_load}")
            return SelectionInfo(load=bisect_load)
        # Not hitting min load, so extend_load cannot be None.
        if (extend_load := self._extend_down(bounds, width_goal)) > bisect_load:
            self.debug(f"Preferring to extend down: {extend_load}.")
            # Does not need to handled.
            return SelectionInfo(load=extend_load)
        self.debug(f"Preferring to bisect: {bisect_load}.")
        return SelectionInfo(load=bisect_load)

    def _min_remeas_load(self, bounds: RelevantBounds) -> Optional[float]:
        """Return None, or min load remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[float]
        """
        if bounds.phi1 is not None:
            if bounds.phi1.intended_load == self.config.min_load:
                load = self.config.min_load
                self.debug(f"Min load remeasurement available: {load}")
                return load
        return None

    def _max_remeas_load(self, bounds: RelevantBounds) -> Optional[float]:
        """Return None, or max load remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[float]
        """
        if bounds.plo1 is not None:
            if bounds.plo1.intended_load == self.config.max_load:
                load = self.config.max_load
                self.debug(f"Max load remeasurement available: {load}")
                return load
        return None

    def _halving_load(
        self, bounds: RelevantBounds, width_goal: float
    ) -> Optional[float]:
        """Return None, or load for phase halving when detected.

        There is some overlap with last bisect, but we want to select
        the same load in both cases, regardless of tightest bounds duration.

        The decision is made based purely on interval width.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: Intended load for halving, or None if this is not halving.
        :rtype: Optional[float]
        """
        tlo, thi = bounds.clo1, bounds.chi1
        # Use plo1 if tighter.
        if bounds.plo1 is not None and (tlo is None or tlo < bounds.plo1):
            tlo = bounds.plo1
        # Use phi1 if tighter.
        if bounds.phi1 is not None and (thi is None or thi > bounds.phi1):
            thi = bounds.phi1
        if tlo is None or thi is None:
            return None
        interval = MeasurementInterval(tlo, thi)
        wig = interval.width_in_goals(width_goal)
        halve = 1.0 < wig <= 2.0
        force = False
        if bounds.clo1 is None and bounds.chi1 is None:
            force = True
            if not halve:
                self.debug(f"Warning: Forced to halve at wig {wig}")
        if halve or force:
            load = strict_half_step_down(
                thi.intended_load, interval.relative_width
            )
            self.debug(f"Halving available: {load}")
            return load
        return None

    def _lo_remeas_load(
        self, bounds: RelevantBounds, width_goal: float
    ) -> Optional[float]:
        """Return None, or load for lowerbound remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[float]
        """
        # TODO: Document the logic.
        if bounds.plo1 is None or bounds.chi1 is None:
            return None
        if bounds.clo1 is not None:
            interval = MeasurementInterval(bounds.clo1, bounds.chi1)
            if interval.width_in_goals(width_goal) <= 1.0:
                # This happens when limit avoidance moved target down.
                self.debug(u"Avoiding double low re-measurement.")
                return None
        interval = MeasurementInterval(bounds.plo1, bounds.chi1)
        if interval.width_in_goals(width_goal) > 1.0:
            return None
        load = bounds.plo1.intended_load
        self.debug(f"Lowerbound re-measurement available: {load}")
        return load

    def _hi_remeas_load(
        self, bounds: RelevantBounds, width_goal: float
    ) -> Optional[float]:
        """Return None, or load for upperbound remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[float]
        """
        # TODO: Document the logic.
        if bounds.phi1 is None or bounds.clo1 is None:
            return None
        if bounds.chi1 is not None:
            interval = MeasurementInterval(bounds.clo1, bounds.chi1)
            if interval.width_in_goals(width_goal) <= 1.0:
                # This happens when limit avoidance moved target up.
                self.debug(u"Avoiding double high re-measurement.")
                return None
        interval = MeasurementInterval(bounds.clo1, bounds.phi1)
        if interval.width_in_goals(width_goal) > 1.0:
            return None
        load = bounds.phi1.intended_load
        self.debug(f"Upperbound remeasurement available: {load}")
        return load

    def _extend_down(
        self, bounds: RelevantBounds, width_goal: float
    ) -> Optional[float]:
        """Return extended width below.

        The only case when this returns None is when hitting min load.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if bounds.chi1.intended_load <= self.config.min_load:
            self.debug(u"Hitting min load, exit early.")
            return None
        if bounds.chi2 is None:
            if bounds.chi1.intended_load < self.config.max_load:
                raise RuntimeError(f"Extending down without chi2: {bounds!r}")
            load = step_down(bounds.chi1.intended_load, width_goal)
            self.debug(f"Max load re-measured high, extending down: {load}")
            return load
        # TODO: Explain why are we ignoring possible phi1.
        old_width = MeasurementInterval(bounds.chi1, bounds.chi2).relative_width
        # Slight mismatch is expected with our current width rounding.
        old_width = max(old_width, width_goal)
        load = multiple_step_down(
            bounds.chi1.intended_load, old_width, self.config.expansion_coefficient
        )
        # Not emitting a comment to debug here, caller knows two cases.
        return load

    def _extend_up(
        self, bounds: RelevantBounds, width_goal: float
    ) -> Optional[float]:
        """Return extended width above.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if bounds.clo1.intended_load >= self.config.max_load:
            self.debug(u"Hitting max rate, we can exit.")
            return None
        if bounds.clo2 is None:
            if bounds.clo1.intended_load > self.config.min_load:
                raise RuntimeError(f"Extending up without clo2: {bounds!r}")
            load = step_up(bounds.clo1.intended_load, width_goal)
            self.debug(f"Min load re-measured low, extending down: {load}")
            return load
        # TODO: Explain why are we ignoring possible plo1.
        old_width = MeasurementInterval(bounds.clo2, bounds.clo1).relative_width
        # Slight mismatch is expected with our current width rounding.
        old_width = max(old_width, width_goal)
        load = multiple_step_up(
            bounds.clo1.intended_load, old_width, self.config.expansion_coefficient
        )
        self.debug(f"No current upper bound, extending up: {load}")
        return load

    def _bisect(
        self, bounds: RelevantBounds, width_goal: float
    ) -> Optional[float]:
        """Return middle rate or None if width is narrow enough.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        interval = MeasurementInterval(bounds.clo1, bounds.chi1)
        if (width := interval.relative_width) <= width_goal:
            goals = interval.width_in_goals(width_goal)
            self.debug(f"Width {goals} goals small enough, phase can end now.")
            return None
        load = half_step_down(bounds.chi1.intended_load, width, width_goal)
        # Not emitting a comment to debug here, caller knows two cases.
        return load
