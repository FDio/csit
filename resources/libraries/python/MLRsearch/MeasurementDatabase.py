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

"""Module defining MeasurementDatabase class."""

import copy

from .ReceiveRateInterval import ReceiveRateInterval


class MeasurementDatabase:
    """Structure holding measurement results for multiple durations.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.
    The replacement logic is benevolent for higher loads
    (where effective loss ratio hides lucky short duration results),
    but uses strict removal for small loads
    (as longer results are hard limits, incompatible short results are removed).
    """

    def __init__(self, measurements):
        """Store (deep copy of) measurement results and normalize them.

        Empty iterable (zero measurements) is an acceptable input.

        :param measurements: The measurement results to store.
        :type measurements: Iterable[ReceiveRateMeasurement]
        """
        self.measurements = [copy.deepcopy(meas) for meas in measurements]
        self._normalize()

    def __repr__(self):
        """Return string executable to get equivalent instance.

        :returns: Code to construct equivalent instance.
        :rtype: str
        """
        return f"NewDatabase(measurements={self.measurements!r})"

    def _normalize(self):
        """Sort, remove obsoleted results, set effective loss ratios.

        TODO: Explain the logic.
        """
        self.measurements.sort()
        # Remove shorter and worse results at same or smaller load.
        last_by_duration = dict()
        new_reversed_measurements = list()
        for measurement in reversed(self.measurements):
            duration = measurement.duration
            for other_duration, other_measurement in last_by_duration.items():
                if other_duration < duration:
                    continue
                if other_measurement.target_tr == measurement.target_tr:
                    break
                if other_measurement.loss_ratio < measurement.loss_ratio:
                    if other_duration > measurement.duration:
                        break
            else:
                new_reversed_measurements.append(measurement)
                last_by_duration[duration] = measurement
        self.measurements = new_reversed_measurements
        self.measurements.reverse()
        # Update effective ratios.
        ratio_previous = None
        for measurement in self.measurements:
            if ratio_previous is None:
                ratio_previous = measurement.loss_ratio
                measurement.effective_loss_ratio = ratio_previous
                continue
            ratio_previous = max(ratio_previous, measurement.loss_ratio)
            measurement.effective_loss_ratio = ratio_previous

    def add(self, measurement):
        """Add measurement and normalize.

        :param measurement: Measurement result to add to the database.
        :type measurement: ReceiveRateMeasurement
        """
        self.measurements.append(copy.deepcopy(measurement))
        self._normalize()

    def get_valid_bounds(self, ratio, min_duration):
        """Return None or a valid measurement for two tightest bounds.

        Measurement result with smaller duration are ignored.

        The validity of a measurement to act as a bound is determined
        by comparing the argument ratio with measurement's effective loss ratio.

        Both lower and upper bounds are returned, both tightest and second
        tightest. If some value is not available, None is returned instead.

        :param ratio: Target ratio, valid has to be lower or equal.
        :param min_duration: Consider results with at least this duration [s].
        :type ratio: float
        :type min_duration: float
        :returns: Tightest lower bound, tightest upper bound,
            second tightest lower bound, second tightest upper bound.
        :rtype: 4-tuple of Optional[ReceiveRateMeasurement]
        """
        lower_1, upper_1, lower_2, upper_2 = None, None, None, None
        for measurement in self.measurements:
            if measurement.duration < min_duration:
                continue
            if measurement.effective_loss_ratio > ratio:
                if upper_1 is None:
                    upper_1 = measurement
                    continue
                upper_2 = measurement
                break
            lower_1, lower_2 = measurement, lower_1
        return lower_1, upper_1, lower_2, upper_2

    def smallest_load_measurement(self, min_duration):
        """Return measurement with smallest load.

        :param min_duration: Consider results with at least this duration [s].
        :type min_duration: float
        :returns: Measurement in this with smallest target_tr.
        :rtype: ReceiveRateMeasurement
        :raises RuntimeError: If no results at requested duration.
        """
        for measurement in self.measurements:
            if measurement.duration < min_duration:
                continue
            return measurement
        raise RuntimeError(f"No smallest duration {min_duration}: {self!r}")

    def largest_load_measurement(self, min_duration):
        """Return measurement with largest load.

        :param min_duration: Consider results with at least this duration [s].
        :type min_duration: float
        :returns: Measurement in this with largest target_tr.
        :rtype: ReceiveRateMeasurement
        :raises RuntimeError: If no results at requested duration.
        """
        for measurement in reversed(self.measurements):
            if measurement.duration < min_duration:
                continue
            return measurement
        raise RuntimeError(f"No largest duration {min_duration}: {self!r}")

    def get_results(self, ratio_list, duration):
        """Return list of intervals for given ratios, at the duration.

        This assumes no trial had larger duration.

        Attempt to construct valid intervals. If a valid bound is missing,
        use smallest/biggest target_tr for lower/upper bound.
        This can result in degenerate intervals,
        but is expected e.g. if max load had zero loss.

        :param ratio_list: Ratios to create intervals for.
        :type ratio_list: Iterable[float]
        :returns: List of intervals.
        :rtype: List[ReceiveRateInterval]
        """
        ret_list = list()
        for ratio in ratio_list:
            bounds = self.get_valid_bounds(ratio, duration)
            lower_bound, upper_bound, _, _ = bounds
            if lower_bound is None:
                lower_bound = self.smallest_load_measurement(duration)
            if upper_bound is None:
                upper_bound = self.largest_load_measurement(duration)
            ret_list.append(ReceiveRateInterval(lower_bound, upper_bound))
        return ret_list
