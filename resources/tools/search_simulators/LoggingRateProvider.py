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

from resources.libraries.python.search.AbstractRateProvider import AbstractRateProvider


class LoggingRateProvider(AbstractRateProvider):
    """Delegating provider, logs relevant values at info level."""

    def __init__(self, provider):
        """Inject (non-printing) provider to delegate to."""
        self.provider = provider

    def measure(self, duration, transmit_rate):
        """Log context, delegate, log and return the measurement."""
        logging.info("Provider called with Tr %s and d %s", transmit_rate, duration)
        measurement = self.provider.measure(duration, transmit_rate)
        logging.info("Provider returned measurement: %s", measurement)
        return measurement
