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

from .DurationAndWidthScaling import DurationAndWidthScaling
from .MeasurementDatabase import MeasurementDatabase
from .OtherConfig import OtherConfig
from .ReceiveRateInterval import ReceiveRateInterval
from .RelevantBounds import RelevantBounds
from .WidthArithmetics import (
    step_down,
    step_up,
    multiple_step_down,
    multiple_step_up,
    half_step_up,
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

    def __init__(
            self, measurer, final_relative_width=0.005,
            final_trial_duration=30.0, initial_trial_duration=1.0,
            number_of_intermediate_phases=2, timeout=600.0, debug=None,
            expansion_coefficient=4.0):
        """Store the measurer object and additional arguments.

        Also, values related to phase scaling are precomputed.

        :param measurer: Rate provider to use by this search object.
        :param final_relative_width: Final lower bound transmit rate
            cannot be more distant that this multiple of upper bound [1].
        :param final_trial_duration: Trial duration for the final phase [s].
        :param initial_trial_duration: Trial duration for the initial phase
            and also for the first intermediate phase [s].
        :param number_of_intermediate_phases: Number of intermediate phases
            to perform before the final phase [1].
        :param timeout: The search will fail itself when not finished
            before this overall time [s].
        :param debug: Callable to use instead of logging.debug().
        :param expansion_coefficient: External search multiplies width by this.
        :type measurer: AbstractMeasurer.AbstractMeasurer
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: float
        :type number_of_intermediate_phases: int
        :type timeout: float
        :type debug: Optional[Callable[[str], None]]
        :type expansion_coefficient: float
        """
        self.measurer = measurer
        self.debug = logging.debug if debug is None else debug
        self.expansion_coefficient = float(expansion_coefficient)
        self.scaling = DurationAndWidthScaling(
            phases=number_of_intermediate_phases,
            initial_duration=initial_trial_duration,
            final_duration=final_trial_duration,
            final_width=final_relative_width,
        )
        self.timeout = float(timeout)
        self.config = None
        self.database = None

    def narrow_down_intervals(self, min_rate, max_rate, packet_loss_ratios):
        """Perform initial phase, create state object, proceed with next phases.

        The current implementation requires the ratios so be unique and sorted.
        Also non-empty.

        :param min_rate: Minimal target transmit rate [tps].
        :param max_rate: Maximal target transmit rate [tps].
        :param packet_loss_ratios: Target ratios of packets loss to locate.
        :type min_rate: float
        :type max_rate: float
        :type packet_loss_ratios: Iterable[float]
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :rtype: List[ReceiveRateInterval]
        :raises RuntimeError: If total duration is larger than timeout.
            Or if ratios list is (empty or) not sorted or unique.
        """
        self.config = OtherConfig(
            packet_loss_ratios=packet_loss_ratios,
            min_rate=min_rate,
            max_rate=max_rate,
            timeout=self.timeout,
        )
        self.database = MeasurementDatabase(self.do_initial_measurements())
        self.ndrpdr_root()
        return self.database.get_results(
            ratio_list=packet_loss_ratios,
            duration=self.scaling.final_duration,
        )

    def do_initial_measurements(self):
        """Perform measurements to get enough data for full logic.

        :returns: Measurement result to consider next.
        :rtype: Iterable[ReceiveRateMeasurement]
        """
        measurements = list()
        self.debug(f"First measurement at max rate: {self.config.max_rate}")
        measured = self.measurer.measure(
            duration=self.scaling.initial_duration,
            transmit_rate=self.config.max_rate,
        )
        measurements.append(measured)
        width_goal = self.scaling.width_goal(phase=0)
        correction_factor = 1.0 / (1.0 - self.config.packet_loss_ratios[0])
        corrected_rr = measured.relative_receive_rate * correction_factor
        if corrected_rr >= self.config.max_rate:
            return measurements
        mrr = self.handle_load_limits(
            corrected_rr, width_goal, None, self.config.max_rate
        )
        if mrr is None:
            self.debug(u"Warning: hard interval narrow or goal wide?")
            return measurements
        self.debug(f"Second measurement at (corrected) mrr: {mrr}")
        measured = self.measurer.measure(
            duration=self.scaling.initial_duration,
            transmit_rate=mrr,
        )
        measurements.append(measured)
        # Attempt to get narrower width.
        if measured.loss_ratio > self.config.packet_loss_ratios[0]:
            corrected_rr2 = measured.relative_receive_rate * correction_factor
            # TODO: Assert corrected_rr2 > mrr
            mrr2 = self.handle_load_limits(
                corrected_rr2, width_goal, None, mrr
            )
        else:
            mrr2 = step_up(mrr, width_goal)
            if mrr2 < self.config.max_rate:
                mrr2 = self.handle_load_limits(
                    mrr2, width_goal, mrr, self.config.max_rate
                )
            else:
                # TODO: Were we safe against rounding errors?
                self.debug(u"Mrr2 would be max rate again.")
                mrr2 = None
        if mrr2 is None:
            self.debug(u"Warning: NDR too close to max rate?")
            return measurements
        self.debug(f"Third measurement at (corrected) mrr2: {mrr2}")
        measured = self.measurer.measure(
            duration=self.scaling.initial_duration,
            transmit_rate=mrr2,
        )
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
        for ratio in self.config.packet_loss_ratios:
            self.debug(f"Focusing on ratio {ratio} now.")
            for phase in range(self.scaling.intermediate_phases + 1):
                self.ndrpdr_iteration(ratio, phase)
        self.debug(u"All ratios done.")

    def ndrpdr_iteration(self, ratio, phase):
        """Search for narrow enough bounds for this ratio at this phase.

        :param ratio: Target loss ratio the bounds should encompass.
        :param phase: Current phase number, implies duration and width goal.
        :type ratio: float
        :type phase: int
        """
        width_goal = self.scaling.width_goal(phase)
        current_duration = self.scaling.duration(phase)
        previous_duration = self.scaling.duration(phase - 1) if phase else None
        self.debug(
            f"Starting phase with {current_duration} duration"
            f" and {width_goal} relative width goal."
        )
        # TODO: Add failing fast.
        while time.monotonic() < self.config.stop_time:
            bounds = RelevantBounds.from_database(
                self.database, ratio, current_duration, previous_duration
            )
            load = self.select_load(bounds, width_goal)
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
            if load >= chitr:
                raise RuntimeError(u"Lower load expected.")
            if chitr <= min_rate:
                self.debug(u"Warning: detect hitting min rate sooner?")
                return None
            load = self._handle_load_with_excludes(
                load, width_goal, min_rate, chitr, min_ex=False, max_ex=True
            )
            return load
        if chitr is None:
            if load <= clotr:
                raise RuntimeError(u"Higher load expected.")
            if clotr >= max_rate:
                self.debug(u"Warning: detect hitting max rate sooner?")
                return None
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
            self.debug(u"Warning: Rounding called when narrow enough.")
            if not min_ex:
                self.debug(u"Minimum not excluded, rounding to it.")
                return minimum
            if not max_ex:
                self.debug(u"Maximum not excluded, rounding to it.")
                return maximum
            self.debug(u"Both limits excluded, narrow enough.")
            return None
        soft_min = step_up(minimum, width_goal)
        soft_max = step_down(maximum, width_goal)
        if soft_min > soft_max:
            self.debug(u"Whole interval is less than two goals.")
            soft_min = soft_max = half_step_up(minimum, width)
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
        self.debug(u"Far enough from limits, rounding not needed.")
        return load

    def select_load(self, bounds, width_goal):
        """Return None or new target_tr to measure at.

        Returning None means either we have narrow enough valid interval
        for this phase, or we are hitting some other early return condition.
        TODO: Are there other conditions here?

        Situations related to min and max rate are expected in measurement
        results, but load candidates are not constrained here,
        so the handling can be centralized elsewhere.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Relative width goal, considered narrow enough.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: The next load rate to measure at, None to end phase.
        :rtype: Optional[float]
        :raises RuntimeError: If database inconsistency is detected.
        """
        # Detecting cases in order they can appear chronologically for phase.
        load = self._get_halving_load(bounds, width_goal)
        if load is not None:
            self.debug(f"Halving available: {load}")
            return load
        load = self._get_lo_remeas_load(bounds, width_goal)
        if load is not None:
            self.debug(f"Lowerbound remeasurement available: {load}")
            return load
        load = self._get_min_remeas_load(bounds)
        if load is not None:
            self.debug(f"Min load remeasurement available: {load}")
            return load
        load = self._get_hi_remeas_load(bounds, width_goal)
        if load is not None:
            self.debug(f"Upperbound remeasurement available: {load}")
            return load
        load = self._get_max_remeas_load(bounds)
        if load is not None:
            self.debug(f"Max load remeasurement available: {load}")
            return load
        if bounds.clo1 is None:
            load = self._extend_down(bounds, width_goal)
            if load is None:
                self.debug(u"Probably hitting min load, FIXME")
                return None
            self.debug(f"No current lower bound, extending down: {load}")
            return load
        if bounds.chi1 is None:
            load = self._extend_up(bounds, width_goal)
            if load is None:
                self.debug(u"Probably hitting max load, FIXME")
                return None
            self.debug(f"No current upper bound, extending up: {load}")
            return load
        bisect_load = self._bisect(bounds, width_goal)
        if bisect_load is None:
            self.debug(u"Width small enough, no more bisecting needed.")
            return None
        if bounds.chi2 is None:
            self.debug(f"Not extending down, so doing bisect: {bisect_load}")
            return bisect_load
        extend_load = self._extend_down(bounds, width_goal)
        if extend_load is not None and extend_load > bisect_load:
            self.debug(f"Preferring to extend down: {extend_load}.")
            return extend_load
        self.debug(f"Preferring to bisect: {bisect_load}.")
        return bisect_load

    def _get_halving_load(self, bounds, width_goal):
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
        # Use phi if tighter.
        if bounds.phi1 is not None and (thi is None or thi > bounds.phi1):
            thi = bounds.phi1
        if tlo is None or thi is None:
            return None
        interval = ReceiveRateInterval(tlo, thi)
        wig = interval.width_in_goals(width_goal)
        if 1.0 < wig <= 2.0:
            # TODO: Support autoexctraction of target_tr in util functions?
            load = half_step_up(
                tlo.target_tr, interval.rel_tr_width, width_goal
            )
            self.debug(f"Halving load found: {load}")
            return load
        return None

    def _get_min_remeas_load(self, bounds):
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
                return self.config.min_rate
        return None

    def _get_lo_remeas_load(self, bounds, width_goal):
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
        interval = ReceiveRateInterval(bounds.plo1, bounds.chi1)
        if interval.width_in_goals(width_goal) > 1.0:
            return None
        load = bounds.plo1.target_tr
        self.debug(f"Low remeasure candidate found: {load}")
        return load

    def _get_max_remeas_load(self, bounds):
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
                return self.config.max_rate
        return None

    def _get_hi_remeas_load(self, bounds, width_goal):
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
        interval = ReceiveRateInterval(bounds.clo1, bounds.phi1)
        if interval.width_in_goals(width_goal) > 1.0:
            return None
        load = bounds.phi1.target_tr
        self.debug(f"High remeasure candidate found: {load}")
        return load

    def _extend_down(self, bounds, width_goal):
        """Return extended width below.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if bounds.chi2 is None:
            if bounds.chi1.target_tr < self.config.max_rate:
                raise RuntimeError(f"Extending down without chi2: {bounds!r}")
            self.debug(u"Assuming max rate just got remeasured high.")
            load = step_down(bounds.chi1.target_tr, width_goal)
            return load
        # TODO: Explain why are we ignoring possible phi1.
        old_width = ReceiveRateInterval(bounds.chi1, bounds.chi2).rel_tr_width
        if old_width < width_goal:
            # The following is possible with out width rounding.
            self.debug(f"Width {old_width} < {width_goal} in _extend_down.")
        load = multiple_step_down(
            bounds.chi1.target_tr, old_width, self.expansion_coefficient
        )
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
        if bounds.clo2 is None:
            if bounds.clo1.target_tr >= self.config.max_rate:
                self.debug(u"Assuming we are hitting max rate.")
                return None
            if bounds.clo1.target_tr > self.config.min_rate:
                raise RuntimeError(f"Extending up without clo2: {bounds!r}")
            self.debug(u"Assuming min rate just got remeasured low.")
            load = step_up(bounds.clo1.target_tr, width_goal)
            return load
        # TODO: Explain why are we ignoring possible plo1.
        old_width = ReceiveRateInterval(bounds.clo2, bounds.clo1).rel_tr_width
        if old_width < width_goal:
            # The following is possible with out width rounding.
            self.debug(f"Width {old_width} < {width_goal} in _extend_up.")
        load = multiple_step_up(
            bounds.clo1.target_tr, old_width, self.expansion_coefficient
        )
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
        width = ReceiveRateInterval(bounds.clo1, bounds.chi1).rel_tr_width
        if width <= width_goal:
            return None
        load = half_step_up(bounds.clo1.target_tr, width, width_goal)
        self.debug(f"Bisect candidate: {load}")
        return load
