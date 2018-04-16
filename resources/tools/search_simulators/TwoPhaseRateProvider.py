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

import random

from resources.libraries.python.search.AbstractRateProvider import AbstractRateProvider
from resources.libraries.python.search.ReceiveRateMeasurement import ReceiveRateMeasurement


class TwoPhaseRateProvider(AbstractRateProvider):
    """Report Dx as sum of two phases, each of random Rr.

    Rr does NOT increase with Tr nor decrease with duration."""

    def __init__(self, first_phase_duration=0.002, first_rr_lo=1950000.0, first_rr_hi=2100000.0,
                 second_rr_lo=2150000.0, second_rr_hi=2180000.0, shiftness=5.0, sensitivity=0.02):
        """Constructor, stores parameters to use."""
        self.first_phase_duration = first_phase_duration
        self.first_rr_lo = first_rr_lo
        self.first_rr_hi = first_rr_hi
        self.second_rr_lo = second_rr_lo
        self.second_rr_hi = second_rr_hi
        self.shiftness = shiftness
        self.sensitivity = sensitivity

    def measure(self, duration, transmit_rate):
        """Compute Dx according to two phase model.

        TODO: Document the model in more detail."""
        first_phase_duration = min(duration, self.first_phase_duration)
        first_phase_tx = int(first_phase_duration * transmit_rate)
        first_phase_rr = random.uniform(self.first_rr_lo, self.first_rr_hi)
        first_phase_rx = int(first_phase_duration * first_phase_rr)
        first_phase_dx = max(0, first_phase_tx - first_phase_rx)
        if first_phase_duration >= duration:
            return ReceiveRateMeasurement(first_phase_duration, transmit_rate, first_phase_tx, first_phase_dx)
        second_phase_duration = duration - first_phase_duration
        second_phase_tx = int(second_phase_duration * transmit_rate)
        second_rr_lo, second_rr_hi = self.second_rr_lo, self.second_rr_hi
        if transmit_rate > second_rr_lo:
            second_rr_range = second_rr_hi - second_rr_lo
            overload_coeff = transmit_rate / second_rr_range * self.sensitivity
            shift_coeff = overload_coeff / (1.0 + overload_coeff)
            shift = shift_coeff * second_rr_range
            second_rr_lo += shift * self.shiftness / 2
            second_rr_hi += shift * self.shiftness
        second_phase_luck = random.betavariate(4, 4)
        second_phase_rr = second_rr_lo + second_phase_luck * (second_rr_hi - second_rr_lo)
        second_phase_rx = int(second_phase_duration * second_phase_rr)
        second_phase_dx = max(0, second_phase_tx - second_phase_rx)
        return ReceiveRateMeasurement(first_phase_duration + second_phase_duration, transmit_rate,
                                      first_phase_tx + second_phase_tx, first_phase_dx + second_phase_dx)
