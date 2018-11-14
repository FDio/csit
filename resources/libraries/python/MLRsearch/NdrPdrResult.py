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

"""Module defining NdrPdrResult class."""

from ReceiveRateInterval import ReceiveRateInterval


class NdrPdrResult(object):
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
            raise TypeError("ndr_interval, is not a ReceiveRateInterval: "
                            "{ndr!r}".format(ndr=ndr_interval))
        if not isinstance(pdr_interval, ReceiveRateInterval):
            raise TypeError("pdr_interval, is not a ReceiveRateInterval: "
                            "{pdr!r}".format(pdr=pdr_interval))
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
        return "ndr {ndr_in_goals}; pdr {pdr_in_goals}".format(
            ndr_in_goals=self.ndr_interval.width_in_goals(relative_width_goal),
            pdr_in_goals=self.pdr_interval.width_in_goals(relative_width_goal))

    def __str__(self):
        """Return string as tuple of named values."""
        return "NDR={ndr!s};PDR={pdr!s}".format(
            ndr=self.ndr_interval, pdr=self.pdr_interval)

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "NdrPdrResult(ndr_interval={ndr!r},pdr_interval={pdr!r})".format(
            ndr=self.ndr_interval, pdr=self.pdr_interval)
