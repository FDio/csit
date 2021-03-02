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

"""Module defining PerDurationDatabase class."""

class PerDurationDatabase:
    """Dict-like structure holding measurement results for one duration.

    This is a building block for MeasurementDatabase.

    This class hold measurements for single target duration value only,
    so the logic is quite simple.

    Several utility methods are added, accomplishing tasks useful for MLRsearch
    (to be called by MeasurementDatabade).
    """

    def __init__(self, duration, measurements):
        """Store (copy of) measurement results and normalize them.

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
        self.measurements = [measurement.copy() for measurement in measurements]
        self._normalize()

    def __repr__(self):
        """Return string executable to get equivalent instance.

        :returns: Code to construct equivalent instance.
        :rtype: str
        """
        return f"MeasurementDatabase(measurements={self.measurements!r})"

    def _normalize(self):
        """Sort by target_tr, fail on detecting duplicate target_tr.

        Also set effective loss ratios.
        """
        measurements = self.measurements
        measurements.sort(key=lambda measurement: measurement.target_tr)
        # Detect duplicated TRs.
        previous_tr = None
        for measurement in measurements:
            current_tr = measurement.target_tr
            if current_tr == previous_tr:
                raise ValueError(
                    u"Transmit rate conflict:"
                    f" {measurement!r} {previous_tr!r}"
                )
            previous_tr = current_tr
        # Update effective ratios.
        ratio_previous = None
        for measurement in measurements:
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
        self.measurements.append(measurement)
        self._normalize()

    def get_valid_lower_bound(self, ratio, min_tr=None, max_tr=None):
        """Return None or a valid lower bound measurement.

        Measurement candidates has to have target_tr between min_tr and max_tr
        (if that value is not None).

        :param ratio: Target ratio, valid has to be lower or equal.
        :param min_tr: Candidate measurements must have target_tr larger. [tps]
        :param max_tr: Candidate measurements must have target_tr smaller. [tps]
        :type ratio: float
        :type min_tr: Optional[float]
        :type max_tr: Optional[float]
        :returns: Whether database has measurement good for valid lower bound.
        :rtype: ReceiveRateMeasurement
        """
        bound = None
        for measurement in self.measurements:
            measurement_tr = measurement.target_tr
            if min_tr is not None and measurement_tr <= min_tr:
                continue
            if max_tr is not None and measurement_tr >= max_tr:
                # Measurements are sorted, so no point searching further.
                break
            if measurement.effective_loss_ratio > ratio:
                # Effective loss ratios increase, so we can break.
                break
            bound = measurement
            # Continuing to find a tighter bound.
        return bound

    def get_valid_upper_bound(self, ratio, min_tr=None, max_tr=None):
        """Return None or a valid upper bound measurement.

        Measurement candidates has to have target_tr between min_tr and max_tr
        (if that value is not None).

        :param ratio: Target ratio, valid has to be lower or equal.
        :param min_tr: Candidate measurements must have target_tr larger. [tps]
        :param max_tr: Candidate measurements must have target_tr smaller. [tps]
        :type ratio: float
        :type min_tr: Optional[float]
        :type max_tr: Optional[float]
        :returns: Whether database has measurement good for valid lower bound.
        :rtype: ReceiveRateMeasurement
        """
        bound = None
        for measurement in reversed(self.measurements):
            measurement_tr = measurement.target_tr
            if max_tr is not None and measurement_tr >= max_tr:
                continue
            if min_tr is not None and measurement_tr <= min_tr:
                # Measurements are sorted, so no point searching further.
                break
            if measurement.effective_loss_ratio <= ratio:
                # Effective loss ratios are sorted, so we can break.
                break
            bound = measurement
            # Continuing to find a tighter bound.
        return bound
