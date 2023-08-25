# Copyright (c) 2023 Cisco and/or its affiliates.
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

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .search_goal import SearchGoal
from .search_goal_set import SearchGoalSet
from .dataclass_property import DataclassProperty


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
    All "official" user inputs are contained here.

    Properties are defined to enforce the requirements on allowed values.
    All fields have default values, so instances can be created without any.
    It is still recommended to set all values after instantiation,
    as the defaults may change in next version.

    As some relations between values of different fields are required,
    users must take care to set them in the correct order.

    For example, min_load has to be set to a value smaller
    than the current value of max_load.
    """

    # Externally visible "fields" (but in fact redefined as properties).
    goals: SearchGoalSet = SearchGoalSet((SearchGoal(),))
    """Container holding search goals."""
    min_load: float = 1e0
    """Each trial measurement must have intended load at least this [tps]."""
    max_load: float = 1e9
    """Each trial measurement must have intended load at most this [tps]."""
    search_duration_max: float = 1800.0
    """The search will end as a failure this long [s] after it is started."""
    warmup_duration: Optional[float] = None
    """If specified, one trial at max load and this duration is performed
    before the usual search starts.
    The results of that one trial are ignored."""

    @DataclassProperty
    def goals(self) -> SearchGoalSet:
        """Return the reference to the current container.

        :returns: The current container instance.
        :rtype: SearchGoalSet
        """
        return self._goals

    @goals.setter
    def goals(self, goals: Iterable[SearchGoal]) -> None:
        """Create and store the goal container.

        :param goals: Search goals to add to the container to store.
        :type goals: Iterable[SearchGoal]
        :raises ValueError: If there are no goals.
        :raises TypeError: If a goal is not a SearchGoal.
        """
        self._goals = SearchGoalSet(goals)

    @DataclassProperty
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

    @DataclassProperty
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

    @DataclassProperty
    def search_duration_max(self) -> float:
        """Getter for max search duration, no logic here.

        :returns: Currently set max search duration [s].
        :rtype: float
        """
        return self._search_duration_max

    @search_duration_max.setter
    def search_duration_max(self, duration: float) -> None:
        """Set max search duration after converting and checking value.

        :param duration: Search duration maximum [s] to set.
        :type duration: float
        :raises ValueError: If the argument is found invalid.
        """
        duration = float(duration)
        if duration <= 0.0:
            raise ValueError(f"Search duration max too small: {duration}")
        self._search_duration_max = duration

    @DataclassProperty
    def warmup_duration(self) -> float:
        """Getter for warmup duration, no logic here.

        :returns: Currently set max search duration [s].
        :rtype: float
        """
        return self._warmup_duration

    @warmup_duration.setter
    def warmup_duration(self, duration: Optional[float]) -> None:
        """Set warmup duration after converting and checking value.

        Zero duration is treated as None, meaning no warmup trial.

        :param duration: Warmup duration [s] to set.
        :type duration: Optional(float)
        :raises ValueError: If the argument is found invalid.
        """
        if duration:
            duration = float(duration)
            if duration < 0.0:
                raise ValueError(f"Warmup duration too small: {duration}")
        else:
            duration = None
        self._warmup_duration = duration
