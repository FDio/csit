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

import math
import logging

from AbstractSearchAlgorithm import AbstractSearchAlgorithm
from ReceiveRateMeasurement import ReceiveRateMeasurement
from ReceiveRateInterval import ReceiveRateInterval
from NdrPdrResult import NdrPdrResult


class WednesdaySearchAlgorithm(AbstractSearchAlgorithm):
    """FIXME: Describe the smart ways and choose a better name."""

    class ProgressState(object):
        """Structure containing data to be passed around in recursion."""

        def __init__(self, result, width_goal, allowed_drop_fraction, fail_rate, line_rate):
            """FIXME"""
            self.result = result
            self.width_goal = width_goal
            self.allowed_drop_fraction = allowed_drop_fraction
            self.fail_rate = fail_rate
            self.line_rate = line_rate
            self.duration_min = min(result.ndr_interval.measured_low.duration,
                                    result.ndr_interval.measured_high.duration,
                                    result.pdr_interval.measured_low.duration,
                                    result.pdr_interval.measured_high.duration)

    def __init__(self, rate_provider, final_duration=30.0, final_width=0.005, duration_coefficient=5.4):
        """FIXME"""
        super(WednesdaySearchAlgorithm, self).__init__(rate_provider)
        self.final_duration = final_duration
        self.final_width = final_width
        self.duration_coefficient = duration_coefficient

    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Perform minimal measurements, initialize state, proceed with the width-aware method."""
        line_measurement = self.rate_provider.measure(1.0, line_rate)
        # 0.999 is to avoid rounding errors making the subsequent logic think the width is too broad.
        max_lo = line_rate * (1.0 - 0.999 * self.final_width)
        mrr = min(max_lo, max(fail_rate, line_measurement.receive_rate))
        mrr_measurement = self.rate_provider.measure(1.0, mrr)
        # Attempt to get narrower width.
        max2_lo = max(fail_rate, mrr * (1.0 - 0.999 * self.final_width))
        mrr2 = min(max2_lo, mrr_measurement.receive_rate)
        if mrr2 > fail_rate:
            line_measurement = mrr_measurement
            mrr_measurement = self.rate_provider.measure(1.0, mrr2)
        starting_interval = ReceiveRateInterval(mrr_measurement, line_measurement)
        starting_result = NdrPdrResult(starting_interval, starting_interval)
        state = self.ProgressState(starting_result, self.final_width, allowed_drop_fraction, fail_rate, line_rate)
        state = self.ndrpdr(state, self.final_duration)
        return state.result

    def _measure_and_update_state(self, state, duration, transmit_rate):
        """Repeated action of updating state upon new measurement."""
        measurement = self.rate_provider.measure(duration, transmit_rate)
        ndr_interval = self._new_interval(state.result.ndr_interval, measurement, 0.0)
        pdr_interval = self._new_interval(state.result.pdr_interval, measurement, state.allowed_drop_fraction)
        state.result = NdrPdrResult(ndr_interval, pdr_interval)
        logging.info("result after update: %s", state.result)
        logging.debug("relative widths: NDR %s PDR %s", ndr_interval.rel_tr_width, pdr_interval.rel_tr_width)
        return state

    def _new_interval(self, old_interval, measurement, allowed_drop_fraction):
        """Figure out which interval bounds to replace."""
        old_lo, old_hi = old_interval.measured_low, old_interval.measured_high
        # Priority zero: direct replace if the target Tr is the same.
        if measurement.target_tr in (old_lo.target_tr, old_hi.target_tr):
            if measurement.target_tr == old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_hi)
            else:
                return ReceiveRateInterval(old_lo, measurement)
        # Priority one: invalid lower bound allows only one type of update.
        if old_lo.drop_fraction > allowed_drop_fraction:
            # We can only expand down.
            if measurement.target_tr < old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_lo)
            else:
                return old_interval
        # Lower bound is now valid.
        # Next priorities depend on target Tr.
        if measurement.target_tr < old_lo.target_tr:
            # Lower external measurement, relevant only if the new measurement has high drop rate.
            if measurement.drop_fraction > allowed_drop_fraction:
                # Returning the broader interval as old_lo would be invalid upper bound.
                return ReceiveRateInterval(measurement, old_hi)
        elif measurement.target_tr > old_hi.target_tr:
            # Upper external measurement, only relevant for invalid upper bound.
            if old_hi.drop_fraction <= allowed_drop_fraction:
                # Old upper bound becomes valid new lower bound.
                return ReceiveRateInterval(old_hi, measurement)
        else:
            # Internal measurement, replaced boundary depends on measured drop fraction.
            if measurement.drop_fraction > allowed_drop_fraction:
                # We have found a narrow valid interval,
                # regardless of whether old upper bound was valid.
                return ReceiveRateInterval(old_lo, measurement)
            else:
                # We do not want to shrink interval if upper bound is not valid.
                if old_hi.drop_fraction > allowed_drop_fraction:
                    return ReceiveRateInterval(measurement, old_hi)
        # Fallback, the interval is unchanged by the measurement.
        return old_interval

    @staticmethod
    def double_relative_width(relative_width):
        """Return relative width corresponding to double logarithmic width."""
        return 1.999 * relative_width - relative_width * relative_width
        # The number should be 2.0, but we want to avoid rounding errors,
        # and ensure half of double is not larger than the original value.

    @staticmethod
    def double_step_down(relative_width, current_bound):
        """Return rate of double logarithmic width below."""
        return current_bound * (1.0 - WednesdaySearchAlgorithm.double_relative_width(relative_width))

    @staticmethod
    def double_step_up(relative_width, current_bound):
        """Return rate of double logarithmic width above."""
        return current_bound / (1.0 - WednesdaySearchAlgorithm.double_relative_width(relative_width))

    @staticmethod
    def half_relative_width(relative_width):
        """Return relative width corresponding to half logarithmic width."""
        return 1.0 - math.sqrt(1.0 - relative_width)

    @staticmethod
    def half_step_up(relative_width, current_bound):
        """Return rate of half logarithmic width above."""
        return current_bound / (1.0 - WednesdaySearchAlgorithm.half_relative_width(relative_width))

    def ndrpdr(self, state, duration):
        """Iterate to improve bounds. When time is up, return current result."""
        acceptable_duration = duration / self.duration_coefficient
        if state.duration_min < acceptable_duration and acceptable_duration >= 1.0:
            # Previous measurements are too short, recurse to get acceptably long measurements.
            # Shorter durations do not need that narrow widths.
            saved_width = state.width_goal
            state.width_goal = self.double_relative_width(state.width_goal)
            state = self.ndrpdr(state, acceptable_duration)
            state.width_goal = saved_width
        logging.info("starting iterations with duration %s and relative width goal %s", duration, state.width_goal)
        while 1:
            # Order of priorities: improper bounds (nl, nh, pl, ph), then narrowing relative Tr widths.
            # Durations are not priorities, they will settle on their own.
            ndr_lo = state.result.ndr_interval.measured_low
            ndr_hi = state.result.ndr_interval.measured_high
            pdr_lo = state.result.pdr_interval.measured_low
            pdr_hi = state.result.pdr_interval.measured_high
            ndr_rel_width = max(state.width_goal, state.result.ndr_interval.rel_tr_width)
            pdr_rel_width = max(state.width_goal, state.result.pdr_interval.rel_tr_width)
            # If we are hitting line or fail rate, we cannot shift, but we can re-measure.
            if ndr_lo.drop_fraction > 0.0:
                if ndr_lo.target_tr > state.fail_rate:
                    new_tr = max(state.fail_rate, self.double_step_down(ndr_rel_width, ndr_lo.target_tr))
                    logging.info("ndr lo external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif ndr_lo.duration < duration:
                    logging.info("ndr lo fail re-measure")
                    state = self._measure_and_update_state(state, duration, state.fail_rate)
                    continue
            if ndr_hi.drop_fraction <= 0.0:
                if ndr_hi.target_tr < state.line_rate:
                    new_tr = max(state.fail_rate, self.double_step_up(ndr_rel_width, ndr_hi.target_tr))
                    logging.info("ndr hi external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif ndr_hi.duration < duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(state, duration, state.line_rate)
                    continue
            if pdr_lo.drop_fraction > state.allowed_drop_fraction:
                if pdr_lo.target_tr > state.fail_rate:
                    new_tr = max(state.fail_rate, self.double_step_down(pdr_rel_width, pdr_lo.target_tr))
                    logging.info("pdr lo external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif pdr_lo.duration < duration:
                    logging.info("pdr lo fail re-measure")
                    state = self._measure_and_update_state(state, duration, state.fail_rate)
                    continue
            if pdr_hi.drop_fraction <= state.allowed_drop_fraction:
                if pdr_hi.target_tr < state.line_rate:
                    new_tr = max(state.fail_rate, self.double_step_up(pdr_rel_width, pdr_hi.target_tr))
                    logging.info("pdr hi external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif pdr_hi.duration < duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(state, duration, state.line_rate)
                    continue
            # If we are hitting line_rate, it is still worth narrowing width,
            # hoping large enough Df will happen.
            # But if we are hitting fail rate (at current duration), no additional measurement
            # will help with that, so we can stop improving.
            if ndr_lo.target_tr <= state.fail_rate and ndr_lo.drop_fraction > 0.0:
                ndr_rel_width = 0.0
            if pdr_lo.target_tr <= state.fail_rate and pdr_lo.drop_fraction > state.allowed_drop_fraction:
                pdr_rel_width = 0.0
            if max(ndr_rel_width, pdr_rel_width) > state.width_goal:
                # We have to narrow some width.
                if ndr_rel_width >= pdr_rel_width:
                    new_tr = self.half_step_up(ndr_rel_width, ndr_lo.target_tr)
                    logging.info("Bisecting for NDR at %s", new_tr)
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                else:
                    new_tr = self.half_step_up(pdr_rel_width, pdr_lo.target_tr)
                    logging.info("Bisecting for PDR at %s", new_tr)
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
            # We do not need to improve width, but there still might be some measurements with smaller duration.
            # We need to re-measure with full duration, possibly creating improper bounds to resolve (thus broadening width).
            if ndr_lo.duration < duration:
                logging.info("re-measuring NDR lower bound")
                self._measure_and_update_state(state, duration, ndr_lo.target_tr)
                continue
            # Except when lower bounds have high Df, in that case we do not need to re-measure _upper_ bounds.
            if ndr_hi.duration < duration and ndr_rel_width > 0.0:
                logging.info("re-measuring NDR upper bound")
                self._measure_and_update_state(state, duration, ndr_hi.target_tr)
                continue
            if pdr_lo.duration < duration:
                logging.info("re-measuring PDR lower bound")
                self._measure_and_update_state(state, duration, pdr_lo.target_tr)
                continue
            if pdr_hi.duration < duration and pdr_rel_width > 0.0:
                logging.info("re-measuring PDR upper bound")
                self._measure_and_update_state(state, duration, pdr_hi.target_tr)
                continue
            # Widths are narrow (or failing), bound measurements are long enough, we can return.
            logging.info("duration done")
            break
        return state
