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

from resources.libraries.python.search.AbstractRateProvider import AbstractRateProvider
from resources.libraries.python.search.ReceiveRateMeasurement import ReceiveRateMeasurement

class KeyboardRateProvider(AbstractRateProvider):
    """Report rate the user has typed."""

    def measure(self, duration, transmit_rate):
        """Print context and ask user for Dx."""
        tx = int(duration * transmit_rate)
        print "Tr", transmit_rate
        print "Tx", tx
        print "d", duration
        print "0.5%", tx / 200.0
        dx = input("Enter Dx:")
        return ReceiveRateMeasurement(duration, transmit_rate, tx, dx)
