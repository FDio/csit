# Copyright (c) 2021 Cisco and/or its affiliates.
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
import math
import time

from .MeasurementDatabase import MeasurementDatabase
from .ProgressState import ProgressState
from .ReceiveRateInterval import ReceiveRateInterval
from .WidthArithmetics import (
    double_step_down,
    double_step_up,
    half_step_up,
)


class MultipleLossRatioSearch:
    """Optimized binary search algorithm for finding bounds for multiple ratios.

    This is unofficially a subclass of AbstractSearchAlgorithm,
    but constructor signature is different.

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
            number_of_intermediate_phases=2, timeout=600.0, debug=None):
        """Store the measurer object and additional arguments.

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
        :type measurer: AbstractMeasurer.AbstractMeasurer
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: float
        :type number_of_intermediate_phases: int
        :type timeout: float
        :type debug: Optional[Callable[[str], None]]
        """
        self.measurer = measurer
        self.final_trial_duration = float(final_trial_duration)
        self.final_relative_width = float(final_relative_width)
        self.number_of_intermediate_phases = int(number_of_intermediate_phases)
        self.initial_trial_duration = float(initial_trial_duration)
        self.timeout = float(timeout)
        self.state = None
        self.debug = logging.debug if debug is None else debug

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
        min_rate = float(min_rate)
        max_rate = float(max_rate)
        packet_loss_ratios = [float(ratio) for ratio in packet_loss_ratios]
        if len(packet_loss_ratios) < 1:
            raise RuntimeError(u"At least one ratio is required!")
        if packet_loss_ratios != sorted(set(packet_loss_ratios)):
            raise RuntimeError(u"Input ratios have to be sorted and unique!")
        measurements = list()
        self.debug(f"First measurement at max rate: {max_rate}")
        max_measurement = self.measurer.measure(
            duration=self.initial_trial_duration,
            transmit_rate=max_rate,
        )
        measurements.append(max_measurement)
        initial_width_goal = self.final_relative_width
        max_lo = max_rate * (1.0 - initial_width_goal)
        mrr = max(min_rate, min(
            max_lo, max_measurement.relative_receive_rate
        ))
        self.debug(f"Second measurement at mrr: {mrr}")
        mrr_measurement = self.measurer.measure(
            duration=self.initial_trial_duration,
            transmit_rate=mrr,
        )
        measurements.append(mrr_measurement)
        # Attempt to get narrower width.
        if mrr_measurement.loss_ratio > packet_loss_ratios[0]:
            max2_lo = mrr * (1.0 - initial_width_goal)
            mrr2 = min(max2_lo, mrr_measurement.relative_receive_rate)
        else:
            mrr2 = mrr / (1.0 - initial_width_goal)
        if min_rate < mrr2 < max_rate:
            max_measurement = mrr_measurement
            self.debug(f"Third measurement at mrr2: {mrr2}")
            mrr_measurement = self.measurer.measure(
                duration=self.initial_trial_duration,
                transmit_rate=mrr2,
            )
            measurements.append(mrr_measurement)
            if mrr2 > mrr:
                max_measurement, mrr_measurement = \
                    (mrr_measurement, max_measurement)
        database = MeasurementDatabase(measurements)
        self.state = ProgressState(
            database, self.number_of_intermediate_phases,
            self.final_trial_duration, self.final_relative_width,
            packet_loss_ratios, min_rate, max_rate,
        )
        start_time = time.monotonic()
        self.ndrpdr(start_time)
        return self.state.database.get_results(ratio_list=packet_loss_ratios)

    def ndrpdr(self, start_time):
        """Perform trials for this phase. State is updated in-place.

        Recursion to smaller durations is performed (if not performed yet).
        Start time has to be given externally, as the sigle value applies
        across all recursion levels.

        :param start_time: Result of time.monotonic() just before calling this.
        :type start_time: float
        :raises RuntimeError: If total duration is larger than timeout.
        """
        state = self.state
        if state.phases > 0:
            # We need to finish preceding intermediate phases first.
            saved_phases = state.phases
            state.phases -= 1
            # Preceding phases have shorter duration.
            saved_duration = state.duration
            duration_multiplier = state.duration / self.initial_trial_duration
            phase_exponent = float(state.phases) / saved_phases
            state.duration = self.initial_trial_duration * math.pow(
                duration_multiplier, phase_exponent
            )
            # Recurse. State is updated in-place.
            self.ndrpdr(start_time)
            # Restore the state for current phase.
            state.duration = saved_duration
            state.phases = saved_phases  # Not needed, but just in case.
        self.debug(
            f"Starting phase with iterations with {state.duration} duration"
            f" and {state.width_goal} relative width goal."
        )
        failing_fast = False
        database = state.database
        database.set_current_duration(state.duration)
        while time.monotonic() < start_time + self.timeout:
            for index, ratio in enumerate(state.packet_loss_ratios):
                new_tr = self._select_for_ratio(ratio)
                if new_tr is None:
                    # Either this ratio is fine, or min rate got invalid result.
                    # If fine, we will continue to handle next ratio.
                    if index > 0:
                        # If first ratio passed, all ratios have valid lower bound.
                        continue
                    lower_bound, _, _, _, _, _ = database.get_bounds(ratio)
                    if lower_bound is None:
                        failing_fast = True
                        self.debug(u"No valid lower bound for this iteration.")
                        break
                    # First ratio is fine.
                    continue
                # We have transmit rate to measure at.
                measurement = self.measurer.measure(
                    duration=state.duration,
                    transmit_rate=new_tr,
                )
                database.add(measurement)
                # Restart ratio handling on updated database.
                break
            else:
                # No ratio needs measuring, we are done with this phase.
                self.debug(u"Phase done.")
                break
            # We have broken out of the for loop.
            if failing_fast:
                # Abort the while loop early.
                break
            # Not failing fast but database got updated, restart the while loop.
        else:
            # Time is up.
            raise RuntimeError(u"Optimized search takes too long.")
        # Min rate is not valid, but returning what we have so next duration can recover.

    def _select_for_ratio(self, ratio):
        """Return None or new target_tr to measure at.

        Returning None means either we have narrow enough valid interval
        for this ratio, or we are hitting min rate and should fail early.

        :param ratio: Loss ratio to ensure narrow valid bounds for.
        :type ratio: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If database inconsistency is detected.
        """
        state = self.state
        data = state.database
        bounds = data.get_bounds(ratio)
        cur_lo1, cur_hi1, pre_lo1, pre_hi1, cur_lo2, cur_hi2 = bounds

        if cur_lo1 is None and cur_hi1 is None:
            # No result at current duration, start by re-measuring previous one.
            previous_measurement = pre_hi1 if pre_lo1 is None else pre_lo1
            new_tr = previous_measurement.target_tr
            self.debug(f"Re-measuring a bound for {ratio}, tr: {new_tr}")
            return new_tr
        if cur_lo1 is None:
            # Upper bound exists (cur_hi1). Is there previous lower bound to re-measure?
            if pre_lo1 is not None and pre_lo1.target_tr < cur_hi1.target_tr:
                new_tr = pre_lo1.target_tr
                self.debug(f"Re-measuring lower bound for {ratio}, tr: {new_tr}")
                return new_tr
            # No, so we want to extend down.
            new_tr = self._extend_down(cur_hi1, cur_hi2, pre_hi1)
            self.debug(
                f"Extending down for {ratio}: old {cur_hi1.target_tr} new {new_tr}"
            )
            return new_tr
        if cur_hi1 is None:
            # Lower bound exists (cur_lo1). Is there previous upper bound to re-measure?
            if pre_hi1 is not None and pre_hi1.target_tr > cur_lo1.target_tr:
                new_tr = pre_hi1.target_tr
                self.debug(f"Re-measuring upper bound for {ratio}, tr: {new_tr}")
                return new_tr
            # No, so we want to extend up.
            new_tr = self._extend_up(cur_lo1, cur_lo2, pre_lo1)
            self.debug(
                f"Extending up for {ratio}: old {cur_lo1.target_tr} new {new_tr}"
            )
            return new_tr
        # Both bounds exist (cur_lo1 and cur_hi1).
        # cur_lo1 might have been selected for this ratio (we are bisecting)
        # or for previous ratio (we are extending down this ratio).
        # Compute both estimates and choose the higher value.
        bisected_tr = self._bisect(cur_lo1, cur_hi1)
        extended_tr = self._extend_down(cur_hi1, cur_hi2, pre_hi1)
        # Only if both are not None we need to decide.
        if bisected_tr and extended_tr and extended_tr > bisected_tr:
            self.debug(
                f"Extending down for {ratio}: old {cur_hi1.target_tr} new {extended_tr}"
            )
            return extended_tr
        self.debug(
            f"Bisecting for {ratio}: lower {cur_lo1.target_tr},"
            f" upper {cur_hi1.target_tr}, new {bisected_tr}"
        )
        return bisected_tr

    def _extend_down(self, cur_hi1, cur_hi2, pre_hi1):
        """Return extended width below, or None if hitting min rate.

        :param cur_hi1: Tightest upper bound for current duration. Has to exist.
        :param cur_hi2: Second tightest current upper bound, may not exist.
        :param pre_hi1: Tightest upper bound, previous duration, may not exist.
        :type cur_hi1: ReceiveRateMeasurement
        :type cur_hi2: Optional[ReceiveRateMeasurement]
        :type pre_hi1: Optional[ReceiveRateMeasurement]
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        """
        state = self.state
        old_tr = cur_hi1.target_tr
        # Do we have a hint for next best upper bound?
        next_bound = cur_hi2
        if pre_hi1 is not None and pre_hi1.target_tr > old_tr:
            if next_bound is None or pre_hi1.target_tr < next_bound.target_tr:
                next_bound = pre_hi1
        old_width = state.width_goal
        if next_bound is not None:
            old_width = ReceiveRateInterval(cur_hi1, next_bound).rel_tr_width
            old_width = max(old_width, state.width_goal)
        new_tr = double_step_down(old_width, old_tr)
        new_tr = max(new_tr, state.min_rate)
        if new_tr >= old_tr:
            self.debug(u"Extend down hits max rate.")
            return None
        return new_tr

    def _extend_up(self, cur_lo1, cur_lo2, pre_lo1):
        """Return extended width above, or None if hitting max rate.

        :param cur_lo1: Tightest lower bound for current duration. Has to exist.
        :param cur_lo2: Second tightest current lower bound, may not exist.
        :param pre_lo1: Tightest lower bound, previous duration, may not exist.
        :type cur_lo1: ReceiveRateMeasurement
        :type cur_lo2: Optional[ReceiveRateMeasurement]
        :type pre_lo1: Optional[ReceiveRateMeasurement]
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        """
        state = self.state
        old_tr = cur_lo1.target_tr
        # Do we have a hint for next best lower bound?
        next_bound = cur_lo2
        if pre_lo1 is not None and pre_lo1.target_tr > old_tr:
            if next_bound is None or pre_lo1.target_tr < next_bound.target_tr:
                next_bound = pre_lo1
        old_width = state.width_goal
        if next_bound is not None:
            old_width = ReceiveRateInterval(cur_lo1, next_bound).rel_tr_width
            old_width = max(old_width, state.width_goal)
        new_tr = double_step_up(old_width, old_tr)
        new_tr = min(new_tr, state.max_rate)
        if new_tr <= old_tr:
            self.debug(u"Extend down hits max rate.")
            return None
        return new_tr

    def _bisect(self, lower_bound, upper_bound):
        """Return middle rate or None if width is narrow enough.

        :param lower_bound: Measurement to use as a lower bound. Has to exist.
        :param upper_bound: Measurement to use as an upper bound. Has to exist.
        :type lower_bound: ReceiveRateMeasurement
        :type upper_bound: ReceiveRateMeasurement
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If database inconsistency is detected.
        """
        state = self.state
        width = ReceiveRateInterval(lower_bound, upper_bound).rel_tr_width
        if width <= state.width_goal:
            self.debug(u"No more bisects needed.")
            return None
        new_tr = half_step_up(width, lower_bound.target_tr)
        return new_tr
