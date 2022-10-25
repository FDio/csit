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

from .criteria import Criteria
from .criterion import Criterion
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

    For example, final_trial_count has to be set to equal
    initial_trial_count, before number_of_intermediate_phases can be set
    to zero.
    """

    # Externally visible "fields" (but in fact redefined as properties).
    criteria: Criteria = Criteria((Criterion(),))
    """FIXME"""
    min_load: float = 1e0
    """Each trial measurement must have intended load at least this [tps]."""
    max_load: float = 1e9
    """Each trial measurement must have intended load at most this [tps]."""
    min_trial_duration: float = 1.0
    """FIXME"""
    single_trial_duration: float = 1.0
    """FIXME"""
    max_search_duration: float = 1800.0
    """The search will end as a failure this long [s] after it is started."""
    warmup_duration: float = 0.0
    """FIXME"""
    # Internal private fields holding the values for properties to access.
    _criteria: Criteria = field(init=False, repr=False)
    _min_load: float = field(init=False, repr=False)
    _max_load: float = field(init=False, repr=False)
    _min_trial_duration: float = field(init=False, repr=False)
    _single_trial_duration: float = field(init=False, repr=False)
    _initial_trial_count: int = field(init=False, repr=False)
    _max_search_duration: float = field(init=False, repr=False)
    _warmup_duration: float = field(init=False, repr=False)

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
        :raises ValueError: If the argument is found invalid.
        """
        load = float(load)
        if load <= 0.0:
            raise ValueError(f"Min load {load} must be positive.")
        # At the time init is first called, _max_load is not set yet.
        if hasattr(self, "_max_load") and load >= self.max_load:
            raise ValueError(f"Min load {load} must be smaller.")
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
        :raises ValueError: If the argument is found invalid.
        """
        load = float(load)
        if load <= self.min_load:
            raise ValueError(f"Max load {load} must be bigger.")
        self._max_load = load

    @dataclass_property
    def min_trial_duration(self) -> float:
        """Getter for max search duration, no logic here.

        :returns: Currently set max search duration [s].
        :rtype: float
        """
        return self._min_trial_duration

    @min_trial_duration.setter
    def min_trial_duration(self, duration: float) -> None:
        """Set max search duration after converting and checking value.

        :param duration: Max search duration [s] value to set.
        :type duration: float
        :raises ValueError: If the argument is found invalid.
        """
        duration = float(duration)
        if duration <= 0.0:
            raise ValueError(f"Min trial duration too small: {duration}")
        if (
            hasattr(self, "_single_trial_duration")
            and duration > self.single_trial_duration
        ):
            raise ValueError(f"Min trial duration {duration} must be smaller.")
        self._min_trial_duration = duration

    @dataclass_property
    def single_trial_duration(self) -> float:
        """Getter for max search duration, no logic here.

        :returns: Currently set max search duration [s].
        :rtype: float
        """
        return self._single_trial_duration

    @single_trial_duration.setter
    def single_trial_duration(self, duration: float) -> None:
        """Set max search duration after converting and checking value.

        :param duration: Max search duration [s]ue to set.
        :type duration: float
        :raises ValueError: If the argument is found invalid.
        """
        duration = float(duration)
        if duration < self.min_trial_duration:
            raise ValueError(f"Single trial duration too small: {duration}")
        self._single_trial_duration = duration

    @dataclass_property
    def criteria(self) -> Criteria:
        """Return a copy of the current list.

        :returns: The current list of loss ratios.
        :rtype: List[float]
        """
        return self._criteria

    @criteria.setter
    def criteria(self, criteria: Criteria) -> None:
        """Copy, convert, check and store the argument list values.

        :param loss_ratios: List of ratios for the current search.
        :type loss_ratios: Iterable[float]
        :raises TypeError: If there is some problem with the argument.
        """
        if not isinstance(criteria, Criteria):
            raise TypeError(f"Must by Criteria instance: {criteria}")
        if len(criteria.loss_ratios) < 1:
            raise ValueError(f"At least one criterion needed: {criteria}")
        self._criteria = criteria

    @dataclass_property
    def max_search_duration(self) -> float:
        """Getter for max search duration, no logic here.

        :returns: Currently set max search duration [s].
        :rtype: float
        """
        return self._max_search_duration

    @max_search_duration.setter
    def max_search_duration(self, duration: float) -> None:
        """Set max search duration after converting and checking value.

        :param duration: Max search duration [s]ue to set.
        :type duration: float
        :raises ValueError: If the argument is found invalid.
        """
        duration = float(duration)
        if duration <= 0.0:
            raise ValueError(f"Max search duration too small: {duration}")
        self._max_search_duration = duration

    @dataclass_property
    def warmup_duration(self) -> float:
        """Getter for max search duration, no logic here.

        :returns: Currently set max search duration [s].
        :rtype: float
        """
        return self._warmup_duration

    @warmup_duration.setter
    def warmup_duration(self, duration: float) -> None:
        """Set max search duration after converting and checking value.

        :param duration: Max search duration [s]ue to set.
        :type duration: float
        :raises ValueError: If the argument is found invalid.
        """
        duration = float(duration)
        if duration < 0.0:
            raise ValueError(f"Warmup duration too small: {duration}")
        self._warmup_duration = duration
