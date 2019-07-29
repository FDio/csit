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

import logging

from resources.libraries.python.MLRsearch.AbstractMeasurer import AbstractMeasurer


class LoggingMeasurer(AbstractMeasurer):
    """Delegating measurer, logs relevant values at info level."""

    def __init__(self, measurer):
        """Inject (non-printing) measurer to delegate to."""
        self.measurer = measurer

    def measure(self, duration, transmit_rate):
        """Log context, delegate, log and return the measurement."""
        logging.info("Provider called with Tr %s and d %s", transmit_rate, duration)
        measurement = self.measurer.measure(duration, transmit_rate)
        logging.info("Provider returned measurement: %s", measurement)
#        logging.info("that is %s packets lost", measurement.loss_count)
        return measurement
