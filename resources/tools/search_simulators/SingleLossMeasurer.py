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

from random import random

from resources.libraries.python.MLRsearch.AbstractMeasurer import AbstractMeasurer
from resources.libraries.python.MLRsearch.ReceiveRateMeasurement import ReceiveRateMeasurement


class SingleLossMeasurer(AbstractMeasurer):
    """Random Dx generator. percentage for Dx=0, Dx=1 otherwise."""

    def __init__(self, loss_probability=0.5):
        """Store loss probability."""
        self.loss_probability = loss_probability

    def measure(self, duration, transmit_rate):
        """Random generate Dx."""
        tx = duration * transmit_rate
        dx = 1 if random() < self.loss_probability else 0
        return ReceiveRateMeasurement(duration, transmit_rate, tx, dx)
