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

"""Module defining PerDurationDatabase class."""

import copy


class PerDurationDatabase:
    """List-like structure holding measurement results for one duration.

    This is a building block for MeasurementDatabase.

    This class hold measurements for single target duration value only,
    so the logic is quite simple.

    Several utility methods are added, accomplishing tasks useful for MLRsearch
    (to be called by MeasurementDatabase).
    """

    def __init__(self, duration, measurements):
        """Store (deep copy of) measurement results and normalize them.

        The results have to have the corresponding target duration,
        and there should be no duplicate target_tr values.
        Empty iterable (zero measurements) is an acceptable input.

        :param duration: All measurements have to have this target duration [s].
        :param measurements: The measurement results to store.
        :type duration: float
        :type measurements: Iterable[ReceiveRateMeasurement]
        :raises ValueError: If duration does not match or if TR duplicity.
        """
        self.duration = duration
        self.measurements = [copy.deepcopy(meas) for meas in measurements]
        self._normalize()

    def __repr__(self):
        """Return string executable to get equivalent instance.

        :returns: Code to construct equivalent instance.
        :rtype: str
        """
        return (
            u"PerDurationDatabase("
            f"duration={self.duration!r},"
            f"measurements={self.measurements!r})"
        )

    def _normalize(self):
        """Sort by target_tr, fail on detecting duplicate target_tr.

        Also set effective loss ratios.

        :raises ValueError: If duration does not match or if TR duplicity.
        """
        self.measurements.sort(key=lambda measurement: measurement.target_tr)
        # Detect duplicated TRs.
        previous_tr = None
        for measurement in self.measurements:
            current_tr = measurement.target_tr
            if current_tr == previous_tr:
                raise ValueError(
                    u"Transmit rate conflict:"
                    f" {measurement!r} {previous_tr!r}"
                )
            previous_tr = current_tr
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

    def get_valid_bounds(self, ratio):
        """Return None or a valid measurement for two tightest bounds.

        The validity of a measurement to act as a bound is determined
        by comparing the argument ratio with measurement's effective loss ratio.

        Both lower and upper bounds are returned, both tightest and second
        tightest. If some value is not available, None is returned instead.

        :param ratio: Target ratio, valid has to be lower or equal.
        :type ratio: float
        :returns: Tightest lower bound, tightest upper bound,
            second tightest lower bound, second tightest upper bound.
        :rtype: 4-tuple of Optional[ReceiveRateMeasurement]
        """
        lower_1, upper_1, lower_2, upper_2 = None, None, None, None
        for measurement in self.measurements:
            if measurement.effective_loss_ratio > ratio:
                if upper_1 is None:
                    upper_1 = measurement
                    continue
                upper_2 = measurement
                break
            lower_1, lower_2 = measurement, lower_1
        return lower_1, upper_1, lower_2, upper_2

    @property
    def smallest_load_measurement(self):
        """Return measurement with smallest load.

        One-liner just so MeasurementDatabase does not assume a list.

        :returns: Measurement in this with smallest target_tr.
        :rtype: ReceiveRateMeasurement
        :raises IndexError: If per duration database is empty.
        """
        return self.measurements[0]

    @property
    def largest_load_measurement(self):
        """Return measurement with largest load.

        One-liner just so MeasurementDatabase does not assume a list.

        :returns: Measurement in this with largest target_tr.
        :rtype: ReceiveRateMeasurement
        :raises IndexError: If per duration database is empty.
        """
        return self.measurements[-1]
