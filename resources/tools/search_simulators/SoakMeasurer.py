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

import math
from random import random
from scipy.stats import poisson

from resources.libraries.python.MLRsearch.AbstractMeasurer import AbstractMeasurer
from resources.libraries.python.MLRsearch.ReceiveRateMeasurement import ReceiveRateMeasurement


class SoakMeasurer(AbstractMeasurer):
    """Random Dx generator, using Poisson distribution and integ-sigma function."""

    def __init__(self, mrr, overround):
        """Store parameters."""
        self.mrr = mrr
        self.overround = overround
        # TODO: Compute and log the critical load for the parameters.

    def measure(self, duration, transmit_rate):
        """Random generate Dx."""
        tx = int(duration * transmit_rate)
        # Two different formulas, to avoid overflows.
        if transmit_rate < self.mrr:
            avg = self.overround * math.log(1.0 + math.exp(
                (transmit_rate - self.mrr) / self.overround))
        else:
            avg = transmit_rate - self.mrr + self.overround * math.log(
                1.0 + math.exp((self.mrr - transmit_rate) / self.overround))
        dx = min(tx, poisson.rvs(avg * duration))
        return ReceiveRateMeasurement(duration, transmit_rate, tx, dx)
