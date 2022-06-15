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

"""Module defining AbstractMeasurer class."""

from abc import ABCMeta, abstractmethod

from .measurement_result import MeasurementResult as Result


class AbstractMeasurer(metaclass=ABCMeta):
    """Abstract class defining common API for measurement providers.

    The original use of this class was in the realm of
    RFC 2544 Throughput search, which explains the teminology
    related to networks, frames, packets, offered load, forwarding rate
    and similar.

    But the same logic can be used in higher level networking scenarios
    (e.g. https requests) or even outside networking (database transactions).

    The current code uses language from packet forwarding,
    docstring sometimes mention transactions as an alternative view.
    """

    @abstractmethod
    def measure(self, intended_duration: float, intended_load: float) -> Result:
        """Perform trial measurement and return the result.

        It is assumed the measurer got already configured with anything else
        needed to perform the measurement (e.g. traffic profile
        of transaction limit).

        Duration and load are the only values expected to vary
        during the search.

        :param intended_duration: Intended trial duration [s].
        :param intended_load: Intended rate of transactions (packets) [tps].
        :type intended_duration: float
        :type intended_load: float
        :returns: Structure detailing the result of the measurement.
        :rtype: measurement_result.MeasurementResult
        """
