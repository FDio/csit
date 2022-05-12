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

"""Module defining MeasurementInterval class."""

from dataclasses import dataclass, field

from .comparable_measurement_result import ComparableMeasurementResult
from .width_arithmetics import width_in_goals


@dataclass
class MeasurementInterval:
    """Structure defining two measurements results, and their relation.

    The main purpose is in utilities calculating "distance" between
    the intended loads, a.k.a. interval width, in various quantities.
    """
    low_end: ComparableMeasurementResult
    """Measurement for the lower (or higher) load."""
    high_end: ComparableMeasurementResult
    """Measurement for the higher (or lower) load."""
    absolute_width: float = field(init=False, repr=False)
    """Absolute width of intended loads. Tps of high_end minus of low_end."""
    relative_width: float = field(init=False, repr=False)
    """Relative width of intended loads. Absolute divided by high_end tps."""

    def __post_init__(self):
        """Sort bounds by intended load, compute secondary quantities."""
        if self.low_end.intended_load > self.high_end.intended_load:
            self.low_end, self.high_end = self.high_end, self.low_end
        self.absolute_width = (
            self.high_end.intended_load - self.low_end.intended_load
        )
        self.relative_width = self.absolute_width / self.high_end.intended_load

    def width_in_goals(self, relative_width_goal: float) -> float:
        """Return relative width as a logaritmic multiple of given goal.

        Relative width goal is some (negative) value on logarithmic scale.
        Current relative width is another logarithmic value.
        Return the latter divided by the former.

        :param relative_width_goal: high_end bound times this is the goal
            difference between high_end bound and low_end bound.
        :type relative_width_goal: float
        :returns: Current width as logarithmic multiple of goal width [1].
        :rtype: float
        """
        return width_in_goals(self.relative_width, relative_width_goal)

    @staticmethod
    def wig(low_end: float, high_end: float, goal: float) -> float:
        """Return "logarithmic distance" between two loads.

        See width_in_goals for more details.

        It is useful to expose this part of logic, so users can see distances
        before performning the measurement.

        :param low_end: Intended load for the lower bound [tps].
        :param high_end: Intended load for the lower bound [tps].
        :param goal: Width goal to use as unit of measurement.
        :type low_end: float
        :type high_end: float
        :type goal: float
        :returns: Width between bounds as multiple of goal.
        :rtype: float
        """
        relative_width = (high_end - low_end) / (high_end)
        return width_in_goals(relative_width, goal)
