# FIXME: License.

import logging

from AbstractSearchAlgorithm import AbstractSearchAlgorithm
from ReceiveRateMeasurement import ReceiveRateMeasurement
from ReceiveRateInterval import ReceiveRateInterval
from NdrPdrResult import NdrPdrResult


class ProgressState(object):
    """Structure containing data to be passed around in recursion."""

    def __init__(self, result, time_bank, allowed_drop_fraction, fail_rate, line_rate):
        """FIXME"""
        self.result = result
        self.time_bank = time_bank
        self.allowed_drop_fraction = allowed_drop_fraction
        self.fail_rate = fail_rate
        self.line_rate = line_rate
        self.duration_min = min(result.ndr_interval.measured_low.duration,
                                result.ndr_interval.measured_high.duration,
                                result.pdr_interval.measured_low.duration,
                                result.pdr_interval.measured_high.duration)


class TotalTimeBasedSearch(AbstractSearchAlgorithm):
    """FIXME: Describe the smart ways and choose a better name."""

    def __init__(self, rate_provider, final_duration=60.0, length=6.0, duration_coefficient=3.0, time_coefficient=4.0):
        """Duration refers to one measurement, time to the whole iteration."""
        super(TotalTimeBasedSearch, self).__init__(rate_provider)
        self.final_duration = final_duration
        self.length = length
        self.duration_coefficient = duration_coefficient
        self.time_coefficient = time_coefficient

    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Compute total allowed time, perform minimal measurements, proceed with the time-aware method."""
        line_measurement = self.rate_provider.measure(1.0, line_rate)
        mrr = min(line_rate, max(fail_rate, line_measurement.receive_rate))
        if mrr >= line_rate:
            # No drops at line rate, but we cannot trust one second measurement.
            mrr = fail_rate
        mrr_measurement = self.rate_provider.measure(1.0, mrr)
        # Even is there are too many drops at fail rate, we still cannot trust one second measurement.
        starting_interval = ReceiveRateInterval(mrr_measurement, line_measurement)
        starting_result = NdrPdrResult(starting_interval, starting_interval)
        time_bank = self.final_duration * self.length
        starting_state = ProgressState(starting_result, time_bank, allowed_drop_fraction, fail_rate, line_rate)
        state = self.ndrpdr(starting_state, self.final_duration)
        return state.result

    def _measure_and_update_state(self, state, duration, transmit_rate):
        """Repeated action of updating state upon new measurement."""
        measurement = self.rate_provider.measure(duration, transmit_rate)
        state.time_bank -= duration
        ndr_interval = self._new_interval(state.result.ndr_interval, measurement, 0.0)
        pdr_interval = self._new_interval(state.result.pdr_interval, measurement, state.allowed_drop_fraction)
        state.result = NdrPdrResult(ndr_interval, pdr_interval)
        logging.info("result after update: %s", state.result)
        return state

    def _new_interval(self, old_interval, measurement, allowed_drop_fraction):
        """Figure out which interval bounds to replace."""
        old_lo, old_hi = old_interval.measured_low, old_interval.measured_high
        # Priority zero: direct replace if target Tr is the same.
        if measurement.target_tr in (old_lo.target_tr, old_hi.target_tr):
            if measurement.target_tr == old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_hi)
            else:
                return ReceiveRateInterval(old_lo, measurement)
        if measurement.drop_fraction > allowed_drop_fraction:
            # Priority two: above-fraction measurement replaces any bound with bigger Tr
            # First compare against lower bound, return the narrower interval.
            if measurement.target_tr < old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_lo)
            if measurement.target_tr < old_hi.target_tr:
                return ReceiveRateInterval(old_lo, measurement)
            # Priority three: otherwise above-fraction measurement only replaces upper bound if it is was not valid
            if old_hi.drop_fraction <= allowed_drop_fraction:
                return ReceiveRateInterval(old_lo, measurement)
        else:
            if old_lo.drop_fraction <= allowed_drop_fraction:
                # Priority four: below-fraction measurement replaces valid lower bound only if measured Tr is higher
                if measurement.target_tr > old_lo.target_tr:
                    return ReceiveRateInterval(measurement, old_hi)
            else:
                # Priority five: invalid lower bound is only updated if measured Tr is lower.
                # the invalid lower bound becomes a valid upper bound.
                if measurement.target_tr < old_lo.target_tr:
                    return ReceiveRateInterval(measurement, old_lo)
        # Fallback: the measurement is irrelevant for the interval
        return old_interval

    def ndrpdr(self, state, duration):
        """Iterate to narrow widths. When time is up, return current result."""
        acceptable_duration = duration / self.duration_coefficient
        if state.duration_min < acceptable_duration and acceptable_duration >= 1.0:
            # Previous measurements are too short, recurse to get acceptable measurements.
            saved_bank = state.time_bank * (1 - 1.0 / self.time_coefficient)
            state.time_bank -= saved_bank
            state = self.ndrpdr(state, acceptable_duration)
            state.time_bank += saved_bank
        logging.info("starting iteration with duration %s time bank %s", duration, state.time_bank)
        while 1:
            # Order of priorities: improper bounds (nl, nh, pl, ph), then reducing Tr difference.
            # Durations are not priorities, they will settle on their own.
            ndr_lo = state.result.ndr_interval.measured_low
            ndr_hi = state.result.ndr_interval.measured_high
            pdr_lo = state.result.pdr_interval.measured_low
            pdr_hi = state.result.pdr_interval.measured_high
            ndr_tr_width = state.result.ndr_interval.abs_tr_width
            pdr_tr_width = state.result.pdr_interval.abs_tr_width
            # If we are hitting line or fail rate, we cannot shift, byt we can re-measure.
            if ndr_lo.drop_fraction > 0.0:
                if ndr_lo.target_tr > state.fail_rate:
                    new_tr = max(ndr_lo.target_tr - 2 * ndr_tr_width, state.fail_rate)
                    logging.info("ndr lo external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif ndr_lo.duration < duration:
                    logging.info("ndr lo fail re-measure")
                    state = self._measure_and_update_state(state, duration, state.fail_rate)
                    continue
            if ndr_hi.drop_fraction <= 0.0:
                if ndr_hi.target_tr < state.line_rate:
                    new_tr = min(ndr_hi.target_tr + 2 * ndr_tr_width, state.line_rate)
                    logging.info("ndr hi external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif ndr_hi.duration < duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(state, duration, state.line_rate)
                    continue
            if pdr_lo.drop_fraction > state.allowed_drop_fraction:
                if pdr_lo.target_tr > state.fail_rate:
                    new_tr = max(pdr_lo.target_tr - 2 * pdr_tr_width, state.fail_rate)
                    logging.info("pdr lo external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif pdr_lo.duration < duration:
                    logging.info("DEBUG: pdr lo fail re-measure")
                    state = self._measure_and_update_state(state, duration, state.fail_rate)
                    continue
            if pdr_hi.drop_fraction <= state.allowed_drop_fraction:
                if pdr_hi.target_tr < state.line_rate:
                    new_tr = min(pdr_hi.target_tr + 2 * pdr_tr_width, state.line_rate)
                    logging.info("pdr hi external")
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                elif pdr_hi.duration < duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(state, duration, state.line_rate)
                    continue
            ndr_relative_width = state.result.ndr_interval.rel_tr_width
            pdr_relative_width = state.result.pdr_interval.rel_tr_width
            # If we are hitting line_rate, it is still worth narrowing width,
            # hoping large enough Df will happen.
            # But if we are hitting fail rate (at current duration), no additional measurement
            # will help with that, so we can stop narrowing.
            if ndr_lo.target_tr <= state.fail_rate and ndr_lo.drop_fraction > 0.0:
                ndr_relative_width = 0.0
            if pdr_lo.target_tr <= state.fail_rate and pdr_lo.drop_fraction > state.allowed_drop_fraction:
                pdr_relative_width = 0.0
            max_relative_width = max(ndr_relative_width, pdr_relative_width)
            if max_relative_width <= 0.0:
                # Both intervals are failing. We can give up time bank.
                if state.time_bank > 0.0:
                    state.time_bank = 0.0
            if state.time_bank >= duration:
                # We have time to narrow widths and at least one interval is not failing.
                if ndr_relative_width >= pdr_relative_width:
                    prediction_from_rr = ndr_hi.receive_rate
                    logging.info("ndr section predicted: %s", prediction_from_rr)
                    new_tr = min(max(prediction_from_rr,
                                     ndr_lo.target_tr + ndr_tr_width / 4),
                                 ndr_hi.target_tr - ndr_tr_width / 4)
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
                else:
                    prediction_from_rr = pdr_hi.receive_rate / (1.0 - state.allowed_drop_fraction)
                    # TODO: If pdr_lo.df>0.0 it might be better to use interpolation.
                    logging.info("pdr section predicted: %s", prediction_from_rr)
                    new_tr = min(max(prediction_from_rr,
                                     pdr_lo.target_tr + pdr_tr_width / 4),
                                 pdr_hi.target_tr - pdr_tr_width / 4)
                    state = self._measure_and_update_state(state, duration, new_tr)
                    continue
            # Time is up (or intervals failing), but there still might be some measurements with smaller duration.
            # We need to re-measure with full duration, possibly creating improper bounds to resolve.
            if ndr_lo.duration < duration:
                logging.info("re-measuring NDR lower bound")
                self._measure_and_update_state(state, duration, ndr_lo.target_tr)
                continue
            # Except when lower bounds have high rate, in that case we do not need to re-measure _upper_ bounds.
            if ndr_hi.duration < duration and ndr_relative_width > 0.0:
                logging.info("re-measuring NDR upper bound")
                self._measure_and_update_state(state, duration, ndr_hi.target_tr)
                continue
            if pdr_lo.duration < duration:
                logging.info("re-measuring PDR lower bound")
                self._measure_and_update_state(state, duration, pdr_lo.target_tr)
                continue
            if pdr_hi.duration < duration and pdr_relative_width > 0.0:
                logging.info("re-measuring PDR upper bound")
                self._measure_and_update_state(state, duration, pdr_hi.target_tr)
                continue
            # Time is up, bound measurements are long enough, we can return.
            logging.info("duration done")
            break
        return state
