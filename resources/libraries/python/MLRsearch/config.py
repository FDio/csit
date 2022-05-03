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

"""Module defining Config class."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Structure containing numerous static config items.

    The main MLRsearch algorithm uses multiple customizable values.
    Pylint complains if the values appear as long argument lists
    or multiple local variables.

    This class offers a storage for values which do not contain
    internally mutable state and are known at an unknown time
    before the search starts. This way users can override only some values,
    and do it over multiple lines.

    One property is defined to enforce the requirements on allowed values.
    All fields have default values, so instances can be created without any.
    It is still recommended to set all values after instantiation,
    as the defaults may change in next version.
    """

    min_rate: float = 1e0
    """Minimal target transmit rate available for the current search [tps]."""
    max_rate: float = 1e7
    """Maximal target transmit rate available for the current search [tps]."""
    _target_loss_ratios: List[float] = field(default_factory=lambda: [0.0])
    """Packet loss ratios. Has to be non-empty and strictly increasing."""
    initial_trial_duration: float = 1.0
    """Trial duration for the initial phase and also
    for the first intermediate phase [s]."""
    final_trial_duration: float = 60.0
    """Trial duration for the final phase [s]."""
    final_relative_width: float = 0.005
    """Final lower bound transmit rate cannot be more distant
    than this multiple of upper bound."""
    number_of_intermediate_phases: int = 2
    """Number of intermediate phases to perform before the final phase."""
    expansion_coefficient: float = 4.0
    """External search multiplies width (in logarithmic space) by this."""
    max_search_duration: float = 1800.0
    """The search will end as a failure this long [s] after it is started."""

    @property
    def target_loss_ratios(self):
        """Return a copy of the current list.

        :returns: The current list of loss ratios.
        :rtype: List[float]
        """
        return list(self._target_loss_ratios)

    @target_loss_ratios.setter
    def target_loss_ratios(self, target_loss_ratios):
        """Copy, convert, check and store the argument list values.

        :param target_loss_ratios: List of ratios for the current search.
        :type target_loss_ratios: Iterable[float]
        :raises RuntimeError: If there is no ratio or the ratios are not sorted.
        """
        ratios = [float(ratio) for ratio in target_loss_ratios]
        if len(ratios) < 1:
            raise RuntimeError(u"At least one ratio is required!")
        if ratios != sorted(set(ratios)):
            raise RuntimeError(u"Input ratios have to be sorted and unique!")
        self._target_loss_ratios = ratios
