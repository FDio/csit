# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Module defining ReceiveRateInterval class."""

import math

from ReceiveRateMeasurement import ReceiveRateMeasurement


class ReceiveRateInterval(object):
    """Structure defining two Rr measurements, and their relation."""

    def __init__(self, measured_low, measured_high):
        """Store the bound measurements after checking argument types.

        :param measured_low: Measurement for the lower bound.
        :param measured_high: Measurement for the upper bound.
        :type measured_low: ReceiveRateMeasurement.ReceiveRateMeasurement
        :type measured_high: ReceiveRateMeasurement.ReceiveRateMeasurement
        """
        # TODO: Type checking is not very pythonic,
        # perhaps users can fix wrong usage without it?
        if not isinstance(measured_low, ReceiveRateMeasurement):
            raise TypeError("measured_low is not a ReceiveRateMeasurement: "
                            "{low!r}".format(low=measured_low))
        if not isinstance(measured_high, ReceiveRateMeasurement):
            raise TypeError("measured_high is not a ReceiveRateMeasurement: "
                            "{high!r}".format(high=measured_high))
        self.measured_low = measured_low
        self.measured_high = measured_high
        # Declare secondary quantities to appease pylint.
        self.abs_tr_width = None
        """Absolute width of target transmit rate. Upper minus lower."""
        self.rel_tr_width = None
        """Relative width of target transmit rate. Absolute divided by upper."""
        self.sort()

    def sort(self):
        """Sort bounds by target Tr, compute secondary quantities."""
        if self.measured_low.target_tr > self.measured_high.target_tr:
            self.measured_low, self.measured_high = (
                self.measured_high, self.measured_low)
        self.abs_tr_width = (
            self.measured_high.target_tr - self.measured_low.target_tr)
        self.rel_tr_width = self.abs_tr_width / self.measured_high.target_tr

    def width_in_goals(self, relative_width_goal):
        """Return float value.

        Relative width goal is some (negative) value on logarithmic scale.
        Current relative width is another logarithmic value.
        Return the latter divided by the former.
        This is useful when investigating how did surprising widths come to be.

        :param relative_width_goal: Upper bound times this is the goal
            difference between upper bound and lower bound.
        :type relative_width_goal: float
        :returns: Current width as logarithmic multiple of goal width [1].
        :rtype: float
        """
        return math.log(1.0 - self.rel_tr_width) / math.log(
            1.0 - relative_width_goal)

    def __str__(self):
        """Return string as half-open interval."""
        return "[{low!s};{high!s})".format(
            low=self.measured_low, high=self.measured_high)

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return ("ReceiveRateInterval(measured_low={low!r}"
                ",measured_high={high!r})".format(
                    low=self.measured_low, high=self.measured_high))
