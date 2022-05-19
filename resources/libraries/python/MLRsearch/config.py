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

from dataclasses import dataclass, field, Field
from typing import Any, Callable, Iterable, List, Optional


private_field = field(init=False, repr=False)


def property_with_default(default: Any) -> Callable[[Callable[[Any], Any]], property]:
    """"""
    def closure(function: Callable[[Any], Any]) -> property:
        """"""
        function.default = default
        propertied = property(function)
        return propertied
    return closure


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

    As some requirements are between values of different fields,
    users must take care to set them in correct order.
    """

    _min_load: float = private_field
    """Minimal target transmit rate available for the current search [tps]."""
    min_load: float = 1e0
    """Constructor argument for the private field (guarded by setter) above."""
    _max_load: float = private_field
    """Maximal target transmit rate available for the current search [tps]."""
    max_load: float = 1e9
    """Constructor argument for the private field (guarded by setter) above."""
    _target_loss_ratios: List[float] = private_field
    """Packet loss ratios. Has to be non-empty and strictly increasing.
    Each ratio has to be non-negative and smaller than one."""
    target_loss_ratios: Iterable[float] = (0.0,)
    """Constructor argument for the private field (guarded by setter) above."""
    _initial_trial_duration: float = private_field
    """Trial duration for the initial phase and also
    for the first intermediate phase [s]."""
    initial_trial_duration: float = 1.0
    """Constructor argument for the private field (guarded by setter) above."""
    _final_trial_duration: float = private_field
    """Trial duration for the final phase [s]."""
    final_trial_duration: float = 60.0
    """Constructor argument for the private field (guarded by setter) above."""
    _final_relative_widths: List[float] = private_field
    """Final lower bound offered load cannot be more distant
    than this multiple of upper bound.
    If all the values are the same, length will match the number of ratios.
    Else a mismatch will lead to runtime errors."""
    final_relative_width: float = 0.005
    """Constructor argument for the private field (guarded by setter) above.
    This variant sets single width, making length of private list flexible."""
    final_relative_widths: Optional[Iterable[float]] = None
    """Constructor argument for the private field (guarded by setter) above.
    This variant sets multiple widths. If the values are not all the same,
    the length of the private list is no longer handles as flexible."""
    _number_of_intermediate_phases: int = private_field
    """Number of intermediate phases to perform before the final phase."""
    number_of_intermediate_phases: int = 2
    """Constructor argument for the private field (guarded by setter) above."""
    _expansion_coefficient: int = private_field
    """External search multiplies width (in logarithmic space) by this."""
    expansion_coefficient: int = 4
    """Constructor argument for the private field (guarded by setter) above."""
    _max_search_duration: float = private_field
    """The search will end as a failure this long [s] after it is started."""
    max_search_duration: float = 1800.0
    """Constructor argument for the private field (guarded by setter) above."""

    # TODO: Is this needed? If yes do we need setters to perform the checks too?
    def __post_init__(self) -> None:
        """Convert inputs and apply checks."""

    @property_with_default(min_load)
    def min_load(self) -> float:
        """Getter for min load, no logic here.

        :returns: Currently set minimal intended load [tps].
        :rtype: float
        """
        return self._min_load

    @min_load.setter
    def min_load(self, load: float) -> None:
        """Set min load after converting type and checking value.

        :param load: Minimal intended load [tps] to set.
        :type load: float
        :raises RuntimeError: If the argument is found invalid.
        """
        if isinstance(load, property):
            load = load.fget.default
        load = float(load)
        if load <= 0.0:
            raise RuntimeError(f"Min load {load} must be positive.")
        if not isinstance(self._max_load, Field) and load >= self._max_load:
            raise RuntimeError(f"Min load {load} must be smaller.")
        self._min_load = load

    @property_with_default(max_load)
    def max_load(self) -> float:
        """Getter for max load, no logic here.

        :returns: Currently set maximal intended load [tps].
        :rtype: float
        """
        return self._max_load

    @max_load.setter
    def max_load(self, load: float) -> None:
        """Set max load after converting type and checking value.

        :param load: Minimal intended load [tps] to set.
        :type load: float
        :raises RuntimeError: If the argument is found invalid.
        """
        if isinstance(load, property):
            load = load.fget.default
        load = float(load)
        if load <= self.min_load:
            raise RuntimeError(f"Max load {load} must be bigger.")
        self._max_load = load

    @property_with_default(target_loss_ratios)
    def target_loss_ratios(self) -> List[float]:
        """Return a copy of the current list.

        :returns: The current list of loss ratios.
        :rtype: List[float]
        """
        ret = list(self._target_loss_ratios)
        return ret

    @target_loss_ratios.setter
    def target_loss_ratios(self, loss_ratios: Iterable[float]) -> None:
        """Copy, convert, check and store the argument list values.

        :param loss_ratios: List of ratios for the current search.
        :type loss_ratios: Iterable[float]
        :raises RuntimeError: If there is some problem with the argument.
        """
        if isinstance(loss_ratios, property):
            loss_ratios = loss_ratios.fget.default
        ratios = list()
        for ratio in loss_ratios:
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

    @property_with_default(initial_trial_duration)
    def initial_trial_duration(self) -> float:
        """Getter for initial trial duration, no logic here.

        :returns: Currently set trial duration [s] for initial phase.
        :rtype: float
        """
        return self._initial_trial_duration

    @initial_trial_duration.setter
    def initial_trial_duration(self, duration: float) -> None:
        """Set initial trial duration after converting type and checking value.

        :param duration: Trial duration [s] for initial phase to set.
        :type duration: float
        :raises RuntimeError: If the argument is found invalid.
        """
        if isinstance(duration, property):
            duration = duration.fget.default
        duration = float(duration)
        if duration <= 0.0:
            raise RuntimeError(f"Initial duration {duration} must be bigger.")
        if not isinstance(self._final_trial_duration, Field):
            if duration >= self._final_trial_duration:
                raise RuntimeError(f"Initial duration {duration} must be smaller.")
        self._initial_trial_duration = duration

    @property_with_default(final_trial_duration)
    def final_trial_duration(self) -> float:
        """Getter for final trial duration, no logic here.

        :returns: Currently set trial duration [s] for the final phase.
        :rtype: float
        """
        return self._final_trial_duration

    @final_trial_duration.setter
    def final_trial_duration(self, duration: float) -> None:
        """Set final trial duration after converting type and checking value.

        :param duration: Trial duration [s] for final phase to set.
        :type duration: float
        :raises RuntimeError: If the argument is found invalid.
        """
        if isinstance(duration, property):
            duration = duration.fget.default
        duration = float(duration)
        if duration <= self._initial_trial_duration:
            raise RuntimeError(f"Final duration {duration} must be bigger.")
        self._final_trial_duration = duration

    @property_with_default(final_relative_width)
    def final_relative_width(self) -> float:
        """Return the stored scalar value, raise if non-constant list is stored.

        :returns: Single width goal, to be applied for all ratios.
        :rtype: float
        :raises RuntimeError: If stored value is a list already.
        """
        value = self._final_relative_widths[0]
        for other in self._final_relative_widths[1:]:
            if other != value:
                raise RuntimeError(u"Width lengths are set and non-constant.")
        return value

    @final_relative_width.setter
    def final_relative_width(self, width: float) -> None:
        """Check type and store the singular value.

        This overwrites any previously stored value, even if it was a list.

        :param width: Single value to set.
        :type width: float
        :raises RuntimeError: If argument is found invalid.
        """
        if isinstance(width, property):
            width = width.fget.default
        width = float(width)  # Happens to support DiscreteWidth.
        if width <= 0.0:
            raise RuntimeError(f"Width must be positive: {width}")
        if width >= 1.0:
            raise RuntimeError(f"Width must be less than 1: {width}")
        # No need to use length of ratios, plural getter does that.
        self._final_relative_widths = [width]

    @property_with_default(final_relative_widths)
    def final_relative_widths(self) -> List[float]:
        """Return a copy of the list if its length is compatible.

        If the list is constant, length will be presented as compatible.
        Otherwise, length of the stored list has to match length of ratios.

        :returns: Width goals, one for each ratio.
        :rtype: List[float]
        :raises RuntimeError: If stored list does not match number of ratios.
        """
        value = self._final_relative_widths[0]
        for other in self._final_relative_widths[1:]:
            if other != value:
                break
        else:
            ret = [value] * len(self._target_loss_ratios)
            return ret
        if len(self._final_relative_widths) != len(self._target_loss_ratios):
            raise RuntimeError(u"Width length does not match ratios.")
        ret = list(self._final_relative_widths)
        return ret

    @final_relative_widths.setter
    def final_relative_widths(self, widths: Optional[Iterable[float]]) -> None:
        """Copy the values (checking them).

        None or empty iterable means no action,
        as it is assumed the singular setter already did set the default.

        :param widths: Multiple width values to set, cannot be empty.
        :type widths: Iterable[float]
        :raises RuntimeError: If argument is found invalid.
        """
        if isinstance(widths, property):
            widths = widths.fget.default
        if not widths:
            return
        for width in (widths := map(float, widths)):
            if width <= 0.0:
                raise RuntimeError(f"Width must be positive: {width}")
            if width >= 1.0:
                raise RuntimeError(f"Width must be less than 1: {width}")
        # We could check for constantness, but no real need to bother.
        self._final_relative_widths = widths

    @property_with_default(number_of_intermediate_phases)
    def number_of_intermediate_phases(self) -> int:
        """Getter for number of intermetiate phases, no logic here.

        :returns: Currently set number of intermetiate phases.
        :rtype: int
        """
        return self._number_of_intermediate_phases

    @number_of_intermediate_phases.setter
    def number_of_intermediate_phases(self, number: int) -> None:
        """Set number of phases after checking type and value.

        :param number: Number of intermediate phases to set.
        :type number: int
        :raises RuntimeError: If the argument is found invalid.
        """
        if isinstance(number, property):
            number = number.fget.default
        if not isinstance(number, int):
            raise RuntimeError(u"Number of phases must be an integer.")
        if number < 1:
            raise RuntimeError(u"Number of intermediate phases must be bigger.")
        self._number_of_intermediate_phases = number

    @property_with_default(expansion_coefficient)
    def expansion_coefficient(self) -> int:
        """Getter for expansion coefficient, no logic here.

        :returns: Currently set expansion coefficient value.
        :rtype: int
        """
        return self._expansion_coefficient

    @expansion_coefficient.setter
    def expansion_coefficient(self, coefficient: int) -> None:
        """Set expansion coefficient after checking type and value.

        :param coefficient: Expansion coefficient value to set.
        :type coefficient: int
        :raises RuntimeError: If the argument is found invalid.
        """
        if isinstance(coefficient, property):
            coefficient = coefficient.fget.default
        if not isinstance(coefficient, int):
            raise RuntimeError(u"Expansion coefficient must be an integer.")
        if coefficient < 1:
            raise RuntimeError(u"Expansion coefficient must be bigger.")
        self._expansion_coefficient = coefficient

    @property_with_default(max_search_duration)
    def max_search_duration(self) -> float:
        """Getter for max search duration, no logic here.

        :returns: Currently set max search duration [s].
        :rtype: float
        """
        return self._max_search_duration

    @max_search_duration.setter
    def max_search_duration(self, duration: int) -> None:
        """Set max search duration after converting and checking value.

        :param duration: Max search duration [s]ue to set.
        :type duration: float
        :raises RuntimeError: If the argument is found invalid.
        """
        if isinstance(duration, property):
            duration = duration.fget.default
        duration = float(duration)
        if duration <= 0.0:
            raise RuntimeError(u"Max search duration must be bigger.")
        self._max_search_duration = duration
