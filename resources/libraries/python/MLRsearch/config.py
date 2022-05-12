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
from typing import List, Union


@dataclass
class Config:
    """Structure containing several static config items.

    The main MLRsearch algorithm uses multiple customizable values.
    Pylint complains if the values appear as long argument lists
    or multiple local variables.

    This class offers a storage for values which do not contain
    internally mutable state and are set at an unknown time
    before the search starts. This way users can override only some values,
    and do it over multiple calls.

    Properties are defined to enforce the requirements on allowed values.
    All fields have default values, so instances can be created without any.
    It is still recommended to set all values after instantiation,
    as the defaults may change in next version.
    """

    min_load: float = 1e0
    """Minimal target transmit rate available for the current search [tps]."""
    max_load: float = 1e7
    """Maximal target transmit rate available for the current search [tps]."""
    _target_loss_ratios: List[float] = field(default_factory=lambda: [0.0])
    """Packet loss ratios. Has to be non-empty and strictly increasing.
    Each ratio has to be non-negative and smaller than one."""
    initial_trial_duration: float = 1.0
    """Trial duration for the initial phase and also
    for the first intermediate phase [s]."""
    final_trial_duration: float = 60.0
    """Trial duration for the final phase [s]."""
    _final_relative_widths: Union[float, List[float]] = 0.005
    # TODO: ^ Plural? Maybe with two setters, one for float one for list?
    """Final lower bound offered load cannot be more distant
    than this multiple of upper bound.
    Besides a single width value (common for all ratios),
    a list of values (one for each ratio) is also supported."""
    number_of_intermediate_phases: int = 2
    """Number of intermediate phases to perform before the final phase."""
    expansion_coefficient: float = 4.0
    """External search multiplies width (in logarithmic space) by this."""
    max_search_duration: float = 1800.0
    """The search will end as a failure this long [s] after it is started."""

    # TODO: Is this needed? If yes, do we need setters?
    def __post_init__(self) -> None:
        """Convert inputs and apply checks."""
        self.min_load = float(self.min_load)
        if self.min_load <= 0.0:
            raise RuntimeError(f"Min load {self.min_load} must be positive.")
        self.max_load = float(self.max_load)
        if self.max_load <= self.min_load:
            raise RuntimeError(f"Max load {self.max_load} must be bigger.")
        # Ratios and widths are converted and checked in setters.
        self.initial_trial_duration = float(self.initial_trial_duration)
        if self.initial_trial_duration <= 0.0:
            raise RuntimeError(u"initial_trial_duration not positive.")
        self.final_trial_duration = float(self.final_trial_duration)
        if self.final_trial_duration <= self.initial_trial_duration:
            raise RuntimeError(u"initial_trial_duration must be bigger.")
        self.number_of_intermediate_phases = int(
            self.number_of_intermediate_phases
        )
        if self.number_of_intermediate_phases < 1:
            raise RuntimeError(u"number_of_intermediate_phases must be bigger.")
        self.expansion_coefficient = float(self.expansion_coefficient)
        if self.expansion_coefficient <= 1.0:
            raise RuntimeError(u"expansion_coefficient must be bigger.")
        self.max_search_duration = float(self.max_search_duration)
        if self.max_search_duration <= 0.0:
            raise RuntimeError(u"max_search_duration must be positive.")

    @property
    def target_loss_ratios(self) -> List[float]:
        """Return a copy of the current list.

        :returns: The current list of loss ratios.
        :rtype: List[float]
        """
        return list(self._target_loss_ratios)

    @target_loss_ratios.setter
    def target_loss_ratios(self, target_loss_ratios: List[float]) -> None:
        """Copy, convert, check and store the argument list values.

        :param target_loss_ratios: List of ratios for the current search.
        :type target_loss_ratios: Iterable[float]
        :raises RuntimeError: If there is no ratio or the ratios are not sorted.
        """
        ratios = list()
        for ratio in target_loss_ratios:
            ratio = float(ratio)
            if ratio < 0.0:
                raise RuntimeError(f"Ratio {ratio} cannot be negative.")
            if ratio >= 1.0:
                raise RuntimeError(f"Ratio {ratio} must be lower than 1.")
            ratios.append(ratio)
        if len(ratios) < 1:
            raise RuntimeError(u"At least one ratio is required!")
        if ratios != sorted(set(ratios)):
            raise RuntimeError(u"Input ratios have to be sorted and unique!")
        self._target_loss_ratios = ratios

    @property
    def final_relative_width(self) -> List[float]:
        """Return a copy of the list if its length is expected.

        If a float value was stored, contruct list of correct length.

        :returns: Width goals, one for each ratio.
        :rtype: List[float]
        :raises RuntimeError: If stored list does not match number of ratios.
        """
        if isinstance(self._final_relative_widths, float):
            widths = [self._final_relative_widths]
            widths *= len(self._target_loss_ratios)
            return widths
        if len(self._final_relative_widths) != len(self._target_loss_ratios):
            raise RuntimeError(u"Width length does not match ratios.")
        return list(self._final_relative_widths)

    @final_relative_width.setter
    def final_relative_width(self, widths: Union[float, List[float]]) -> None:
        """Check type and store the value.

        :param widths: Single or multiple values to set.
        :type widths: Union[float, List[float]]
        :raises RuntimeError: If argument is not of expected fype.
        """
        if isinstance(widths, float):
            self._final_relative_widths = widths
            return
        if isinstance(widths, list):
            self._final_relative_widths = map(float, widths)
            return
        raise RuntimeError(f"Unexpected widths: {widths!r}")
