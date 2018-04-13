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

from ReceiveRateInterval import ReceiveRateInterval


class NdrPdrResult(object):
    """Two measurement intervals, return value of search algorithms.

    Partial fraction is NOT part of the result. Pdr interval should be valid
    for all partial fractions implied by the interval."""

    def __init__(self, ndr_interval, pdr_interval):
        """Constructor, store the measurement after checking argument types."""
        # TODO: Type checking is not very pythonic, perhaps users can fix wrong usage without it?
        if not isinstance(ndr_interval, ReceiveRateInterval):
            raise TypeError("ndr_interval, is not a ReceiveRateInterval: " + repr(ndr_interval))
        if not isinstance(pdr_interval, ReceiveRateInterval):
            raise TypeError("pdr_interval, is not a ReceiveRateInterval: " + repr(pdr_interval))
        self.ndr_interval = ndr_interval
        self.pdr_interval = pdr_interval

    def width_in_goals(self, relative_width_goal):
        """Return a debug string related to widths in logarithmic scale."""
        return (  "ndr " + str(self.ndr_interval.width_in_goals(relative_width_goal))
                + "; pdr " + str(self.pdr_interval.width_in_goals(relative_width_goal)))

    def __str__(self):
        """Return string as tuple of named values."""
        return "NDR=" + str(self.ndr_interval) + ";PDR=" + str(self.pdr_interval)

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "NdrPdrResult(ndr_interval=" + repr(self.ndr_interval) + \
               ",pdr_interval=" + repr(self.pdr_interval) + ")"
