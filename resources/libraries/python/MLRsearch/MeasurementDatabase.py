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

import copy

from robot.api import logger

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

    def __init__(self, database):
        """Store per-duration databases, sort and store durations.

        Deepcopy is used so further processing does not affect the argument.

        :param database: Measurements grouped by their durations.
        :type database: Mapping[float, PerDurationDatabase]
        """
        self.durations = list()
        self.data_for_duration = dict()
        for duration, data in database.items():
            self._ensure_duration(duration)
            self.data_for_duration[duration] = copy.deepcopy(data)

    def __repr__(self):
        """Return string executable to get equivalent instance.

        :returns: Code to construct equivalent instance.
        :rtype: str
        """
        return f"MeasurementDatabase(database={self.data_for_duration!r})"

    @classmethod
    def from_list(cls, measurements):
        """Form a database out of unsorted list of measurements.

        :param measurements: The measurement results for database to contain.
        :type measurements: Iterable[ReceiveRateMeasurement]
        :returns: New MeasurementDatabase containing the measurements.
        :rtype: cls
        """
        database = cls(dict())
        for measurement in measurements:
            database.add(measurement, ignore_current_duration=True)
        return database

    def _ensure_duration(self, duration):
        """If not present, add new empty per duration database for the duration.

        :param duration: New duration for per duration database, in seconds.
        :type duration: float
        :raises RuntimeError: If the duration is only partially present.
        """
        disd = duration in self.durations
        disdfdk = duration in self.data_for_duration.keys()
        if disd and disdfdk:
            return
        if disd or disdfdk:
            raise RuntimeError(f"Duration {duration} incosistent: {self!r}")
        self.durations.append(duration)
        self.durations.sort()
        self.data_for_duration[duration] = PerDurationDatabase(duration, [])

    @property
    def current_duration(self):
        """Return None or largest duration present.

        :returns: Largest duration (can have empty PerDurationDatabase).
        :rtype: float
        """
        return self.durations[-1] if self.durations else None

    @property
    def previous_duration(self):
        """Return None or second largest duration present.

        :returns: Largest duration (should not have empty PerDurationDatabase).
        :rtype: float
        """
        return self.durations[-2] if len(self.durations) >= 2 else None

    def set_current_duration(self, duration):
        """Remember what MLRsearch considers the current duration.

        Setting the same duration is allowed, setting smaller is not allowed.

        :param duration: Target trial duration of current phase, in seconds.
        :type duration: float
        :raises RuntimeError: If the duration is smaller than previous.
        """
        logger.debug(f"scd {self!r}")
        if duration < self.current_duration:
            raise RuntimeError(
                f"Duration {duration} shorter than current duration"
                f" {self.current_duration}"
            )
        self._ensure_duration(duration)

    def add(self, measurement, ignore_current_duration=False):
        """Add a measurement. Optionally, duration has to match the set one.

        :param measurement: Measurement result to add to the database.
        :param ignore_current_duration: Do not check duration if true.
        :type measurement: ReceiveRateMeasurement
        :type ignore_current_duration: bool
        :raise RuntimeError: If duration is checked and does not match.
        """
        duration = measurement.duration
        if not ignore_current_duration:
            if duration != self.current_duration:
                raise RuntimeError(
                    f"{measurement!r} duration different than"
                    f" {self.current_duration}"
                )
        else:
            self._ensure_duration(duration)
        self.data_for_duration[duration].add(measurement)

    def get_bounds(self, ratio):
        """Return 6 bounds: lower/upper, current/previous, tightest/second.

        Second tightest bounds are only returned for current duration.
        None instead of a measurement if there is no measurement of that type.

        The result contains bounds in this order:
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
        This can result in degenerate intervals,
        but is expected e.g. if max load had zero loss.

        :param ratio_list: Ratios to create intervals for.
        :type ratio_list: Iterable[float]
        :returns: List of intervals.
        :rtype: List[ReceiveRateInterval]
        """
        ret_list = list()
        current_data = self.data_for_duration[self.current_duration]
        for ratio in ratio_list:
            lower_bound, upper_bound, _, _, _, _ = self.get_bounds(ratio)
            # TODO: Enrich PerDurationDatabase API, instead of assuming
            # it allways be a sorted list.
            if lower_bound is None:
                lower_bound = current_data.smallest_load_measurement
            if upper_bound is None:
                upper_bound = current_data.largest_load_measurement
            ret_list.append(ReceiveRateInterval(lower_bound, upper_bound))
        return ret_list
