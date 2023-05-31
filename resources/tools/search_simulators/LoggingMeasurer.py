# Copyright (c) 2022 Cisco and/or its affiliates.
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

from resources.libraries.python.MLRsearch.trial_measurement.abstract_measurer import AbstractMeasurer


class LoggingMeasurer(AbstractMeasurer):
    """Delegating measurer, logs relevant values at info level."""

    def __init__(self, measurer):
        """Inject (non-printing) measurer to delegate to."""
        self.measurer = measurer

    def measure(self, intended_duration, intended_load):
        """Log context, delegate, log and return the measurement."""
#        logging.info(f"Provider called with Tr {intended_load} and d {intended_duration}")
        measurement = self.measurer.measure(
            intended_duration=intended_duration,
            intended_load=intended_load,
        )
#        logging.info(f"Provider returned measurement: {measurement}")
        return measurement
