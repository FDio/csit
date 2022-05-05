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

from .duration_and_width_scaling import DurationAndWidthScaling
from .measurement_database import MeasurementDatabase
from .receive_rate_interval import ReceiveRateInterval
from .relevant_bounds import RelevantBounds
from .selection_info import SelectionInfo
from .width_arithmetics import (
    step_down, step_up, multiple_step_down, multiple_step_up,
    half_step_up, strict_half_step_up,
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

    def __init__(self, config):
        """Store the configuration and declare dynamic fields.

        The user is allowed to mutate configuration after it is stored,
        but not when search is running.

        :param config: Structure holding multiple configuration values.
        :type config: Config
        """
        self.config = config
        self.measurer = None
        self.debug = None
        self.scaling = dict()
        self.database = None
        self.stop_time = None

    def search(self, measurer, debug=None):
        """Perform initial phase, create state object, proceed with next phases.

        Stateful arguments (measurer and debug) are stored.
        Derived objects are constructed from config.

        :param measurer: Rate provider to use by this search object.
        :param debug: Callable to optionally use instead of logging.debug().
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :type measurer: AbstractMeasurer
        :type debug: Optional[Callable[[str], None]]
        :rtype: List[ReceiveRateInterval]
        :raises RuntimeError: If total duration is larger than timeout.
        """
        self.measurer = measurer
        self.debug = logging.debug if debug is None else debug
        for index, ratio in enumerate(self.config.target_loss_ratios):
            self.scaling[ratio] = DurationAndWidthScaling(
                phases=self.config.number_of_intermediate_phases,
                initial_duration=self.config.initial_trial_duration,
                final_duration=self.config.final_trial_duration,
                final_width=self.config.final_relative_width[index],
            )
        self.stop_time = time.monotonic() + self.config.max_search_duration
        self.database = MeasurementDatabase(self.do_initial_measurements())
        self.ndrpdr_root()
        return self.database.get_results(
            ratio_list=self.config.target_loss_ratios,
            duration=self.config.final_trial_duration,
        )

    def do_initial_measurements(self):
        """Perform measurements to get enough data for full logic.

        :returns: Measurement result to consider next.
        :rtype: Iterable[ReceiveRateMeasurement]
        """
        max_rate = self.config.max_rate
        ratio = self.config.target_loss_ratios[0]
        width_goal = self.scaling[ratio].width_goal(phase=0)
        duration = self.scaling[ratio].duration(phase=0)
        measure = self.measurer.measure
        measurements = list()
        self.debug(f"First measurement at max rate: {max_rate}")
        measured = measure(duration=duration, transmit_rate=max_rate)
        measurements.append(measured)
        corrected_rr = measured.relative_receive_rate / (1.0 - ratio)
        if corrected_rr >= max_rate:
            return measurements
        mrr = self.handle_load_limits(
            corrected_rr, width_goal, None, max_rate
        )
        if mrr is None:
            self.debug(u"Warning: limits too close or goal too wide?")
            return measurements
        self.debug(f"Second measurement at (corrected) mrr: {mrr}")
        measured = measure(duration=duration, transmit_rate=mrr)
        measurements.append(measured)
        # Attempt to get narrower width.
        if measured.loss_ratio > ratio:
            corrected_rr2 = measured.relative_receive_rate / (1.0 - ratio)
            # TODO: Assert corrected_rr2 > mrr
            mrr2 = self.handle_load_limits(
                corrected_rr2, width_goal, None, mrr
            )
        else:
            mrr2 = step_up(mrr, width_goal)
            if mrr2 < max_rate:
                mrr2 = self.handle_load_limits(
                    mrr2, width_goal, mrr, max_rate
                )
            else:
                # TODO: Were we safe against rounding errors?
                self.debug(u"Mrr2 would be max rate again.")
                mrr2 = None
        if mrr2 is None:
            self.debug(u"Warning: NDR too close to max rate?")
            return measurements
        self.debug(f"Third measurement at (corrected) mrr2: {mrr2}")
        measured = measure(duration=duration, transmit_rate=mrr2)
        measurements.append(measured)
        # If mrr2 > mrr and mrr2 got zero loss,
        # it is better to do external search from mrr2 up.
        # To prevent bisection between mrr2 and max_rate,
        # we simply remove the max_rate measurement.
        # Similar logic applies to higher loss ratio goals.
        # Overall, with mrr2 measurement done, we never need
        # the first measurement done at max rate.
        measurements = measurements[1:]
        return measurements

    def ndrpdr_root(self):
        """Iterate search over ratios and phases.

        :raises RuntimeError: If total duration is larger than timeout.
        """
        for ratio in self.config.target_loss_ratios:
            self.debug(f"Focusing on ratio {ratio} now.")
            scaling = self.scaling[ratio]
            for phase in range(scaling.intermediate_phases + 1):
                self.ndrpdr_iteration(ratio, phase)
        self.debug(u"All ratios done.")

    def ndrpdr_iteration(self, ratio, phase):
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
                break
            # We have transmit rate to measure at.
            # We do not check duration versus stop_time here,
            # as some measurers can be unpredictably faster
            # than what duration suggests.
            measurement = self.measurer.measure(
                duration=current_duration,
                transmit_rate=load,
            )
            self.database.add(measurement)
        else:
            # Time is up.
            raise RuntimeError(u"Optimized search takes too long.")
        self.debug(u"Phase done.")

    def handle_load_limits(self, load, width_goal, clotr, chitr):
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
        :type clotr: Optional[Union[float, ReceiveRateMeasurement]]
        :type chitr: Optional[Union[float, ReceiveRateMeasurement]]
        :return: Adjusted load to measure at, or None if narrow enough.
        :rtype: Optional[float]
        :raises RuntimeError: If unsupported corner case is detected.
        """
        if load is None:
            return None
        min_rate, max_rate = self.config.min_rate, self.config.max_rate
        load = max(min_rate, min(max_rate, load))
        if hasattr(clotr, u"target_tr"):
            clotr = clotr.target_tr
        if hasattr(chitr, u"target_tr"):
            chitr = chitr.target_tr
        if clotr is None and chitr is None:
            load = self._handle_load_with_excludes(
                load, width_goal, min_rate, max_rate, min_ex=False, max_ex=False
            )
            return load
        if clotr is None:
            if chitr <= min_rate:
                # Expected when hitting the min load.
                return None
            if load >= chitr:
                raise RuntimeError(u"Lower load expected.")
            load = self._handle_load_with_excludes(
                load, width_goal, min_rate, chitr, min_ex=False, max_ex=True
            )
            return load
        if chitr is None:
            if clotr >= max_rate:
                # Expected when hitting the max load.
                return None
            if load <= clotr:
                raise RuntimeError(u"Higher load expected.")
            load = self._handle_load_with_excludes(
                load, width_goal, clotr, max_rate, min_ex=True, max_ex=False
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
        self, load, width_goal, minimum, maximum, min_ex, max_ex
    ):
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
            soft_min = soft_max = strict_half_step_up(minimum, width)
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

    def select_load(self, bounds, width_goal, selection):
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
        # TODO: Ensure sub-methods never return zero load, drop "is not None".
        if (load := self._min_remeas_load(bounds)) is not None:
            return SelectionInfo(load=load)
        if (load := self._max_remeas_load(bounds)) is not None:
            return SelectionInfo(load=load)
        if selection.halve:
            if (load := self._halving_load(bounds, width_goal)) is not None:
                return SelectionInfo(load=load, remeasure=selection.remeasure)
        if selection.remeasure:
            if (load := self._lo_remeas_load(bounds, width_goal)) is not None:
                return SelectionInfo(load=load)
            if (load := self._hi_remeas_load(bounds, width_goal)) is not None:
                return SelectionInfo(load=load)
        if bounds.clo1 is None:
            if (load := self._extend_down(bounds, width_goal)) is None:
                # Hitting min load.
                return SelectionInfo(load=None)
            self.debug(f"No current lower bound, extending down: {load}")
            return SelectionInfo(load=load, handle=True)
        if bounds.chi1 is None:
            load = self._extend_up(bounds, width_goal)
            return SelectionInfo(load=load, handle=load is not None)
        if (bisect_load := self._bisect(bounds, width_goal)) is None:
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

    def _min_remeas_load(self, bounds):
        """Return None, or min load remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[float]
        """
        if bounds.phi1 is not None:
            if bounds.phi1.target_tr == self.config.min_rate:
                load = self.config.min_rate
                self.debug(f"Min load remeasurement available: {load}")
                return load
        return None

    def _max_remeas_load(self, bounds):
        """Return None, or max load remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[float]
        """
        if bounds.plo1 is not None:
            if bounds.plo1.target_tr == self.config.max_rate:
                load = self.config.max_rate
                self.debug(f"Max load remeasurement available: {load}")
                return load
        return None

    def _halving_load(self, bounds, width_goal):
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
        interval = ReceiveRateInterval(tlo, thi)
        wig = interval.width_in_goals(width_goal)
        halve = 1.0 < wig <= 2.0
        force = False
        if bounds.clo1 is None and bounds.chi1 is None:
            force = True
            if not halve:
                self.debug(f"Warning: Forced to halve at wig {wig}")
        if halve or force:
            # TODO: Support autoexctraction of target_tr in util functions?
            load = strict_half_step_up(tlo.target_tr, interval.rel_tr_width)
            self.debug(f"Halving available: {load}")
            return load
        return None

    def _lo_remeas_load(self, bounds, width_goal):
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
            interval = ReceiveRateInterval(bounds.clo1, bounds.chi1)
            if interval.width_in_goals(width_goal) <= 1.0:
                # This happens when limit avoidance moved target down.
                self.debug(u"Avoiding double low re-measurement.")
                return None
        interval = ReceiveRateInterval(bounds.plo1, bounds.chi1)
        if interval.width_in_goals(width_goal) > 1.0:
            return None
        load = bounds.plo1.target_tr
        self.debug(f"Lowerbound re-measurement available: {load}")
        return load

    def _hi_remeas_load(self, bounds, width_goal):
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
            interval = ReceiveRateInterval(bounds.clo1, bounds.chi1)
            if interval.width_in_goals(width_goal) <= 1.0:
                # This happens when limit avoidance moved target up.
                self.debug(u"Avoiding double high re-measurement.")
                return None
        interval = ReceiveRateInterval(bounds.clo1, bounds.phi1)
        if interval.width_in_goals(width_goal) > 1.0:
            return None
        load = bounds.phi1.target_tr
        self.debug(f"Upperbound remeasurement available: {load}")
        return load

    def _extend_down(self, bounds, width_goal):
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
        if bounds.chi1.target_tr <= self.config.min_rate:
            self.debug(u"Hitting min load, exit early.")
            return None
        if bounds.chi2 is None:
            if bounds.chi1.target_tr < self.config.max_rate:
                raise RuntimeError(f"Extending down without chi2: {bounds!r}")
            load = step_down(bounds.chi1.target_tr, width_goal)
            self.debug(f"Max load re-measured high, extending down: {load}")
            return load
        # TODO: Explain why are we ignoring possible phi1.
        old_width = ReceiveRateInterval(bounds.chi1, bounds.chi2).rel_tr_width
        # Slight mismatch is expected with our current width rounding.
        old_width = max(old_width, width_goal)
        load = multiple_step_down(
            bounds.chi1.target_tr, old_width, self.config.expansion_coefficient
        )
        # Not emitting a comment to debug here, caller knows two cases.
        return load

    def _extend_up(self, bounds, width_goal):
        """Return extended width above.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if bounds.clo1.target_tr >= self.config.max_rate:
            self.debug(u"Hitting max rate, we can exit.")
            return None
        if bounds.clo2 is None:
            if bounds.clo1.target_tr > self.config.min_rate:
                raise RuntimeError(f"Extending up without clo2: {bounds!r}")
            load = step_up(bounds.clo1.target_tr, width_goal)
            self.debug(f"Min load re-measured low, extending down: {load}")
            return load
        # TODO: Explain why are we ignoring possible plo1.
        old_width = ReceiveRateInterval(bounds.clo2, bounds.clo1).rel_tr_width
        # Slight mismatch is expected with our current width rounding.
        old_width = max(old_width, width_goal)
        load = multiple_step_up(
            bounds.clo1.target_tr, old_width, self.config.expansion_coefficient
        )
        self.debug(f"No current upper bound, extending up: {load}")
        return load

    def _bisect(self, bounds, width_goal):
        """Return middle rate or None if width is narrow enough.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        interval = ReceiveRateInterval(bounds.clo1, bounds.chi1)
        if (width := interval.rel_tr_width) <= width_goal:
            goals = interval.width_in_goals(width_goal)
            self.debug(f"Width {goals} goals small enough, phase can end now.")
            return None
        load = half_step_up(bounds.clo1.target_tr, width, width_goal)
        # Not emitting a comment to debug here, caller knows two cases.
        return load
