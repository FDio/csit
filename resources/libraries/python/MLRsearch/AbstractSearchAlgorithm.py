# Copyright (c) 2021 Cisco and/or its affiliates.
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


class AbstractSearchAlgorithm(metaclass=ABCMeta):
    """Abstract class defining common API for search algorithms."""

    def __init__(self, measurer):
        """Store the rate provider.

        :param measurer: Object able to perform trial or composite measurements.
        :type measurer: AbstractMeasurer.AbstractMeasurer
        """
        self.measurer = measurer

    @abstractmethod
    def narrow_down_intervals(
            self, min_rate, max_rate, packet_loss_ratios):
        """Perform measurements to narrow down intervals, return them.

        :param min_rate: Minimal target transmit rate [tps].
            Usually, tests are set to fail if search reaches this or below.
        :param max_rate: Maximal target transmit rate [tps].
            Usually computed from line rate and various other limits,
            to prevent failures or duration stretching in Traffic Generator.
        :param packet_loss_ratios: Ratios of packet loss to search for,
            e.g. [0.0, 0.005] for NDR and PDR.
        :type min_rate: float
        :type max_rate: float
        :type packet_loss_ratios: Iterable[float]
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :rtype: List[ReceiveRateInterval.ReceiveRateInterval]
        """
