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

    This class contains most of replacement and selection logic required
    for MLRsearch. One exception is lack of any special handling for maximal
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
        self.durations = sorted(self.data_for_duration.keys())

    def __repr__(self):
        """Return string executable to get equivalent instance.

        :returns: Code to construct equivalent instance.
        :rtype: str
        """
        return f"MeasurementDatabase(measurements={self.data_for_duration!r})"

    def add(self, measurement):
        """Add a measurement.

        :param measurement: Measurement result to add to the database.
        :type measurement: ReceiveRateMeasurement
        """
        duration = measurement.duration
        if self.durations and self.durations[-1] > duration:
            raise ValueError(
                f"{measurement!r} duration shorter than {self.durations[-1]}"
            )
        if duration in self.data_for_duration:
            self.data_for_duration[duration].add(measurement)
        else:
            self.data_for_duration[duration] = PerDurationDatabase(
                duration, [measurement]
            )
            self.durations = sorted(self.data_for_duration.keys())

    def get_valid_lower_bound(self, ratio, min_tr=None, max_tr=None):
        """Return None or a valid lower bound measurement.

        Actually, a pair of values is returned. The first is for max duration,
        the second for second longest duration (as this is useful for MLRsearch).
        The second value is computed only if the first is None.

        Candidate measurements can be optionally limited in target_tr.

        :param ratio: Target ratio, valid has to be lower or equal to this.
        :param min_tr: Candidate measurements must have target_tr larger. [tps]
        :param max_tr: Candidate measurements must have target_tr smaller. [tps]
        :type ratio: float
        :type min_tr: Optional[float]
        :type max_tr: Optional[float]
        :returns: Pair of values, at most one is a measurement useful as bound.
        :rtype: 2-tuple of Optional[ReceiveRateMeasurement]
        """
        if not self.durations:
            return None, None
        database = self.data_for_duration[self.durations[-1]]
        bound = database.get_valid_lower_bound(ratio, min_tr, max_tr)
        if bound is not None or len(self.durations) == 1:
            return bound, None
        database = self.data_for_duration[self.durations[-2]]
        bound = database.get_valid_lower_bound(ratio, min_tr, max_tr)
        return None, bound

    def get_valid_upper_bound(self, ratio, min_tr=None, max_tr=None):
        """Return None or a valid upper bound measurement.

        Actually, a pair of values is returned. The first is for max duration,
        the second for second longest duration (as this is useful for MLRsearch).
        The second value is computed only if the first is None.

        Candidate measurements can be optionally limited in target_tr.

        :param ratio: Target ratio, valid has to be greater than this.
        :param min_tr: Candidate measurements must have target_tr larger. [tps]
        :param max_tr: Candidate measurements must have target_tr smaller. [tps]
        :type ratio: float
        :type min_tr: Optional[float]
        :type max_tr: Optional[float]
        :returns: Pair of values, at most one is a measurement useful as bound.
        :rtype: 2-tuple of Optional[ReceiveRateMeasurement]
        """
        if not self.durations:
            return None, None
        database = self.data_for_duration[self.durations[-1]]
        bound = database.get_valid_upper_bound(ratio, min_tr, max_tr)
        if bound is not None or len(self.durations) == 1:
            return bound, None
        database = self.data_for_duration[self.durations[-2]]
        bound = database.get_valid_upper_bound(ratio, min_tr, max_tr)
        return None, bound

    def get_results(self, ratio_list):
        """Return list of intervals for given ratios.

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
        measurements = self.data_for_duration[self.durations[-1]]
        for ratio in ratio_list:
            lower_bound, _ = self.get_valid_lower_bound(ratio)
            if lower_bound is None:
                lower_bound = measurements[0]
            upper_bound, _ = self.get_valid_upper_bound(ratio)
            if upper_bound is None:
                upper_bound = measurements[-1]
            ret_list.append(ReceiveRateInterval(lower_bound, upper_bound))
        return ret_list
