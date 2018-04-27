# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Module defining OptimizedSearchAlgorithm class."""

import logging
import math
import time

from .AbstractSearchAlgorithm import AbstractSearchAlgorithm
from .NdrPdrResult import NdrPdrResult
from .ReceiveRateInterval import ReceiveRateInterval


class OptimizedSearchAlgorithm(AbstractSearchAlgorithm):
    """Optimized binary search algorithm for finding NDR and PDR bounds.

    Traditional binary search algorithm needs initial interval
    (lower and upper bound), and returns final interval after bisecting
    (until some exit condition is met).
    The exit condition is usually related to the interval width,
    (upper bound value minus lower bound value).

    The optimized algorithm contains several improvements
    aimed to reduce overall search time.

    One improvement is searching for two intervals at once.
    The intervals are for NDR (No Drop Rate) and PDR (Partial Drop Rate).

    Next improvement is that the initial interval does need to be valid.
    Imagine initial interval (10, 11) where 11 is smaller
    than the searched value.
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
    The resulting interval of final phase is the result of the whole algorithm.

    Each non-initial phase uses its own trial duration and width goal.
    Any non-initial phase stops searching (for NDR or PDR independently)
    when minimum is not a valid lower bound (at current duration),
    or all of the following is true:
    Both bounds are valid, bound bounds are measured at the current phase
    trial duration, interval width is less than the width goal
    for current phase."""

    class ProgressState(object):
        """Structure containing data to be passed around in recursion."""

        def __init__(self, result, phases, duration, width_goal,
                     allowed_drop_fraction, fail_rate, line_rate):
            """Convert and store the argument values.

            :param result: Current measured NDR and PDR intervals.
            :param phases: How many intermediate phases to perform
                before the current one.
            :param duration: Trial duration to use in the current phase [s].
            :param width_goal: The goal relative width for the curreent phase.
            :param allowed_drop_fraction: PDR fraction for the current search.
            :param fail_rate: Minimum target transmit rate
                for the current search [pps].
            :param line_rate: Maximum target transmit rate
                for the current search [pps].
            :type result: NdrPdrResult
            :type phases: int
            :type duration: float
            :type width_goal: float
            :type allowed_drop_fraction: float
            :type fail_rate: float
            :type line_rate: float
            """
            self.result = result
            self.phases = int(phases)
            self.duration = float(duration)
            self.width_goal = float(width_goal)
            self.allowed_drop_fraction = float(allowed_drop_fraction)
            self.fail_rate = float(fail_rate)
            self.line_rate = float(line_rate)

    def __init__(self, rate_provider, final_relative_width=0.005,
                 final_trial_duration=30.0, initial_trial_duration=1.0,
                 intermediate_phases=2, timeout=600.0):
        """Store rate provider and additional arguments.

        :param rate_provider: Rate provider to use by this search object.
        :param final_relative_width: Final lower bound transmit rate
            cannot be more distant that this multiple of upper bound [1].
        :param final_trial_duration: Trial duration for the final phase [s].
        :param initial_trial_duration: Trial duration for the initial phase
            and also for the first intermediate phase [s].
        :param intermediate_phases: Number of intermediate phases to perform
            before the final phase [1].
        :param timeout: The search will fail itself when not finished
            before this overall time [s].
        :type rate_provider: AbstractRateProvider
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: int
        :type intermediate_phases: int
        :type timeout: float
        """
        super(OptimizedSearchAlgorithm, self).__init__(rate_provider)
        self.final_trial_duration = float(final_trial_duration)
        self.final_relative_width = float(final_relative_width)
        self.intermediate_phases = int(intermediate_phases)
        self.initial_trial_duration = float(initial_trial_duration)
        self.timeout = float(timeout)

    def narrow_down_ndr_and_pdr(
            self, fail_rate, line_rate, allowed_drop_fraction):
        """Perform initial phase, create state object, proceed with next phases.

        :param fail_rate: Minimal target transmit rate [pps].
        :param line_rate: Maximal target transmit rate [pps].
        :param allowed_drop_fraction: Fraction of dropped packets for PDR [1].
        :type fail_rate: float
        :type line_rate: float
        :type allowed_drop_fraction: float
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :rtype: NdrPdrResult
        :raises RuntimeError: If total duration is larger than timeout.
        """
        fail_rate = float(fail_rate)
        line_rate = float(line_rate)
        allowed_drop_fraction = float(allowed_drop_fraction)
        line_measurement = self.rate_provider.measure(
            self.initial_trial_duration, line_rate)
        # 0.999 is to avoid rounding errors which make
        # the subsequent logic think the width is too broad.
        max_lo = max(
            fail_rate, line_rate * (1.0 - 0.999 * self.final_relative_width))
        mrr = min(max_lo, max(fail_rate, line_measurement.receive_rate))
        mrr_measurement = self.rate_provider.measure(
            self.initial_trial_duration, mrr)
        # Attempt to get narrower width.
        max2_lo = max(
            fail_rate, mrr * (1.0 - 0.999 * self.final_relative_width))
        mrr2 = min(max2_lo, mrr_measurement.receive_rate)
        if mrr2 > fail_rate:
            line_measurement = mrr_measurement
            mrr_measurement = self.rate_provider.measure(
                self.initial_trial_duration, mrr2)
        starting_interval = ReceiveRateInterval(
            mrr_measurement, line_measurement)
        starting_result = NdrPdrResult(starting_interval, starting_interval)
        state = self.ProgressState(
            starting_result, self.intermediate_phases,
            self.final_trial_duration, self.final_relative_width,
            allowed_drop_fraction, fail_rate, line_rate)
        state = self.ndrpdr(state)
        return state.result

    def _measure_and_update_state(self, state, transmit_rate):
        """Perform trial measurement, update bounds, return new state.

        :param state: State before this measurement.
        :param transmit_rate: Target transmit rate for this measurement [pps].
        :type state: ProgressState
        :type transmit_rate: float
        :returns: State after the measurement.
        :rtype: ProgressState
        """
        # TODO: Implement https://stackoverflow.com/a/24683360
        # to avoid the string manipulation if log verbosity is too low.
        logging.info("result before update: %s", state.result)
        logging.debug(
            "relative widths in goals: %s", state.result.width_in_goals(
                self.final_relative_width))
        measurement = self.rate_provider.measure(state.duration, transmit_rate)
        ndr_interval = self._new_interval(
            state.result.ndr_interval, measurement, 0.0)
        pdr_interval = self._new_interval(
            state.result.pdr_interval, measurement, state.allowed_drop_fraction)
        state.result = NdrPdrResult(ndr_interval, pdr_interval)
        return state

    @staticmethod
    def _new_interval(old_interval, measurement, allowed_drop_fraction):
        """Return new interval with bounds updated according to the measurement.

        :param old_interval: The current interval before the measurement.
        :param measurement: The new meaqsurement to take into account.
        :param allowed_drop_fraction: Fraction for PDR (or zero for NDR).
        :type old_interval: ReceiveRateInterval
        :type measurement: ReceiveRateMeasurement
        :type allowed_drop_fraction: float
        :returns: The updated interval.
        :rtype: ReceiveRateInterval
        """
        old_lo, old_hi = old_interval.measured_low, old_interval.measured_high
        # Priority zero: direct replace if the target Tr is the same.
        if measurement.target_tr in (old_lo.target_tr, old_hi.target_tr):
            if measurement.target_tr == old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_hi)
            else:
                return ReceiveRateInterval(old_lo, measurement)
        # Priority one: invalid lower bound allows only one type of update.
        if old_lo.drop_fraction > allowed_drop_fraction:
            # We can only expand down, old bound becomes valid upper one.
            if measurement.target_tr < old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_lo)
            else:
                return old_interval
        # Lower bound is now valid.
        # Next priorities depend on target Tr.
        if measurement.target_tr < old_lo.target_tr:
            # Lower external measurement, relevant only
            # if the new measurement has high drop rate.
            if measurement.drop_fraction > allowed_drop_fraction:
                # Returning the broader interval as old_lo
                # would be invalid upper bound.
                return ReceiveRateInterval(measurement, old_hi)
        elif measurement.target_tr > old_hi.target_tr:
            # Upper external measurement, only relevant for invalid upper bound.
            if old_hi.drop_fraction <= allowed_drop_fraction:
                # Old upper bound becomes valid new lower bound.
                return ReceiveRateInterval(old_hi, measurement)
        else:
            # Internal measurement, replaced boundary
            # depends on measured drop fraction.
            if measurement.drop_fraction > allowed_drop_fraction:
                # We have found a narrow valid interval,
                # regardless of whether old upper bound was valid.
                return ReceiveRateInterval(old_lo, measurement)
            else:
                # In ideal world, we would not want to shrink interval
                # if upper bound is not valid.
                # In the real world, we want to shrink it for
                # "invalid upper bound at line rate" case.
                return ReceiveRateInterval(measurement, old_hi)
        # Fallback, the interval is unchanged by the measurement.
        return old_interval

    @staticmethod
    def double_relative_width(relative_width):
        """Return relative width corresponding to double logarithmic width.

        :param relative_width: The base relative width to double.
        :type relative_width: float
        :returns: The relative width of double logarithmic size.
        :rtype: float
        """
        return 1.999 * relative_width - relative_width * relative_width
        # The number should be 2.0, but we want to avoid rounding errors,
        # and ensure half of double is not larger than the original value.

    @staticmethod
    def double_step_down(relative_width, current_bound):
        """Return rate of double logarithmic width below.

        :param relative_width: The base relative width to double.
        :param current_bound: The current target transmit rate to move [pps].
        :type relative_width: float
        :type current_bound: float
        :returns: Transmit rate smaller by logarithmically double width [pps].
        :rtype: float
        """
        return current_bound * (
            1.0 - OptimizedSearchAlgorithm.double_relative_width(
                relative_width))

    @staticmethod
    def double_step_up(relative_width, current_bound):
        """Return rate of double logarithmic width above.

        :param relative_width: The base relative width to double.
        :param current_bound: The current target transmit rate to move [pps].
        :type relative_width: float
        :type current_bound: float
        :returns: Transmit rate larger by logarithmically double width [pps].
        :rtype: float
        """
        return current_bound / (
            1.0 - OptimizedSearchAlgorithm.double_relative_width(
                relative_width))

    @staticmethod
    def half_relative_width(relative_width):
        """Return relative width corresponding to half logarithmic width.

        :param relative_width: The base relative width to halve.
        :type relative_width: float
        :returns: The relative width of half logarithmic size.
        :rtype: float
        """
        return 1.0 - math.sqrt(1.0 - relative_width)

    @staticmethod
    def half_step_up(relative_width, current_bound):
        """Return rate of half logarithmic width above.

        :param relative_width: The base relative width to halve.
        :param current_bound: The current target transmit rate to move [pps].
        :type relative_width: float
        :type current_bound: float
        :returns: Transmit rate larger by logarithmically half width [pps].
        :rtype: float
        """
        return current_bound / (
            1.0 - OptimizedSearchAlgorithm.half_relative_width(relative_width))

    def ndrpdr(self, state):
        """Pefrom trials for this phase. Return the new state when done.

        :param state: State before this phase.
        :type state: ProgressState
        :returns: The updates state.
        :rtype: ProgressState
        :raises RuntimeError: If total duration is larger than timeout.
        """
        if state.phases > 0:
            # We need to finish preceding intermediate phases first.
            saved_phases = state.phases
            state.phases -= 1
            # Preceding phases have shorter duration.
            saved_duration = state.duration
            duration_multiplier = state.duration / self.initial_trial_duration
            phase_exponent = float(state.phases) / saved_phases
            state.duration = self.initial_trial_duration * math.pow(
                duration_multiplier, phase_exponent)
            # Shorter durations do not need that narrow widths.
            saved_width = state.width_goal
            state.width_goal = self.double_relative_width(state.width_goal)
            # Recurse.
            state = self.ndrpdr(state)
            # Restore the state for current phase.
            state.duration = saved_duration
            state.width_goal = saved_width
            state.phases = saved_phases  # Not needed, but just in case.
        logging.info(
            "starting iterations with duration %s and relative width goal %s",
            state.duration, state.width_goal)
        start_time = time.time()
        while 1:
            if time.time() > start_time + self.timeout:
                raise RuntimeError("Optimized search takes too long.")
            # Order of priorities: improper bounds (nl, pl, nh, ph),
            # then narrowing relative Tr widths.
            # Durations are not priorities yet,
            # they will settle on their own hopefully.
            ndr_lo = state.result.ndr_interval.measured_low
            ndr_hi = state.result.ndr_interval.measured_high
            pdr_lo = state.result.pdr_interval.measured_low
            pdr_hi = state.result.pdr_interval.measured_high
            ndr_rel_width = max(
                state.width_goal, state.result.ndr_interval.rel_tr_width)
            pdr_rel_width = max(
                state.width_goal, state.result.pdr_interval.rel_tr_width)
            # If we are hitting line or fail rate, we cannot shift,
            # but we can re-measure.
            if ndr_lo.drop_fraction > 0.0:
                if ndr_lo.target_tr > state.fail_rate:
                    new_tr = max(state.fail_rate, self.double_step_down(
                        ndr_rel_width, ndr_lo.target_tr))
                    logging.info("ndr lo external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif ndr_lo.duration < state.duration:
                    logging.info("ndr lo fail re-measure")
                    state = self._measure_and_update_state(
                        state, state.fail_rate)
                    continue
            if pdr_lo.drop_fraction > state.allowed_drop_fraction:
                if pdr_lo.target_tr > state.fail_rate:
                    new_tr = max(state.fail_rate, self.double_step_down(
                        pdr_rel_width, pdr_lo.target_tr))
                    logging.info("pdr lo external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif pdr_lo.duration < state.duration:
                    logging.info("pdr lo fail re-measure")
                    state = self._measure_and_update_state(
                        state, state.fail_rate)
                    continue
            if ndr_hi.drop_fraction <= 0.0:
                if ndr_hi.target_tr < state.line_rate:
                    new_tr = min(state.line_rate, self.double_step_up(
                        ndr_rel_width, ndr_hi.target_tr))
                    logging.info("ndr hi external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif ndr_hi.duration < state.duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(
                        state, state.line_rate)
                    continue
            if pdr_hi.drop_fraction <= state.allowed_drop_fraction:
                if pdr_hi.target_tr < state.line_rate:
                    new_tr = min(state.line_rate, self.double_step_up(
                        pdr_rel_width, pdr_hi.target_tr))
                    logging.info("pdr hi external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif pdr_hi.duration < state.duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(
                        state, state.line_rate)
                    continue
            # If we are hitting line_rate, it is still worth narrowing width,
            # hoping large enough Df will happen.
            # But if we are hitting fail rate (at current duration),
            # no additional measurement will help with that,
            # so we can stop narrowing in this phase.
            if (ndr_lo.target_tr <= state.fail_rate
                    and ndr_lo.drop_fraction > 0.0):
                ndr_rel_width = 0.0
            if (pdr_lo.target_tr <= state.fail_rate
                    and pdr_lo.drop_fraction > state.allowed_drop_fraction):
                pdr_rel_width = 0.0
            if max(ndr_rel_width, pdr_rel_width) > state.width_goal:
                # We have to narrow some width.
                if ndr_rel_width >= pdr_rel_width:
                    new_tr = self.half_step_up(ndr_rel_width, ndr_lo.target_tr)
                    logging.info("Bisecting for NDR at %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                else:
                    new_tr = self.half_step_up(pdr_rel_width, pdr_lo.target_tr)
                    logging.info("Bisecting for PDR at %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
            # We do not need to improve width, but there still might be
            # some measurements with smaller duration.
            # We need to re-measure with full duration, possibly
            # creating invalid bounds to resolve (thus broadening width).
            if ndr_lo.duration < state.duration:
                logging.info("re-measuring NDR lower bound")
                self._measure_and_update_state(state, ndr_lo.target_tr)
                continue
            if pdr_lo.duration < state.duration:
                logging.info("re-measuring PDR lower bound")
                self._measure_and_update_state(state, pdr_lo.target_tr)
                continue
            # Except when lower bounds have high Df, in that case
            # we do not need to re-measure _upper_ bounds.
            if ndr_hi.duration < state.duration and ndr_rel_width > 0.0:
                logging.info("re-measuring NDR upper bound")
                self._measure_and_update_state(state, ndr_hi.target_tr)
                continue
            if pdr_hi.duration < state.duration and pdr_rel_width > 0.0:
                logging.info("re-measuring PDR upper bound")
                self._measure_and_update_state(state, pdr_hi.target_tr)
                continue
            # Widths are narrow (or failing), bound measurements
            # are long enough, we can return.
            logging.info("phase done")
            break
        return state
