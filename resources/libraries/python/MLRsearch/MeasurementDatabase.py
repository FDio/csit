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

"""Module defining MeasurementDatabase class."""

import logging

from .ReceiveRateMeasurement import ReceiveRateMeasurement
from .ReceiveRateInterval import ReceiveRateInterval


class MeasurementDatabase:
    """Dict-like structure holding measurement results.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.
    All methods assume there is a non-zero number of measurements.

    This class contains most of replacement and selection logic required
    for MLRsearch. One exception is lack of any special handling for maximal
    or minimal rates.
    """

    def __init__(self, measurements):
        """Store (copy of) measurement results and normalize them.

        :param measurements: The measurement results to store.
        :type measurements: Iterable[ReceiveRateMeasurement]
        """
        self.measurements = [measurement.copy() for measurement in measurements]
        self._normalize()

    def __repr__(self):
        """Return string executable to get equivalent instance.

        :returns: Code to construct equivalent instance.
        :rtype: str
        """
        return f"MeasurementDatabase(measurements={self.measurements!r})"

    def _normalize(self):
        """Sort by target_tr, keep only one result per target_tr.

        Also set effective loss ratios.

        If durations differ, keep the longer duration result.
        If loss ratios differ, keep the more lossy result.
        Otherwise keep the most recent result.
        """
        measurements_old = self.measurements
        measurements_new = list()
        while len(measurements_old) > 0:
            # Find next bext measurement.
            best_measurement = None
            best_tr = None
            best_index = None
            for index, measurement in enumerate(measurements_old):
                if best_index is None:
                    best_index, best_measurement = index, measurement
                    best_tr = best_measurement.target_tr
                    continue
                measured_tr = measurement.target_tr
                if measured_tr > best_tr:
                    continue
                if measured_tr == best_tr:
                    if measurement.duration > best_measurement.duration:
                        best_index, best_measurement = index, measurement
                        best_tr = best_measurement.target_tr
                        continue
                # measured_tr < best_tr
                best_index, best_measurement = index, measurement
                best_tr = best_measurement.target_tr
            measurements_new.append(best_measurement)
            # Remove duplicates.
            measurements_old = [
                measurement for measurement in measurements_old
                if measurement.target_tr > best_tr
            ]
        # Update effective ratios.
        ratio_previous = None
        for measurement in measurements_new:
            if ratio_previous is None:
                ratio_previous = measurement.loss_ratio
                measurement.effective_loss_ratio = ratio_previous
                continue
            ratio_previous = max(ratio_previous, measurement.loss_ratio)
            measurement.effective_loss_ratio = ratio_previous
        self.measurements = measurements_new

    def add(self, measurement):
        """Add measurement and normalize.

        :param measurement: Measurement result to add to the database.
        :type measurement: ReceiveRateMeasurement
        """
        self.measurements.append(measurement)
        self._normalize()

    def get_valid_lower_bound(self, ratio):
        """Return None or a valid lower bound measurement.

        Duration does not matter, MLRsearch should re-measure
        to avoid short duration bounds.

        :param ratio: Target ratio, valid has to be lower or equal.
        :type ratio: float
        :returns: Whether database has measurement good for valid lower bound.
        :rtype: ReceiveRateMeasurement
        """
        bound = None
        for measurement in self.measurements:
            if measurement.effective_loss_ratio > ratio:
                # Measurements are sorted, so no point searching further.
                break
            bound = measurement
            # Continuing to find a tighter bound.
        return bound

    def get_valid_upper_bound(self, ratio):
        """Return None or a valid upper bound measurement.

        Duration does not matter, MLRsearch should re-measure
        to avoid short duration bounds.

        :param ratio: Target ratio, valid has to be lower or equal.
        :type ratio: float
        :returns: Whether database has measurement good for valid lower bound.
        :rtype: ReceiveRateMeasurement
        """
        bound = None
        for measurement in reversed(self.measurements):
            if measurement.effective_loss_ratio <= ratio:
                # Measurements are sorted, so no point searching further.
                break
            bound = measurement
            # Continuing to find a tighter bound.
        return bound

    def select_tr_for_lower_bound(self, ratio, min_rate, max_rate):
        """Choose next target load based on conditions and measurements.

        This is a very specific method to be used by MLRsearch.
        As measurements from smaller durations are likely to have similar
        loss ratio upon re-measuring at higher durations,
        this method attemps to find such a measurement and return its target_tr.
        The measurement has to have low enough effective loss ratio.
        MLRsearch gives min_rate and max_rate as additional conditions,
        due to window width reasons. If no measurement fits in the interval
        (target_tr equal to min_rate or max_rate fits), return min_rate.
        If multiple measurements fit, return the largest target_tr.

        :param ratio: Loss ratio, measurements need to have equal or smaller.
        :param min_rate: Minimal transmit rate eligible for selection.
        :param max_rate: Maximal transmit rate eligible for selection.
        :type ratio: float
        :type min_rate: float
        :type max_rate: float
        :returns: Next candidate transmit rate fitting the conditions.
        :rtype: float
        """
        for measurement in reversed(self.measurements):
            measured_tr = measurement.target_tr
            if measured_tr > max_rate:
                continue
            if measured_tr < min_rate:
                break
            measured_ratio = measurement.effective_loss_ratio
            if measured_ratio > ratio:
                continue
            return measured_tr
        return min_rate

    def select_tr_for_upper_bound(self, ratio, min_rate, max_rate):
        """Choose next target load based on conditions and measurements.

        This is a very specific method to be used by MLRsearch.
        As measurements from smaller durations are likely to have similar
        loss ratio upon re-measuring at higher durations,
        this method attemps to find such a measurement and return its target_tr.
        The measurement has to have high enough effective loss ratio.
        MLRsearch gives min_rate and max_rate as additional conditions,
        due to window width reasons. If no measurement fits in the interval
        (target_tr equal to min_rate or max_rate fits), return max_rate.
        If multiple measurements fit, return the smallest target_tr.

        :param ratio: Loss ratio, measurements need to have equal or larger.
        :param min_rate: Minimal transmit rate eligible for selection.
        :param max_rate: Maximal transmit rate eligible for selection.
        :type ratio: float
        :type min_rate: float
        :type max_rate: float
        :returns: Next candidate transmit rate fitting the conditions.
        :rtype: float
        """
        for measurement in self.measurements:
            measured_tr = measurement.target_tr
            if measured_tr < min_rate:
                continue
            if measured_tr > max_rate:
                break
            measured_ratio = measurement.effective_loss_ratio
            if measured_ratio < ratio:
                continue
            return measured_tr
        return max_rate

    def get_results(self, ratio_list):
        """Return list of interval for given ratios.

        Attempt to construct valid intervals. If a valid bound is missing,
        use smallest/biggest target_tr for lower/upper bound.
        This can result in degenerate intervals.
        The current implementation does not care about durations.

        :param ratio_list: Ratios to create intervals for.
        :type ratio_list: Iterable[float]
        :returns: List of intervals.
        :rtype: List[ReceiveRateInterval]
        """
        ret_list = list()
        for ratio in ratio_list:
            lower_bound = self.get_valid_lower_bound(ratio)
            if lower_bound is None:
                lower_bound = self.measurements[0]
            upper_bound = self.get_valid_upper_bound(ratio)
            if upper_bound is None:
                upper_bound = self.measurements[-1]
            ret_list.append(ReceiveRateInterval(lower_bound, upper_bound))
        return ret_list
