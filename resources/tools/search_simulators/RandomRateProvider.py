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

from random import randint

from resources.libraries.python.search.AbstractRateProvider import AbstractRateProvider
from resources.libraries.python.serach.ReceiveRateMeasurement import ReceiveRateMeasurement


class RandomRateProvider(AbstractRateProvider):
    """Random Dx generator. 50-50 for Dx=0, uniform drop fraction otherwise."""

    def measure(self, duration, transmit_rate):
        """Random generate Dx."""
        tx = duration * transmit_rate
        dx = 0
        if randint(0, 1):
            dx = randint(0, int(tx))
        return ReceiveRateMeasurement(duration, transmit_rate, tx, dx)
