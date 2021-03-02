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
            number_of_intermediate_phases=2, timeout=600.0, logger=None):
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
        :param logger: If specified, use this instead of logging module.
        :type measurer: AbstractMeasurer.AbstractMeasurer
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: float
        :type number_of_intermediate_phases: int
        :type timeout: float
        :type logger: None or a module with .debug() function of single argument.
        """
        self.measurer = measurer
        self.final_trial_duration = float(final_trial_duration)
        self.final_relative_width = float(final_relative_width)
        self.number_of_intermediate_phases = int(number_of_intermediate_phases)
        self.initial_trial_duration = float(initial_trial_duration)
        self.timeout = float(timeout)
        self.state = None
        self.logger = logging if logger is None else logger

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
        self.logger.debug(u"First measurement at max rate.")
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
        self.logger.debug(u"Second measurement at mrr.")
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
            self.logger.debug(u"Third measurement at mrr2.")
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
        self.logger.debug(
            f"Starting phase with iterations with {state.duration} duration"
            f" and {state.width_goal} relative width goal."
        )
        failing_fast = False
        database = state.database
        while time.monotonic() < start_time + self.timeout:
            for index, ratio in enumerate(state.packet_loss_ratios):
                new_tr = self._select_for_ratio(ratio)
                if new_tr is None:
                    # Either this ratio is fine, or min rate got invalid result.
                    # If fine, we will continue to handle next ratio.
                    if index > 0:
                        # If first ratio passed, all ratios have valid lower bound.
                        continue
                    lower_bound, _ = database.get_valid_lower_bound(ratio)
                    if lower_bound is None:
                        failing_fast = True
                        self.logger.debug(u"No valid lower bound for this iteration.")
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
                self.logger.debug(u"Phase done.")
            # We have broken out of the for loop.
            if failing_fast:
                # Abort the while loop early.
                break
            # Restart ratio handling if time permits.
        else:
            # Time is up.
            raise RuntimeError(u"Optimized search takes too long.")
        # Min rate is not valid, but returning what we have so next duration can recover.

    def _select_for_ratio(self, ratio):
        """Return None or new target_tr to measure at.

        This is a top level method, no previous bounds (re)discovered yet.
        The state is updated in-place.

        As the logic is quite convoluted (especialy with respect to
        invalid bounds), sub-methods are called.

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
        lower_bound, short_lower_bound = data.get_valid_lower_bound(ratio)
        upper_bound, short_upper_bound = data.get_valid_upper_bound(ratio)
        if lower_bound is None:
            if upper_bound is None:
                # No measurements at this duration.
                if short_lower_bound is None:
                    if short_upper_bound is None:
                        raise RuntimeError(
                            u"No measurement for this nor previous duration."
                        )
                    # Short upper bound is not None.
                    # It is the only relevant value we have from previous duration.
                    self.logger.debug(f"Re-measuring upper bound for {ratio}")
                    return short_upper_bound.target_tr
                # Short lower bound is not None; re-measure it.
                self.logger.debug(f"Re-measuring lower bound for {ratio}")
                return short_lower_bound.target_tr
            # Upper bound is not None.
            return self._extend_down(ratio, upper_bound)
        # Lower bound is not None.
        if upper_bound is None:
            return self._extend_up(ratio, lower_bound)
        # Upper bound is not None.
        return self._bisect(ratio, lower_bound, upper_bound)

    def _extend_down(self, ratio, upper_bound):
        """Return extended width below, or None if hitting min rate.

        :param ratio: Loss ratio to ensure narrow valid bounds for.
        :param upper_bound: Measurement to use as an upper bound.
        :type ratio: float
        :type upper_bound: ReceiveRateMeasurement
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If database inconsistency is detected.
        """
        state = self.state
        old_width = state.last_width
        old_tr = upper_bound.target_tr
        new_tr = double_step_down(old_width, old_tr)
        new_tr = max(new_tr, state.min_rate)
        if new_tr >= old_tr:
            self.logger.debug(f"Extend down hits max rate for {ratio}")
            return None
        state.remember_width(old_tr, new_tr)
        self.logger.debug(f"Extending down for {ratio}")
        return new_tr

    def _extend_up(self, ratio, lower_bound):
        """Return extended width above, or None if hitting min rate.

        :param ratio: Loss ratio to ensure narrow valid bounds for.
        :param lower_bound: Measurement to use as an lower bound.
        :type ratio: float
        :type lower_bound: ReceiveRateMeasurement
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If database inconsistency is detected.
        """
        state = self.state
        old_width = state.last_width
        old_tr = lower_bound.target_tr
        new_tr = double_step_up(old_width, old_tr)
        new_tr = min(new_tr, state.max_rate)
        if new_tr <= old_tr:
            self.logger.debug(f"Extend up hits max rate for {ratio}")
            return None
        state.remember_width(old_tr, new_tr)
        self.logger.debug(f"Extending up for {ratio}")
        return new_tr

    def _bisect(self, ratio, lower_bound, upper_bound):
        """Return middle rate or None if width is narrow enough.

        :param ratio: Loss ratio to ensure narrow valid bounds for.
        :param lower_bound: Measurement to use as a lower bound.
        :param upper_bound: Measurement to use as an upper bound.
        :type ratio: float
        :type lower_bound: ReceiveRateMeasurement
        :type upper_bound: ReceiveRateMeasurement
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If database inconsistency is detected.
        """
        state = self.state
        state.remember_width()
        interval = ReceiveRateInterval(lower_bound, upper_bound)
        width = interval.rel_tr_width
        if width <= state.width_goal:
            self.logger.debug(f"No more bisects needed for {ratio}")
            return None
        self.logger.debug(f"Bisecting for {ratio}")
        new_tr = half_step_up(width, lower_bound.target_tr)
        return new_tr
