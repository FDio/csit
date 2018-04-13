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

"""Abstract classes for NDRPDR search algorithms."""

from abc import ABCMeta, abstractmethod


class AbstractRateProvider(object):
    """Abstract class defining common API for rate providers."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def measure(self, duration, transmit_rate):
        """Perform trial measurement and return ReceiveRateMeasurement."""
        pass


class AbstractSearchAlgorithm(object):
    """Abstract class defining common API for search algorithms."""

    __metaclass__ = ABCMeta

    def __init__(self, rate_provider):
        """Constructor, needs injected rate provider."""
        # TODO: Type check for AbstractRateProvider?
        self.rate_provider = rate_provider

    @abstractmethod
    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Return NdrPdrResult object with the narrow measured data."""
        # TODO: Do we agree on arguments related to precision or trial duration?
        pass
