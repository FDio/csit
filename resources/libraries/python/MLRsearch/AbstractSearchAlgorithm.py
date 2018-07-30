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

    def __init__(self, measurer):
        """Store the rate provider.

        :param measurer: Object able to perform trial or composite measurements.
        :type measurer: AbstractMeasurer.AbstractMeasurer
        """
        # TODO: Type check for AbstractMeasurer?
        self.measurer = measurer

    @abstractmethod
    def narrow_down_ndr_and_pdr(
            self, fail_rate, line_rate, packet_loss_ratio):
        """Perform measurements to narrow down intervals, return them.

        This will be renamed when custom loss ratio lists are supported.

        :param fail_rate: Minimal target transmit rate [pps].
        :param line_rate: Maximal target transmit rate [pps].
        :param packet_loss_ratio: Fraction of packets lost, for PDR [1].
        :type fail_rate: float
        :type line_rate: float
        :type packet_loss_ratio: float
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :rtype: NdrPdrResult.NdrPdrResult
        """
        # TODO: Do we agree on arguments related to precision or trial duration?
        pass
