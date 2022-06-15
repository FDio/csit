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

from dataclasses import dataclass

from .comparable_measurement_result import ComparableMeasurementResult
from .discrete_width import DiscreteWidth


@dataclass
class MeasurementInterval:
    """Structure defining two measurements results, and their relation.

    The main purpose is in utilities calculating "distance" between
    the intended loads, a.k.a. interval width, in various quantities.

    Only measurements with round discrete form (the integer value matching
    the float value) of intended load are accepted.

    This class allows degenerate (i.e. zero width) intervals.
    """
    low_end: ComparableMeasurementResult
    """Measurement for the lower (or higher) load."""
    high_end: ComparableMeasurementResult
    """Measurement for the higher (or lower) load."""

    def __post_init__(self):
        """Sort bounds by intended load, compute secondary quantities.

        :raises RuntimeError: If a result used non-rounded load.
        """
        if not self.low_end.discrete_load.is_round:
            raise RuntimeError(f"Non-round low end: {self.low_end!r}")
        if not self.high_end.discrete_load.is_round:
            raise RuntimeError(f"Non-round low end: {self.high_end!r}")
        if self.low_end.intended_load > self.high_end.intended_load:
            self.low_end, self.high_end = self.high_end, self.low_end

    def width_in_goals(self, goal: DiscreteWidth) -> float:
        """Return relative width as a logaritmic multiple of given goal.

        Integer forms are used for computation, safe as end loads are rounded.
        The result is in float, as load rounding is to int, not to width goal.

        :param goal: high_end bound (float) times this (float) is the goal
            difference between high_end bound and low_end bound.
        :type relative_width_goal: DiscreteWidth
        :returns: Current width as (logarithmic) multiple of goal width.
        :rtype: float
        """
        return (
            int(self.high_end.discrete_load) - int(self.low_end.discrete_load)
        ) / int(goal)

    @property
    def relative_width(self) -> float:
        """Return relative width computed from float values.

        This is useful for debugging final MLR results,
        which may have zero-width intervals
        (or even different rounding instances).

        :returns: Difference of float load divided by high end load.
        :rtype: float
        """
        difference = self.high_end.intended_load - self.low_end.intended_load
        return difference / self.high_end.intended_load
