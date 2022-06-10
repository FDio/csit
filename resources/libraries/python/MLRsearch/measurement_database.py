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

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .comparable_measurement_result import ComparableMeasurementResult as Result
from .measurement_interval import MeasurementInterval


MaybeResult = Optional[Result]
"""Just to make the 4-tuple type fit into a single line."""


@dataclass
class MeasurementDatabase:
    """Structure holding measurement results for multiple durations.

    Several utility methods are added, accomplishing tasks useful for MLRsearch.
    The replacement logic is benevolent both for higher loads
    (where effective loss ratio hides lucky long duration results),
    and for small loads (overridden ratio hides lucky short duration results).

    The constructor uses shallow copy, so users should not edit
    the measurement results afterwards.
    """

    measurements: List[Result]
    """The measurement results to store, kept in normalized form."""

    def __post_init__(self) -> None:
        """Store (shallow copy of) measurement results and normalize them."""
        self.measurements = list(self.measurements)
        self._normalize()

    def _normalize(self) -> None:
        """Sort, remove obsoleted results, set effective and overridden ratios.

        MLRsearch algorithm needs several assumptions to ensure convergence,
        but real results may violate those assumptions.
        The main anomaly to deal with is when a measurement at higher load
        results in smaller loss ratio than at lower load.

        The normalization here restores the assumptions
        by selectively removing old measurement results,
        or overriding some loss ratios to safe "conservative" values.

        There are three specific situations which need to be addressed:

        1. If there are two trial measurements done at exactly the same
        intended load. In that case, the shorter duration one
        has no purpose, so is removed from database.

        2. If a longer duration trial has smaller loss rate than
        a shorter duration trial at lower load. In this case, the shorter
        duration can still become useful (e.g. when the longer gets deleted
        due to point 1 later), but its loss rate needs to be hidden.
        That is done by setting its overridden loss rate.

        3. If the same duration trial (other cases are handled
        by previous points) at lower load has higher loss rate.
        In this case, it is the higher load result that is deemed "lucky",
        so its effective loss ratio is increased.

        Keeping the list of results sorted allows all the points to be applied
        quickly by iterating in the correct direction.
        """
        self.measurements.sort()
        # Remove obsolete result, override conflicting loss ratios.
        last_by_duration = dict()
        new_reversed_measurements = list()
        for measurement in reversed(self.measurements):
            duration = measurement.intended_duration
            # Old overrides may be too aggressive, recompute.
            measurement.overridden_loss_ratio = measurement.loss_ratio
            for other_duration, other_measurement in last_by_duration.items():
                if other_duration < duration:
                    # Fine, keep comparing with others.
                    continue
                if other_measurement.intended_load == measurement.intended_load:
                    # Obsoleted, do not keep.
                    break
                ratio_override = other_measurement.overridden_loss_ratio
                if (
                    other_duration > measurement.intended_duration
                    and ratio_override < measurement.overridden_loss_ratio
                ):
                    # We cannot remove the measurement,
                    # as it can be the latest one, but we have to override.
                    measurement.overridden_loss_ratio = ratio_override
                    # Continue, there may be a stricter override.
            else:
                new_reversed_measurements.append(measurement)
                last_by_duration[duration] = measurement
        self.measurements = new_reversed_measurements
        self.measurements.reverse()
        # Update effective ratios.
        ratio_previous = None
        for measurement in self.measurements:
            if ratio_previous is None:
                ratio_previous = measurement.overridden_loss_ratio
                measurement.effective_loss_ratio = ratio_previous
                continue
            ratio_previous = max(
                ratio_previous, measurement.overridden_loss_ratio
            )
            measurement.effective_loss_ratio = ratio_previous

    def add(self, measurement: Result) -> None:
        """Add measurement and normalize.

        :param measurement: Measurement result to add to the database.
        :type measurement: MeasurementResult
        """
        self.measurements.append(measurement)
        self._normalize()

    def get_valid_bounds(
        self, ratio: float, min_duration: float
    ) -> Tuple[MaybeResult, MaybeResult, MaybeResult, MaybeResult]:
        """Return None or a valid measurement for two tightest bounds.

        Measurement results with smaller duration are ignored.

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
        :rtype: 4-tuple of Optional[ComparableMeasurementResult]
        """
        lower_1, upper_1, lower_2, upper_2 = None, None, None, None
        for measurement in self.measurements:
            if measurement.intended_duration < min_duration:
                continue
            if measurement.effective_loss_ratio > ratio:
                if upper_1 is None:
                    upper_1 = measurement
                    continue
                upper_2 = measurement
                break
            lower_1, lower_2 = measurement, lower_1
        return lower_1, upper_1, lower_2, upper_2

    def smallest_load_measurement(self, min_duration: float) -> Result:
        """Return measurement with smallest load and large enough duration.

        :param min_duration: Consider results with at least this duration [s].
        :type min_duration: float
        :returns: Measurement in this with smallest intended_load.
        :rtype: ComparableMeasurementResult
        :raises RuntimeError: If no results at requested duration.
        """
        for measurement in self.measurements:
            if measurement.duration < min_duration:
                continue
            return measurement
        raise RuntimeError(f"No smallest duration {min_duration}: {self!r}")

    def largest_load_measurement(self, min_duration: float) -> Result:
        """Return measurement with largest load and large enough duration.

        :param min_duration: Consider results with at least this duration [s].
        :type min_duration: float
        :returns: Measurement in this with largest intended_load.
        :rtype: ComparableMeasurementResult
        :raises RuntimeError: If no results at requested duration.
        """
        for measurement in reversed(self.measurements):
            if measurement.duration < min_duration:
                continue
            return measurement
        raise RuntimeError(f"No largest duration {min_duration}: {self!r}")

    def get_intervals(
        self, ratio_list: List[float], duration: float
    ) -> List[MeasurementInterval]:
        """Return list of intervals for given ratios, at the duration.

        This assumes no trial had larger duration.

        Attempt to construct valid intervals. If a valid bound is missing,
        use smallest/biggest intended_load for lower/upper bound.
        This can result in degenerate intervals,
        but is expected e.g. if max load has zero loss.

        :param ratio_list: Ratios to create intervals for.
        :type ratio_list: Iterable[float]
        :returns: List of intervals.
        :rtype: List[MeasurementInterval]
        """
        ret_list = list()
        for ratio in ratio_list:
            bounds = self.get_valid_bounds(ratio=ratio, min_duration=duration)
            lower_bound, upper_bound, _, _ = bounds
            if lower_bound is None:
                lower_bound = self.smallest_load_measurement(duration)
            if upper_bound is None:
                upper_bound = self.largest_load_measurement(duration)
            ret_list.append(MeasurementInterval(lower_bound, upper_bound))
        return ret_list
