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

from .ReceiveRateInterval import ReceiveRateInterval
from .PerDurationDatabase import PerDurationDatabase


class MeasurementDatabase:
    """A structure holding measurement results.

    The implementation uses a dict from duration values
    to PerDurationDatabase instances.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.

    This class contains the "find tightest bounds" parts of logic required
    by MLRsearch. One exception is lack of any special handling for maximal
    or minimal rates.
    """

    def __init__(self, measurements):
        """Store measurement results in per-duration databases.

        TODO: Move processing to a factory method,
        keep constructor only to store (presumably valid) values.

        If the measurements argument contains is a dict,
        the constructor assumes it contains the processed databases.

        :param measurements: The measurement results to store.
        :type measurements: Iterable[ReceiveRateMeasurement]
        """
        if isinstance(measurements, dict):
            self.data_for_duration = measurements
        else:
            self.data_for_duration = dict()
            # TODO: There is overlap with add() code. Worth extracting?
            for measurement in measurements:
                duration = measurement.duration
                if duration in self.data_for_duration:
                    self.data_for_duration[duration].add(measurement)
                else:
                    self.data_for_duration[duration] = PerDurationDatabase(
                        duration, [measurement]
                    )
        durations = sorted(self.data_for_duration.keys())
        self.current_duration = durations[-1] if duration else None
        self.previous_duration = durations[-2] if len(durations) > 1 else None

    def __repr__(self):
        """Return string executable to get equivalent instance.

        :returns: Code to construct equivalent instance.
        :rtype: str
        """
        return f"MeasurementDatabase(measurements={self.data_for_duration!r})"

    def set_current_duration(self, duration):
        """Remember what MLRsearch considers the current duration.

        Setting the same duration is allowed, setting smaller is not allowed.

        :param duration: Target trial duration of current phase, in seconds.
        :type duration: float
        :raises ValueError: If the duration is smaller than previous.
        """
        if duration < self.current_duration:
            raise ValueError(
                f"Duration {duration} shorter than current duration"
                f" {self.current_duration}"
            )
        if duration > self.current_duration:
            self.previous_duration = self.current_duration
            self.current_duration = duration
            self.data_for_duration[duration] = PerDurationDatabase(
                duration, list()
            )
        # Else no-op.

    def add(self, measurement):
        """Add a measurement. Duration has to match the set one.

        :param measurement: Measurement result to add to the database.
        :type measurement: ReceiveRateMeasurement
        """
        duration = measurement.duration
        if duration != self.current_duration:
            raise ValueError(
                f"{measurement!r} duration different than"
                f" {self.current_duration}"
            )
        self.data_for_duration[duration].add(measurement)

    def get_bounds(self, ratio):
        """Return 6 bounds: lower/upper, current/previous, tightest/second.

        Second tightest bounds are only returned for current duration.
        None instead of a measurement if there is no measurement of that type.

        The result cotains bounds in this order:
        1. Tightest lower bound for current duration.
        2. Tightest upper bound for current duration.
        3. Tightest lower bound for previous duration.
        4. Tightest upper bound for previous duration.
        5. Second tightest lower bound for current duration.
        6. Second tightest upper bound for current duration.

        :param ratio: Target ratio, valid has to be lower or equal.
        :type ratio: float
        :returns: Measurements acting as various bounds.
        :rtype: 6-tuple of Optional[PerDurationDatabase]
        """
        cur_lo1, cur_hi1, pre_lo, pre_hi, cur_lo2, cur_hi2 = [None] * 6
        duration = self.current_duration
        if duration is not None:
            data = self.data_for_duration[duration]
            cur_lo1, cur_hi1, cur_lo2, cur_hi2 = data.get_valid_bounds(ratio)
        duration = self.previous_duration
        if duration is not None:
            data = self.data_for_duration[duration]
            pre_lo, pre_hi, _, _ = data.get_valid_bounds(ratio)
        return cur_lo1, cur_hi1, pre_lo, pre_hi, cur_lo2, cur_hi2

    def get_results(self, ratio_list):
        """Return list of intervals for given ratios, from current duration.

        Attempt to construct valid intervals. If a valid bound is missing,
        use smallest/biggest target_tr for lower/upper bound.
        This can result in degenerate intervals.

        :param ratio_list: Ratios to create intervals for.
        :type ratio_list: Iterable[float]
        :returns: List of intervals.
        :rtype: List[ReceiveRateInterval]
        """
        ret_list = list()
        measurements = self.data_for_duration[self.current_duration].measurements
        for ratio in ratio_list:
            lower_bound, upper_bound, _, _, _, _ = self.get_bounds(ratio)
            if lower_bound is None:
                lower_bound = measurements[0]
            if upper_bound is None:
                upper_bound = measurements[-1]
            ret_list.append(ReceiveRateInterval(lower_bound, upper_bound))
        return ret_list
