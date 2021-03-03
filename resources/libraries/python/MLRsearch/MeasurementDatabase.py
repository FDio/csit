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
        durations = sorted(self.data_for_duration.keys())
        self.current_duration = durations[-1] if duration else None
        self.previous_duration = durations[-2] if len(durations) > 1 else None

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
        if self.current_duration is not None:
            if duration < self.current_duration:
                raise ValueError(
                    f"{measurement!r} duration shorter than"
                    f" {self.current_duration}"
                )
        if duration in self.data_for_duration:
            self.data_for_duration[duration].add(measurement)
            return
        self.data_for_duration[duration] = PerDurationDatabase(
            duration, [measurement]
        )
        self.previous_duration = self.current_duration
        self.current_duration = duration

    def get_values_for_ratio(self, ratio, duration=None):
        """Return lower bound, upper bound and hint from shorter duration.

        Returned bounds are from the current duration and have to be valid.
        If no valid bound exists, None is returned intead of a real bound.
        Hint is a valid bound from previous duration. It has to fall between
        the current duration bounds. Lower bound is preferred for hint.

        The duration argument is needed, because new MLRsearch phase
        call this before adding first measurement for new duration.
        The given value has to be equal or larger
        than biggest duration in database. If None, current duration is used.

        :param ratio: Target ratio, valid has to be lower or equal to this.
        :param duration: Duration [s] of valid bounds.
        :type ratio: float
        :param duration: Optional[float]
        :returns: Three measurements: lower bound, upper bound and hint.
        :rtype: 3-tuple of Optional[ReceiveRateMeasurement]
        """
        if self.current_duration is None:
            return None, None, None
        if duration is None:
            duration = self.current_duration
        if duration < self.current_duration:
            raise RuntimeError(u"Asked for too short duration.")
        if duration == self.current_duration:
            data = self.data_for_duration[self.current_duration]
            lower_bound, upper_bound = data.get_valid_bounds(ratio)
            hint_duration = self.previous_duration
        else:
            lower_bound, upper_bound = None, None
            hint_duration = self.current_duration
        if hint_duration is None:
            return lower_bound, upper_bound, None
        data = self.data_for_duration[hint_duration]
        lower_hint, upper_hint = data.get_valid_bounds(ratio)
        if lower_bound is not None:
            if lower_hint is not None:
                if lower_hint.target_tr <= lower_bound.target_tr:
                    lower_hint = None
            if upper_hint is not None:
                if upper_hint.target_tr <= lower_bound.target_tr:
                    upper_hint = None
        if upper_bound is not None:
            if lower_hint is not None:
                if lower_hint.target_tr >= upper_bound.target_tr:
                    lower_hint = None
            if upper_hint is not None:
                if upper_hint.target_tr >= upper_bound.target_tr:
                    upper_hint = None
        hint = upper_hint if lower_hint is None else lower_hint
        return lower_bound, upper_bound, hint

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
        measurements = self.data_for_duration[self.current_duration].measurements
        for ratio in ratio_list:
            lower_bound, upper_bound, _ = self.get_values_for_ratio(ratio)
            if lower_bound is None:
                lower_bound = measurements[0]
            if upper_bound is None:
                upper_bound = measurements[-1]
            ret_list.append(ReceiveRateInterval(lower_bound, upper_bound))
        return ret_list
