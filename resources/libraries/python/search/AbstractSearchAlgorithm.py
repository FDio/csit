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

"""Module defining AbstractSearchAlgorithm class."""

from abc import ABCMeta, abstractmethod


class AbstractSearchAlgorithm(object):
    """Abstract class defining common API for search algorithms."""

    __metaclass__ = ABCMeta

    def __init__(self, rate_provider):
        """Store the rate provider.

        :param rate_provider: Object able to perform trial measurements.
        :type rate_provider: AbstractRateProvider
        """
        # TODO: Type check for AbstractRateProvider?
        self.rate_provider = rate_provider

    @abstractmethod
    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate,
                                allowed_drop_fraction):
        """Perform measurements to narrow down intervals, return them.

        :param fail_rate: Minimal target transmit rate [pps].
        :param line_rate: Maximal target transmit rate [pps].
        :param allowed_drop_fraction: Fraction of dropped packets for PDR [1].
        :type fail_rate: float
        :type line_rate: float
        :type allowed_drop_fraction: float
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :rtype: NdrPdrResult
        """
        # TODO: Do we agree on arguments related to precision or trial duration?
        pass
