# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Module defining NdrPdrResult class."""

from .ReceiveRateInterval import ReceiveRateInterval


class NdrPdrResult:
    """Two measurement intervals, return value of search algorithms.

    Partial fraction is NOT part of the result. Pdr interval should be valid
    for all partial fractions implied by the interval."""

    def __init__(self, ndr_interval, pdr_interval):
        """Store the measured intervals after checking argument types.

        :param ndr_interval: Object containing data for NDR part of the result.
        :param pdr_interval: Object containing data for PDR part of the result.
        :type ndr_interval: ReceiveRateInterval.ReceiveRateInterval
        :type pdr_interval: ReceiveRateInterval.ReceiveRateInterval
        """
        # TODO: Type checking is not very pythonic,
        # perhaps users can fix wrong usage without it?
        if not isinstance(ndr_interval, ReceiveRateInterval):
            raise TypeError(
                f"ndr_interval, is not a ReceiveRateInterval: {ndr_interval!r}"
            )
        if not isinstance(pdr_interval, ReceiveRateInterval):
            raise TypeError(
                f"pdr_interval, is not a ReceiveRateInterval: {pdr_interval!r}"
            )
        self.ndr_interval = ndr_interval
        self.pdr_interval = pdr_interval

    def width_in_goals(self, relative_width_goal):
        """Return a debug string related to current widths in logarithmic scale.

        :param relative_width_goal: Upper bound times this is the goal
            difference between upper bound and lower bound.
        :type relative_width_goal: float
        :returns: Message containing NDR and PDR widths in goals.
        :rtype: str
        """
        return f"ndr {self.ndr_interval.width_in_goals(relative_width_goal)};" \
            f" pdr {self.pdr_interval.width_in_goals(relative_width_goal)}"

    def __str__(self):
        """Return string as tuple of named values."""
        return f"NDR={self.ndr_interval!s};PDR={self.pdr_interval!s}"

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return f"NdrPdrResult(ndr_interval={self.ndr_interval!r}," \
            f"pdr_interval={self.pdr_interval!r})"
