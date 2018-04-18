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

from resources.libraries.python.search.AbstractSearchAlgorithm import AbstractSearchAlgorithm
from resources.libraries.python.search.NdrPdrResult import NdrPdrResult
from resources.libraries.python.search.ReceiveRateInterval import ReceiveRateInterval
from resources.libraries.python.search.ReceiveRateMeasurement import ReceiveRateMeasurement


class BasicBinarySearchAlgorithm(AbstractSearchAlgorithm):
    """Bisect untilinterval width is smaller than the goal;
    separately for both NDR and PDR.
    No fast fail, nor other smart stuff."""

    def __init__(self, rate_provider, duration, width):
        """Store rate provider and additional parameters."""
        super(BasicBinarySearchAlgorithm, self).__init__(rate_provider)
        self.width = width
        """Upper and lower bounds (target transmit rates) need to be closer than this."""
        self.duration = duration
        """Each trial measurement will be performed at this duration."""

    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Perform boundary measurements, proceed with iteration-aware method."""
        line_measurement = self.rate_provider.measure(self.duration, line_rate)
        fail_measurement = self.rate_provider.measure(self.duration, fail_rate)
        ndr = self.bisect(fail_measurement, line_measurement, 0.0)
        pdr = self.bisect(fail_measurement, line_measurement, allowed_drop_fraction)
        return NdrPdrResult(ndr, pdr)

    def bisect(self, lower_measurement, upper_measurement, allowed_drop_fraction):
        """Bisect and recurse for PDR of given Df."""
        if upper_measurement.target_tr - lower_measurement.target_tr < self.width:
            return ReceiveRateInterval(lower_measurement, upper_measurement)
        middle_target_tr = (lower_measurement.target_tr + upper_measurement.target_tr) / 2.0
        middle_measurement = self.rate_provider.measure(self.duration, middle_target_tr)
        if middle_measurement.drop_fraction > allowed_drop_fraction:
            return self.bisect(lower_measurement, middle_measurement, allowed_drop_fraction)
        return self.bisect(middle_measurement, upper_measurement, allowed_drop_fraction)
