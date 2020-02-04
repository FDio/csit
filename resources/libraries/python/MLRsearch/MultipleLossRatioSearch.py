# Copyright (c) 2019 Cisco and/or its affiliates.
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

from .AbstractSearchAlgorithm import AbstractSearchAlgorithm
from .NdrPdrResult import NdrPdrResult
from .ReceiveRateInterval import ReceiveRateInterval


class MultipleLossRatioSearch(AbstractSearchAlgorithm):
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

    Next improvement is that the initial interval does not need to be valid.
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
    for current phase.

    TODO: Review and update this docstring according to rst docs.
    TODO: Support configurable number of Packet Loss Ratios.
    """

    class ProgressState:
        """Structure containing data to be passed around in recursion."""

        def __init__(
                self, result, phases, duration, width_goal, packet_loss_ratio,
                minimum_transmit_rate, maximum_transmit_rate):
            """Convert and store the argument values.

            :param result: Current measured NDR and PDR intervals.
            :param phases: How many intermediate phases to perform
                before the current one.
            :param duration: Trial duration to use in the current phase [s].
            :param width_goal: The goal relative width for the curreent phase.
            :param packet_loss_ratio: PDR fraction for the current search.
            :param minimum_transmit_rate: Minimum target transmit rate
                for the current search [pps].
            :param maximum_transmit_rate: Maximum target transmit rate
                for the current search [pps].
            :type result: NdrPdrResult.NdrPdrResult
            :type phases: int
            :type duration: float
            :type width_goal: float
            :type packet_loss_ratio: float
            :type minimum_transmit_rate: float
            :type maximum_transmit_rate: float
            """
            self.result = result
            self.phases = int(phases)
            self.duration = float(duration)
            self.width_goal = float(width_goal)
            self.packet_loss_ratio = float(packet_loss_ratio)
            self.minimum_transmit_rate = float(minimum_transmit_rate)
            self.maximum_transmit_rate = float(maximum_transmit_rate)

    def __init__(
            self, measurer, final_relative_width=0.005,
            final_trial_duration=30.0, initial_trial_duration=1.0,
            number_of_intermediate_phases=2, timeout=600.0, doublings=1):
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
        :param doublings: How many doublings to do in external search step.
            Default 1 is suitable for fairly stable tests,
            less stable tests might get better overal duration with 2 or more.
        :type measurer: AbstractMeasurer.AbstractMeasurer
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: int
        :type number_of_intermediate_phases: int
        :type timeout: float
        :type doublings: int
        """
        super(MultipleLossRatioSearch, self).__init__(measurer)
        self.final_trial_duration = float(final_trial_duration)
        self.final_relative_width = float(final_relative_width)
        self.number_of_intermediate_phases = int(number_of_intermediate_phases)
        self.initial_trial_duration = float(initial_trial_duration)
        self.timeout = float(timeout)
        self.doublings = int(doublings)

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
            1.0 - MultipleLossRatioSearch.double_relative_width(relative_width)
        )

    @staticmethod
    def expand_down(relative_width, doublings, current_bound):
        """Return rate of expanded logarithmic width below.

        :param relative_width: The base relative width to double.
        :param doublings: How many doublings to do for expansion.
        :param current_bound: The current target transmit rate to move [pps].
        :type relative_width: float
        :type doublings: int
        :type current_bound: float
        :returns: Transmit rate smaller by logarithmically double width [pps].
        :rtype: float
        """
        for _ in range(doublings):
            relative_width = MultipleLossRatioSearch.double_relative_width(
                relative_width
            )
        return current_bound * (1.0 - relative_width)

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
            1.0 - MultipleLossRatioSearch.double_relative_width(relative_width)
        )

    @staticmethod
    def expand_up(relative_width, doublings, current_bound):
        """Return rate of expanded logarithmic width above.

        :param relative_width: The base relative width to double.
        :param doublings: How many doublings to do for expansion.
        :param current_bound: The current target transmit rate to move [pps].
        :type relative_width: float
        :type doublings: int
        :type current_bound: float
        :returns: Transmit rate smaller by logarithmically double width [pps].
        :rtype: float
        """
        for _ in range(doublings):
            relative_width = MultipleLossRatioSearch.double_relative_width(
                relative_width
            )
        return current_bound / (1.0 - relative_width)

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
            1.0 - MultipleLossRatioSearch.half_relative_width(relative_width)
        )

    def narrow_down_ndr_and_pdr(
            self, minimum_transmit_rate, maximum_transmit_rate,
            packet_loss_ratio):
        """Perform initial phase, create state object, proceed with next phases.

        :param minimum_transmit_rate: Minimal target transmit rate [pps].
        :param maximum_transmit_rate: Maximal target transmit rate [pps].
        :param packet_loss_ratio: Fraction of packets lost, for PDR [1].
        :type minimum_transmit_rate: float
        :type maximum_transmit_rate: float
        :type packet_loss_ratio: float
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :rtype: NdrPdrResult.NdrPdrResult
        :raises RuntimeError: If total duration is larger than timeout.
        """
        minimum_transmit_rate = float(minimum_transmit_rate)
        maximum_transmit_rate = float(maximum_transmit_rate)
        packet_loss_ratio = float(packet_loss_ratio)
        line_measurement = self.measurer.measure(
            self.initial_trial_duration, maximum_transmit_rate)
        initial_width_goal = self.final_relative_width
        for _ in range(self.number_of_intermediate_phases):
            initial_width_goal = self.double_relative_width(initial_width_goal)
        max_lo = maximum_transmit_rate * (1.0 - initial_width_goal)
        mrr = max(
            minimum_transmit_rate, min(max_lo, line_measurement.receive_rate)
        )
        mrr_measurement = self.measurer.measure(
            self.initial_trial_duration, mrr
        )
        # Attempt to get narrower width.
        if mrr_measurement.loss_fraction > 0.0:
            max2_lo = mrr * (1.0 - initial_width_goal)
            mrr2 = min(max2_lo, mrr_measurement.receive_rate)
        else:
            mrr2 = mrr / (1.0 - initial_width_goal)
        if minimum_transmit_rate < mrr2 < maximum_transmit_rate:
            line_measurement = mrr_measurement
            mrr_measurement = self.measurer.measure(
                self.initial_trial_duration, mrr2)
            if mrr2 > mrr:
                line_measurement, mrr_measurement = \
                    (mrr_measurement, line_measurement)
        starting_interval = ReceiveRateInterval(
            mrr_measurement, line_measurement)
        starting_result = NdrPdrResult(starting_interval, starting_interval)
        state = self.ProgressState(
            starting_result, self.number_of_intermediate_phases,
            self.final_trial_duration, self.final_relative_width,
            packet_loss_ratio, minimum_transmit_rate, maximum_transmit_rate
        )
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
        logging.info(f"result before update: {state.result}")
        logging.debug(
            f"relative widths in goals: "
            f"{state.result.width_in_goals(self.final_relative_width)}"
        )
        measurement = self.measurer.measure(state.duration, transmit_rate)
        ndr_interval = self._new_interval(
            state.result.ndr_interval, measurement, 0.0
        )
        pdr_interval = self._new_interval(
            state.result.pdr_interval, measurement, state.packet_loss_ratio
        )
        state.result = NdrPdrResult(ndr_interval, pdr_interval)
        return state

    @staticmethod
    def _new_interval(old_interval, measurement, packet_loss_ratio):
        """Return new interval with bounds updated according to the measurement.

        :param old_interval: The current interval before the measurement.
        :param measurement: The new meaqsurement to take into account.
        :param packet_loss_ratio: Fraction for PDR (or zero for NDR).
        :type old_interval: ReceiveRateInterval.ReceiveRateInterval
        :type measurement: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type packet_loss_ratio: float
        :returns: The updated interval.
        :rtype: ReceiveRateInterval.ReceiveRateInterval
        """
        old_lo, old_hi = old_interval.measured_low, old_interval.measured_high
        new_lo = new_hi = None
        # Priority zero: direct replace if the target Tr is the same.
        if measurement.target_tr in (old_lo.target_tr, old_hi.target_tr):
            if measurement.target_tr == old_lo.target_tr:
                new_lo = measurement
            else:
                new_hi = measurement
        # Priority one: invalid lower bound allows only one type of update.
        elif old_lo.loss_fraction > packet_loss_ratio:
            # We can only expand down, old bound becomes valid upper one.
            if measurement.target_tr < old_lo.target_tr:
                new_lo, new_hi = measurement, old_lo
            else:
                return old_interval

        # Lower bound is now valid.
        # Next priorities depend on target Tr.
        elif measurement.target_tr < old_lo.target_tr:
            # Lower external measurement, relevant only
            # if the new measurement has high loss rate.
            if measurement.loss_fraction > packet_loss_ratio:
                # Returning the broader interval as old_lo
                # would be invalid upper bound.
                new_lo = measurement
        elif measurement.target_tr > old_hi.target_tr:
            # Upper external measurement, only relevant for invalid upper bound.
            if old_hi.loss_fraction <= packet_loss_ratio:
                # Old upper bound becomes valid new lower bound.
                new_lo, new_hi = old_hi, measurement
        else:
            # Internal measurement, replaced boundary
            # depends on measured loss fraction.
            if measurement.loss_fraction > packet_loss_ratio:
                # We have found a narrow valid interval,
                # regardless of whether old upper bound was valid.
                new_hi = measurement
            else:
                # In ideal world, we would not want to shrink interval
                # if upper bound is not valid.
                # In the real world, we want to shrink it for
                # "invalid upper bound at maximal rate" case.
                new_lo = measurement

        return ReceiveRateInterval(
            old_lo if new_lo is None else new_lo,
            old_hi if new_hi is None else new_hi
        )

    def ndrpdr(self, state):
        """Perform trials for this phase. Return the new state when done.

        :param state: State before this phase.
        :type state: ProgressState
        :returns: The updated state.
        :rtype: ProgressState
        :raises RuntimeError: If total duration is larger than timeout.
        """
        start_time = time.time()
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
            f"starting iterations with duration {state.duration} and relative "
            f"width goal {state.width_goal}"
        )
        while 1:
            if time.time() > start_time + self.timeout:
                raise RuntimeError(u"Optimized search takes too long.")
            # Order of priorities: invalid bounds (nl, pl, nh, ph),
            # then narrowing relative Tr widths.
            # Durations are not priorities yet,
            # they will settle on their own hopefully.
            ndr_lo = state.result.ndr_interval.measured_low
            ndr_hi = state.result.ndr_interval.measured_high
            pdr_lo = state.result.pdr_interval.measured_low
            pdr_hi = state.result.pdr_interval.measured_high
            ndr_rel_width = max(
                state.width_goal, state.result.ndr_interval.rel_tr_width
            )
            pdr_rel_width = max(
                state.width_goal, state.result.pdr_interval.rel_tr_width
            )
            # If we are hitting maximal or minimal rate, we cannot shift,
            # but we can re-measure.
            new_tr = self._ndrpdr_loss_fraction(
                state, ndr_lo, ndr_hi, pdr_lo, pdr_hi, ndr_rel_width,
                pdr_rel_width
            )

            if new_tr is not None:
                state = self._measure_and_update_state(state, new_tr)
                continue

            # If we are hitting maximum_transmit_rate,
            # it is still worth narrowing width,
            # hoping large enough loss fraction will happen.
            # But if we are hitting the minimal rate (at current duration),
            # no additional measurement will help with that,
            # so we can stop narrowing in this phase.
            if (ndr_lo.target_tr <= state.minimum_transmit_rate
                    and ndr_lo.loss_fraction > 0.0):
                ndr_rel_width = 0.0
            if (pdr_lo.target_tr <= state.minimum_transmit_rate
                    and pdr_lo.loss_fraction > state.packet_loss_ratio):
                pdr_rel_width = 0.0

            new_tr = self._ndrpdr_width_goal(
                state, ndr_lo, pdr_lo, ndr_rel_width, pdr_rel_width
            )

            if new_tr is not None:
                state = self._measure_and_update_state(state, new_tr)
                continue

            # We do not need to improve width, but there still might be
            # some measurements with smaller duration.
            new_tr = self._ndrpdr_duration(
                state, ndr_lo, ndr_hi, pdr_lo, pdr_hi, ndr_rel_width,
                pdr_rel_width
            )

            if new_tr is not None:
                state = self._measure_and_update_state(state, new_tr)
                continue

            # Widths are narrow (or lower bound minimal), bound measurements
            # are long enough, we can return.
            logging.info(u"phase done")
            break
        return state

    def _ndrpdr_loss_fraction(
            self, state, ndr_lo, ndr_hi, pdr_lo, pdr_hi, ndr_rel_width,
            pdr_rel_width):
        """Perform loss_fraction-based trials within a ndrpdr phase

        :param state: current state
        :param ndr_lo: ndr interval measured low
        :param ndr_hi: ndr interval measured high
        :param pdr_lo: pdr interval measured low
        :param pdr_hi: pdr interval measured high
        :param ndr_rel_width: ndr interval relative width
        :param pdr_rel_width: pdr interval relative width
        :type state: ProgressState
        :type ndr_lo: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type ndr_hi: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type pdr_lo: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type pdr_hi: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type ndr_rel_width: float
        :type pdr_rel_width: float
        :returns: a new transmit rate if one should be applied
        :rtype: float
        """
        result = None
        if ndr_lo.loss_fraction > 0.0:
            if ndr_lo.target_tr > state.minimum_transmit_rate:
                result = max(
                    state.minimum_transmit_rate, self.expand_down(
                        ndr_rel_width, self.doublings, ndr_lo.target_tr
                    )
                )
                logging.info(f"ndr lo external {result}")
            elif ndr_lo.duration < state.duration:
                result = state.minimum_transmit_rate
                logging.info(u"ndr lo minimal re-measure")

        if result is None and pdr_lo.loss_fraction > state.packet_loss_ratio:
            if pdr_lo.target_tr > state.minimum_transmit_rate:
                result = max(
                    state.minimum_transmit_rate, self.expand_down(
                        pdr_rel_width, self.doublings, pdr_lo.target_tr
                    )
                )
                logging.info(f"pdr lo external {result}")
            elif pdr_lo.duration < state.duration:
                result = state.minimum_transmit_rate
                logging.info(u"pdr lo minimal re-measure")

        if result is None and ndr_hi.loss_fraction <= 0.0:
            if ndr_hi.target_tr < state.maximum_transmit_rate:
                result = min(
                    state.maximum_transmit_rate, self.expand_up(
                        ndr_rel_width, self.doublings, ndr_hi.target_tr
                    )
                )
                logging.info(f"ndr hi external {result}")
            elif ndr_hi.duration < state.duration:
                result = state.maximum_transmit_rate
                logging.info(u"ndr hi maximal re-measure")

        if result is None and pdr_hi.loss_fraction <= state.packet_loss_ratio:
            if pdr_hi.target_tr < state.maximum_transmit_rate:
                result = min(
                    state.maximum_transmit_rate, self.expand_up(
                        pdr_rel_width, self.doublings, pdr_hi.target_tr
                    )
                )
                logging.info(f"pdr hi external {result}")
            elif pdr_hi.duration < state.duration:
                result = state.maximum_transmit_rate
                logging.info(u"ndr hi maximal re-measure")
        return result

    def _ndrpdr_width_goal(
            self, state, ndr_lo, pdr_lo, ndr_rel_width, pdr_rel_width):
        """Perform width_goal-based trials within a ndrpdr phase

        :param state: current state
        :param ndr_lo: ndr interval measured low
        :param pdr_lo: pdr interval measured low
        :param ndr_rel_width: ndr interval relative width
        :param pdr_rel_width: pdr interval relative width
        :type state: ProgressState
        :type ndr_lo: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type pdr_lo: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type ndr_rel_width: float
        :type pdr_rel_width: float
        :returns: a new transmit rate if one should be applied
        :rtype: float
        Return a new transmit rate if one should be applied.
        """
        if ndr_rel_width > state.width_goal:
            # We have to narrow NDR width first, as NDR internal search
            # can invalidate PDR (but not vice versa).
            result = self.half_step_up(ndr_rel_width, ndr_lo.target_tr)
            logging.info(f"Bisecting for NDR at {result}")
        elif pdr_rel_width > state.width_goal:
            # PDR internal search.
            result = self.half_step_up(pdr_rel_width, pdr_lo.target_tr)
            logging.info(f"Bisecting for PDR at {result}")
        else:
            result = None
        return result

    @staticmethod
    def _ndrpdr_duration(
            state, ndr_lo, ndr_hi, pdr_lo, pdr_hi, ndr_rel_width,
            pdr_rel_width):
        """Perform duration-based trials within a ndrpdr phase

        :param state: current state
        :param ndr_lo: ndr interval measured low
        :param ndr_hi: ndr interval measured high
        :param pdr_lo: pdr interval measured low
        :param pdr_hi: pdr interval measured high
        :param ndr_rel_width: ndr interval relative width
        :param pdr_rel_width: pdr interval relative width
        :type state: ProgressState
        :type ndr_lo: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type ndr_hi: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type pdr_lo: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type pdr_hi: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type ndr_rel_width: float
        :type pdr_rel_width: float
        :returns: a new transmit rate if one should be applied
        :rtype: float
        """
        # We need to re-measure with full duration, possibly
        # creating invalid bounds to resolve (thus broadening width).
        if ndr_lo.duration < state.duration:
            result = ndr_lo.target_tr
            logging.info(u"re-measuring NDR lower bound")
        elif pdr_lo.duration < state.duration:
            result = pdr_lo.target_tr
            logging.info(u"re-measuring PDR lower bound")
        # Except when lower bounds have high loss fraction, in that case
        # we do not need to re-measure _upper_ bounds.
        elif ndr_hi.duration < state.duration and ndr_rel_width > 0.0:
            result = ndr_hi.target_tr
            logging.info(u"re-measuring NDR upper bound")
        elif pdr_hi.duration < state.duration and pdr_rel_width > 0.0:
            result = pdr_hi.target_tr
            logging.info(u"re-measuring PDR upper bound")
        else:
            result = None
        return result
