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

import copy
import logging
import math
import time

from .AbstractSearchAlgorithm import AbstractSearchAlgorithm
from .MeasurementDatabase import MeasurementDatabase
from .ReceiveRateInterval import ReceiveRateInterval
from .WidthArithmetics import (
    step_down,
    double_relative_width,
    double_step_down,
    quadruple_step_down,
    step_up,
    double_step_up,
    quadruple_step_up,
    half_relative_width,
    half_step_up,
)


class MultipleLossRatioSearch(AbstractSearchAlgorithm):
    """Optimized binary search algorithm for finding bounds for multiple ratios.

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

    class ProgressState:
        """Structure containing data to be passed around in recursion."""

        def __init__(
                self, database, phases, duration, width_goal, packet_loss_ratios,
                min_rate, max_rate):
            """Convert and store the argument values.

            :param result: Structure containing measured results.
            :param phases: How many intermediate phases to perform
                before the current one.
            :param duration: Trial duration to use in the current phase [s].
            :param width_goal: The goal relative width for the curreent phase.
            :param packet_loss_ratios: List of fractions for the current search.
            :param min_rate: Minimal target transmit rate available
                for the current search [tps].
            :param max_rate: Maximal target transmit rate available
                for the current search [tps].
            :type result: MeasurementDatabase
            :type phases: int
            :type duration: float
            :type width_goal: float
            :type packet_loss_ratios: Iterable[float]
            :type min_rate: float
            :type max_rate: float
            """
            self.database = database
            self.phases = int(phases)
            self.duration = float(duration)
            self.width_goal = float(width_goal)
            self.packet_loss_ratios = [
                float(ratio) for ratio in packet_loss_ratios
            ]
            self.min_rate = float(min_rate)
            self.max_rate = float(max_rate)
            self.last_width = self.width_goal
            """This is used to track width expansion during external search."""

        def remember_width(self, tr_lo=None, tr_hi=None):
            """Sompute and store width, or reset it to width goal.

            If the width is too small (or None is in input), width goal is used.

            :param tr_lo: One of target rate values to compute width from.
            :param tr_hi: The other target rate value, order does not matter.
            :type tr_lo: Optional[float]
            :type tr_hi: Optional[float]
            """
            # Fallback.
            self.last_width = self.width_goal
            # Conditions to use fallback.
            if tr_lo is None or tr_hi is None:
                return
            difference = abs(tr_hi - tr_lo)
            if not difference:
                return
            width = difference / max(tr_hi, tr_lo)
            if width <= self.width_goal:
                return
            # Set the non-fallback value.
            self.last_width = width

        def min_rate_measured(self):
            """Return whether we have hit the min rate at current duration.

            If true, external search down cannot progress any further.
            Measurement database is not aware of min or max rate.

            :returns: Whether long enough result is in database.
            :rtype: bool
            """
            least_measurement = self.database.measurements[0]
            if least_measurement.target_tr > self.min_rate:
                return False
            if least_measurement.duration < self.duration:
                return False
            return True

        def max_rate_measured(self):
            """Return whether we have hit the max rate at current duration.

            If true, external search up cannot progress any further.
            Measurement database is not aware of min or max rate.

            :returns: Whether long enough result is in database.
            :rtype: bool
            """
            most_measurement = self.database.measurements[-1]
            if most_measurement.target_tr < self.max_rate:
                return False
            if most_measurement.duration < self.duration:
                return False
            return True

    def __init__(
            self, measurer, final_relative_width=0.005,
            final_trial_duration=30.0, initial_trial_duration=1.0,
            number_of_intermediate_phases=2, timeout=600.0):
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
        :type measurer: AbstractMeasurer.AbstractMeasurer
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: float
        :type number_of_intermediate_phases: int
        :type timeout: float
        """
        super(MultipleLossRatioSearch, self).__init__(measurer)
        self.final_trial_duration = float(final_trial_duration)
        self.final_relative_width = float(final_relative_width)
        self.number_of_intermediate_phases = int(number_of_intermediate_phases)
        self.initial_trial_duration = float(initial_trial_duration)
        self.timeout = float(timeout)

    def narrow_down_intervals(self, min_rate, max_rate, packet_loss_ratios):
        """Perform initial phase, create state object, proceed with next phases.

        The current implementation requires the ration so be unique and sorted.
        Also non-empty.

        :param min_rate: Minimal target transmit rate [tps].
        :param max_rate: Maximal target transmit rate [tps].
        :param packet_loss_ratio: Fraction of packets lost, for PDR [1].
        :type min_rate: float
        :type max_rate: float
        :type packet_loss_ratio: float
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
        max_measurement = self.measurer.measure(
            self.initial_trial_duration, max_rate)
        measurements.append(max_measurement)
        initial_width_goal = self.final_relative_width
        for _ in range(self.number_of_intermediate_phases):
            initial_width_goal = self.double_relative_width(initial_width_goal)
        max_lo = max_rate * (1.0 - initial_width_goal)
        mrr = max(min_rate, min(
            max_lo, max_measurement.relative_receive_rate
        ))
        mrr_measurement = self.measurer.measure(
            self.initial_trial_duration, mrr
        )
        measurements.append(mrr_measurement)
        # Attempt to get narrower width.
        if mrr_measurement.loss_fraction > packet_loss_ratios[0]:
            max2_lo = mrr * (1.0 - initial_width_goal)
            mrr2 = min(max2_lo, mrr_measurement.relative_receive_rate)
        else:
            mrr2 = mrr / (1.0 - initial_width_goal)
        if min_rate < mrr2 < max_rate:
            max_measurement = mrr_measurement
            mrr_measurement = self.measurer.measure(
                self.initial_trial_duration, mrr2)
            measurements.append(mrr_measurement)
            if mrr2 > mrr:
                max_measurement, mrr_measurement = \
                    (mrr_measurement, max_measurement)
        database = MeasurmentDatabase(measurements)
        state = self.ProgressState(
            database, self.number_of_intermediate_phases,
            self.final_trial_duration, self.final_relative_width,
            packet_loss_ratios, min_rate, max_rate,
        )
        state = self.ndrpdr(state)
        return state.database.get_results(packet_loss_ratios)

    def ndrpdr(self, state):
        """Perform trials for this phase. Return the new state when done.

        Recursion to smaller durations is performed (if not performed yet).

        :param state: State before this phase.
        :type state: ProgressState
        :returns: The updated state.
        :rtype: ProgressState
        :raises RuntimeError: If total duration is larger than timeout.
        """
        start_time = time.monotonic()
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
            self.ndrpdr(state)
            # Restore the state for current phase.
            state.duration = saved_duration
            state.phases = saved_phases  # Not needed, but just in case.
        logging.info(
            f"Starting iterations with {state.duration}s duration"
            f" and {state.width_goal} relative width goal."
        )
        failing_fast = False
        while time.monotonic() < start_time + self.timeout:
            for ratio in state.packet_loss_ratios:
                new_tr = self._select_for_ratio(state, ratio)
                if new_tr is None:
                    # Either this ratio is fine, or min rate got invalid result.
                    if state.min_rate_measured():
                        if state.database.measurements[0].loss_ratio > ratio:
                            failing_fast = True
                            break
                    # The current ratio is fine.
                    continue
                # We have transmit rate to measure at.
                measurement = self.measurer.measure(new_tr, state.duration)
                state.database.add(measurement)
                # Restart ratio handling on updated database.
                break
            else:
                # No ratio needs measuring, we are done with this phase.
                logging.info(u"phase done")
                return state
            if failing_fast:
                break
            # Restart ratio handling if time permits.
        else:
            # Time is up.
            raise RuntimeError(u"Optimized search takes too long.")
        # Min rate is not valid, but returning what we have so next duration can recover.
        return state

    def _select_for_ratio(self, state, ratio):
        """Return None or new target_tr to measure at.

        This is a top level method, no previous bounds (re)discovered yet.
        The state is updated in-place.

        As the logic is quite convoluted (especialy with respect to
        invalid bounds), sub-methods are called.

        Returning None means either we have narrow enough valid interval
        for this ratio, or we are hitting min rate and should fail early.

        :param state: State before this phase.
        :param ratio: Loss ratio to ensure narrow valid bounds for.
        :type state: ProgressState
        :type ratio: float
        :returns: The next target transmit rate to measure at.
        :rtype: Optional[float]
        :raises RuntimeError: If database inconsistency is detected.
        """
        data = state.database
        lower_bound = data.get_valid_lower_bound(ratio, state.duration)
        if lower_bound is None:
            return self._lower_bound_invalid(state, ratio)
        lower_tr = lower_bound.target_tr
        if lower_tr >= state.max_rate:
            return None
        upper_bound = data.get_valid_upper_bound(ratio, state.duration)
        if upper_bound is None:
            return self._upper_bound_invalid(state, ratio, lower_bound)
        upper_tr = upper_bound.target_tr
        if upper_tr <= state.min_rate:
            return None
        # No special cases, ordinary bisection.
        state.remember_width()
        interval = ReceiveRateInterval(lower_bound, upper_bound)
        width = interval.rel_tr_width
        if width <= state.width_goal:
            return None
        new_tr = half_step_up(width, lower_tr)
        return net_tr

    def _upper_bound_invalid(self, state, ratio, lower_bound):
        """Return None or new target_tr to measure at.

        This is a low-level method. Lower bound is known and valid
        for the current duration, but upper bound is not.
        The lower bound is verified to be lower than max rate.
        The state is updated in-place.

        First, check if previous durations have usable upper bound.
        If not, perform external search upwards, using state
        to track interval size increase. Interval at least doubles,
        at most quadruples (unless limited by max_rate).
        Previously measured target_trs are preferred,
        to avoid unecessary fragmentation.

        :param state: State before this phase.
        :param ratio: Loss ratio to ensure narrow valid bounds for.
        :param lower_bound: Measurement usable as a valid lower bound.
        :type state: ProgressState
        :type ratio: float
        :type lower_bound: ReceiveRateMeasurement
        :returns: The next target transmit rate to measure at.
        :rtype: float
        """
        data = status.database
        # Maybe upper bound just needs te be re-measured at current duration?
        short_bound = data.get_valid_upper_bound(ratio)
        if short_bound is not None:
            return short_bound.target_tr
        # External search upwards. We need previous width.
        old_width = state.last_width
        # Now we can choose target for external search.
        new_min = double_step_up(old_width, lower_tr)
        new_max = quadruple_step_up(old_width, lower_tr)
        new_tr = data.select_tr_for_upper_bound(
            ratio, new_min, new_max
        )
        new_tr = min(new_tr, state.max_rate)
        self.remember_width(lower_tr, new_tr)
        return new_tr


    def _lower_bound_invalid(self, state, ratio):
        """Return None or new target_tr to measure at.

        This is a top level method, no previous bounds (re)discovered yet.
        The state is updated in-place.

        As the logic is quite convoluted (especialy with respect to
        invalid bounds), sub-methods are called.

        This is a low-level method.
        Consistent measurement database is non-empty,
        so duration-unaware query should find either upper or lower bound.

        FIXME
        The lower bound is verified to be lower than max rate.
        The state is updated in-place.

        First, check if previous durations have usable upper bound.
        If not, perform external search upwards, using state
        to track interval size increase. Interval at least doubles,
        at most quadruples (unless limited by max_rate).
        Previously measured target_trs are preferred,
        to avoid unecessary fragmentation.

        :param state: State before this phase.
        :param ratio: Loss ratio to ensure narrow valid bounds for.
        :type state: ProgressState
        :type ratio: float
        :returns: The next target transmit rate to measure at.
        :rtype: float
        :raises RuntimeError: If database inconsistency is detected.
        """
        data = status.database
        # Maybe lower bound just needs re-measure?
        short_bound = data.get_valid_lower_bound(ratio)
        if short_bound is not None:
            return short_bound.target_tr
        # External search downwards. We need upper bound and previous width.
        # For upper bound, prefer current duration,
        # but allow shorter durations as a fallback.
        upper_bound = data.get_valid_upper_bound(ratio, state.duration)
        if upper_bound is None:
            upper_bound = data.get_valid_upper_bound(ratio)
        if upper_bound is None:
            raise RuntimeError(u"Inconsistent measurement database: {data!r}")
        upper_tr = upper_bound.target_tr
        if upper_tr <= state.min_tr:
            if upper_bound.duration < status.duration:
                # We can still re-measure, hoping for valid bound.
                return state.min_tr
            # Fail fast.
            return None
        # Not hitting min rate yet, so external search down.
        old_width = status.last_width
        new_max = double_step_down(old_width, upper_tr)
        new_min = quadruple_step_down(old_width, upper_tr)
        new_tr = data.select_tr_for_lower_bound(
            ratio, new_min, new_max
        )
        new_tr = max(new_tr, state.min_rate)
        self.remember_width(new_tr, upper_tr)
        return new_tr







        previous_tr = data.select_tr_for_upper_bound(
            ratio, state.min_rate, state.max_rate
        )

        old_width = (lower_tr - previous_tr) / lower_tr
        # Now we can choose target for external search.
        new_min = double_step_up(old_width, lower_tr)
        new_max = quadruple_step_up(old_width, lower_tr)
        new_tr = data.select_tr_for_upper_bound(
            ratio, new_min, new_max
        )
        if new_tr < state.max_rate:
            break
        if not max_measured:
            max_measured = True
            break
        # Max was measured and still not valid. We can still bisect.
        width = (state.max_rate - lower_tr) / state.max_rate
            if width <= state.width_goal:
                continue
            # Need bisect.
            new_tr = half_step_up(width, lower_tr)
            break
        # Continue to next ratio.
        


            next_tr = self._choose_tr_by_invalid_bounds(state)

            if next_tr is not None:
                state = self._measure_and_update_state(state, next_tr)
                continue

            if (ndr_lo.target_tr <= state.min_rate
                    and ndr_lo.loss_fraction > 0.0):
                ndr_rel_width = 0.0
            if (pdr_lo.target_tr <= state.min_rate
                    and pdr_lo.loss_fraction > state.packet_loss_ratio):
                pdr_rel_width = 0.0

            next_tr = self._ndrpdr_width_goal(
                state, ndr_lo, pdr_lo, ndr_rel_width, pdr_rel_width
            )

            if next_tr is not None:
                state = self._measure_and_update_state(state, next_tr)
                continue

            # We do not need to improve width, but there still might be
            # some measurements with smaller duration.
            next_tr = self._ndrpdr_duration(
                state, ndr_lo, ndr_hi, pdr_lo, pdr_hi, ndr_rel_width,
                pdr_rel_width
            )

            if next_tr is not None:
                state = self._measure_and_update_state(state, next_tr)
                continue

            # Widths are narrow (or lower bound minimal), bound measurements
            # are long enough, we can return.
            logging.info(u"phase done")
            break
        else:
            raise RuntimeError(u"Optimized search takes too long.")
        return state

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

    def _choose_tr_by_invalid_bounds(self, state):
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
        next_tr = None
        # Is there an invalid lower bound?
        for index, ratio in enumerate(state.packet_loss_ratios):
            interval = state.result[index]
            lower_bound = state.result[index].measured_low
            if lower_bound.loss_fraction <= ratio:
                continue
            # Invalid lower bound, but could be hitting the minimum.
            tr_lo = lower_bound.target_tr
            if tr_lo <= state.min_rate:
                continue
            # Invalid lower bound that can be lowered.
            # But maybe
            expanded_tr = self._select_lower_tr_(
                interval.rel_tr_width, self.doublings, tr_lo
            )
            if 
            next_tr = max(
                state.min_rate, self.expand_down(
                    ndr_rel_width, self.doublings, ndr_lo.target_tr
                )
            )
            logging.info(f"ndr lo external {next_tr}")

        if next_tr is None and pdr_lo.loss_fraction > state.packet_loss_ratio:
            if pdr_lo.target_tr > state.min_rate:
                next_tr = max(
                    state.min_rate, self.expand_down(
                        pdr_rel_width, self.doublings, pdr_lo.target_tr
                    )
                )
                logging.info(f"pdr lo external {next_tr}")
            elif pdr_lo.duration < state.duration:
                next_tr = state.min_rate
                logging.info(u"pdr lo minimal re-measure")

        if next_tr is None and ndr_hi.loss_fraction <= 0.0:
            if ndr_hi.target_tr < state.max_rate:
                next_tr = min(
                    state.max_rate, self.expand_up(
                        ndr_rel_width, self.doublings, ndr_hi.target_tr
                    )
                )
                logging.info(f"ndr hi external {next_tr}")
            elif ndr_hi.duration < state.duration:
                next_tr = state.max_rate
                logging.info(u"ndr hi maximal re-measure")

        if next_tr is None and pdr_hi.loss_fraction <= state.packet_loss_ratio:
            if pdr_hi.target_tr < state.max_rate:
                next_tr = min(
                    state.max_rate, self.expand_up(
                        pdr_rel_width, self.doublings, pdr_hi.target_tr
                    )
                )
                logging.info(f"pdr hi external {next_tr}")
            elif pdr_hi.duration < state.duration:
                next_tr = state.max_rate
                logging.info(u"ndr hi maximal re-measure")
        return next_tr

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
            self.rel_widths = [
                max(self.width_goal, interval.rel_tr_width)
                for interval in self.result
            ]
            # If we are hitting max_rate,
            # it is still worth narrowing width,
            # hoping large enough loss fraction will happen.
            # But if we are hitting the minimal rate (at current duration),
            # no additional measurement will help with that,
            # so we can stop narrowing in this phase.
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
