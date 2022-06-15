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
from typing import Iterable, List, Optional

from .dataclass_property.dataclass_property import dataclass_property


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

    As some relations between values of different fields are required,
    users must take care to set them in the correct order.

    For example, final_trial_duration has to be set to equal
    initial_trial_duration, before number_of_intermediate_phases can be set
    to zero.
    """

    # Externally visible "fields" (but in fact redefined as properties).
    min_load: float = 1e0
    """Each trial measurement must have intended load at least this [tps]."""
    max_load: float = 1e9
    """Each trial measurement must have intended load at most this [tps]."""
    target_loss_ratios: Iterable[float] = (0.0,)
    """Packet loss ratio goals to find loads for.
    Has to be non-empty and strictly increasing.
    Each ratio has to be non-negative and smaller than one."""
    initial_trial_duration: float = 1.0
    """Trial duration [s] for the initial phase
    and also for the first intermediate phase."""
    final_trial_duration: float = 60.0
    """Trial duration for the final phase [s]."""
    final_relative_widths: Iterable[float] = (0.005,)
    """Final lower bound offered load cannot be more distant
    than this multiple of the final upper bound offered load.
    This variant sets multiple widths. Cannot be empty.
    If the values are all the same, the length effectively matches
    the length of target_loss_ratios."""
    final_relative_width: Optional[float] = None
    """A shorthand for the case when all final_relative_widths values
    are the same. If they are not, this getter returns None.
    If setter gets None, it does not change the previously stored value."""
    number_of_intermediate_phases: int = 2
    """Number of intermediate phases to perform before the final phase."""
    expansion_coefficient: int = 4
    """External search multiplies width (in logarithmic space) by this."""
    max_search_duration: float = 1800.0
    """The search will end as a failure this long [s] after it is started."""
    # Internal private fields holding the values for properties to access.
    _min_load: float = field(init=False, repr=False)
    _max_load: float = field(init=False, repr=False)
    _target_loss_ratios: List[float] = field(init=False, repr=False)
    _initial_trial_duration: float = field(init=False, repr=False)
    _final_trial_duration: float = field(init=False, repr=False)
    _final_relative_widths: List[float] = field(init=False, repr=False)
    # No _final_relative_width, length 1 list in _final_relative_widths instead.
    _number_of_intermediate_phases: int = field(init=False, repr=False)
    _expansion_coefficient: int = field(init=False, repr=False)
    _max_search_duration: float = field(init=False, repr=False)

    @dataclass_property
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
        load = float(load)
        if load <= 0.0:
            raise RuntimeError(f"Min load {load} must be positive.")
        # At the time init is first called, _max_load is not set yet.
        if hasattr(self, u"_max_load") and load >= self.max_load:
            raise RuntimeError(f"Min load {load} must be smaller.")
        self._min_load = load

    @dataclass_property
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
        load = float(load)
        if load <= self.min_load:
            raise RuntimeError(f"Max load {load} must be bigger.")
        self._max_load = load

    @dataclass_property
    def target_loss_ratios(self) -> List[float]:
        """Return a copy of the current list.

        :returns: The current list of loss ratios.
        :rtype: List[float]
        """
        return list(self._target_loss_ratios)

    @target_loss_ratios.setter
    def target_loss_ratios(self, loss_ratios: Iterable[float]) -> None:
        """Copy, convert, check and store the argument list values.

        :param loss_ratios: List of ratios for the current search.
        :type loss_ratios: Iterable[float]
        :raises RuntimeError: If there is some problem with the argument.
        """
        ratios = list()
        for ratio in map(float, loss_ratios):
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

    @dataclass_property
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
        duration = float(duration)
        if duration <= 0.0:
            raise RuntimeError(f"Initial duration {duration} must be bigger.")
        # At the time init is first called _final_trial_duration is not set yet.
        if hasattr(self, u"_final_trial_duration"):
            if duration > self.final_trial_duration:
                raise RuntimeError(f"Duration {duration} must be smaller.")
        self._initial_trial_duration = duration

    @dataclass_property
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
        duration = float(duration)
        if duration < self.initial_trial_duration:
            raise RuntimeError(f"Final duration {duration} must be bigger.")
        self._final_trial_duration = duration

    @dataclass_property
    def final_relative_widths(self) -> List[float]:
        """Return a copy of the list if its length is compatible.

        If the list is constant, length will be presented as compatible.
        Otherwise, length of the stored list has to match length of ratios.

        :returns: Width goals, one for each ratio.
        :rtype: List[float]
        :raises RuntimeError: If stored list does not match number of ratios.
        """
        widths = list(self._final_relative_widths)
        len_loss_ratios = len(self._target_loss_ratios)
        first_value, *other_values = widths
        for other in other_values:
            if other != first_value:
                break
        else:
            return [first_value] * len_loss_ratios
        if len(widths) != len_loss_ratios:
            raise RuntimeError(u"Width length does not match ratios.")
        return widths

    @final_relative_widths.setter
    def final_relative_widths(self, widths: Iterable[float]) -> None:
        """Copy the values (checking them).

        :param widths: Multiple width values to set, cannot be empty.
        :type widths: Iterable[float]
        :raises RuntimeError: If argument is found invalid (e.g. empty).
        """
        # The float happens to also add support for DiscreteWidth.
        widths = list(map(float, widths))
        if not widths:
            raise RuntimeError(u"Width list cannot be empty.")
        for width in widths:
            if width <= 0.0:
                raise RuntimeError(f"Width must be positive: {width}")
            if width >= 1.0:
                raise RuntimeError(f"Width must be less than 1: {width}")
        # We could check for constantness, but no real need to bother here.
        self._final_relative_widths = widths

    @dataclass_property
    def final_relative_width(self) -> Optional[float]:
        """Return the stored scalar value, None if non-constant list is stored.

        :returns: Single width goal, to be applied for all ratios.
        :rtype: Optional[float]
        """
        first_value, *other_values = self.final_relative_widths
        for other in other_values:
            if other != first_value:
                return None
        return first_value

    @final_relative_width.setter
    def final_relative_width(self, width: Optional[float]) -> None:
        """Check type and store the singular value.

        None means no change.

        Otherwise this overwrites any previously stored value
        with a one-element list.

        :param width: Single value to set.
        :type width: Optional[float]
        :raises RuntimeError: If argument is found invalid.
        """
        if width is None:
            return
        # The float() happens to also add support for DiscreteWidth.
        width = float(width)
        if width <= 0.0:
            raise RuntimeError(f"Width must be positive: {width}")
        if width >= 1.0:
            raise RuntimeError(f"Width must be less than 1: {width}")
        # No need to use length of ratios, plural getter does that.
        self._final_relative_widths = [width]

    @dataclass_property
    def number_of_intermediate_phases(self) -> int:
        """Getter for number of intermetiate phases, no logic here.

        :returns: Currently set number of intermetiate phases.
        :rtype: int
        """
        return self._number_of_intermediate_phases

    @number_of_intermediate_phases.setter
    def number_of_intermediate_phases(self, number: int) -> None:
        """Set number of phases after checking type and value.

        Ordinarily, there has to be at least one intermediate phase.
        The exception is if inital and final trial durations are the same,
        in which case there can be zero intermediate phases.

        :param number: Number of intermediate phases to set.
        :type number: int
        :raises RuntimeError: If the argument is found invalid.
        """
        if not isinstance(number, int):
            raise RuntimeError(u"Number of phases must be an integer.")
        too_small = False
        if number < 0:
            too_small = True
        elif number < 1:
            if self.initial_trial_duration != self.final_trial_duration:
                too_small = True
        if too_small:
            raise RuntimeError(u"Number of intermediate phases must be bigger.")
        self._number_of_intermediate_phases = number

    @dataclass_property
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
        if not isinstance(coefficient, int):
            raise RuntimeError(u"Expansion coefficient must be an integer.")
        if coefficient < 1:
            raise RuntimeError(u"Expansion coefficient must be bigger.")
        self._expansion_coefficient = coefficient

    @dataclass_property
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
        duration = float(duration)
        if duration <= 0.0:
            raise RuntimeError(u"Max search duration must be bigger.")
        self._max_search_duration = duration
