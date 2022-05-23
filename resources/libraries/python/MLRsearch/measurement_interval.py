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
from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth


@dataclass
class MeasurementInterval:
    """Structure defining two measurements results, and their relation.

    The main purpose is in utilities calculating "distance" between
    the intended loads, a.k.a. interval width, in various quantities.

    Only measurements with round (int vlaue matching float value)
    intended load are accepted.
    Also, a MLR specific halving method is included.
    """
    low_end: ComparableMeasurementResult
    """Measurement for the lower (or higher) load."""
    high_end: ComparableMeasurementResult
    """Measurement for the higher (or lower) load."""
    discrete_width: DiscreteWidth = field(init=False, repr=False)
    """Discrete width between intended loads. Tps of high_end minus of low_end."""

    def __post_init__(self):
        """Sort bounds by intended load, compute secondary quantities.

        :raises RuntimeError: If a result used non-rounded load.
        """
        if self.low_end.intended_load > self.high_end.intended_load:
            self.low_end, self.high_end = self.high_end, self.low_end
        if not self.low_end.discrete_load.is_round:
            raise RuntimeError(f"Non-round low end: {self.low_end!r}")
        if not self.high_end.discrete_load.is_round:
            raise RuntimeError(f"Non-round low end: {self.high_end!r}")
        self.discrete_width = (
            self.high_end.discrete_load - self.low_end.discrete_load
        )

    def width_in_goals(self, goal: DiscreteWidth) -> float:
        """Return relative width as a logaritmic multiple of given goal.

        In values are used for computation, safe as end loads are rounded.
        The result is in float, as rounding is to int, not to width goal.

        :param goal: high_end bound (float) times this (float) is the goal
            difference between high_end bound and low_end bound.
        :type relative_width_goal: DiscreteWidth
        :returns: Current width as (logarithmic) multiple of goal width.
        :rtype: float
        """
        return int(self.discrete_width) / int(goal)

    def middle(self, width_goal: DiscreteWidth) -> DiscreteLoad:
        """Return new intended load (discrete form) in the middle.

        All calculations are based on int forms.

        One of the halfs is rounded to a power-of-two multiple of the goal.
        The power that leads to most even split is used.
        Lower width is the smaller one (if not exactly even).
        This approach prefers lower loads and can save some measurements
        (by avoiding intervals smaller than the goal).

        If the interval width is one goal (or less), exception is raised.
        If the interval width is between one and two goals (not including),
        even split is attempted (still rounded to integer).

        :param width_goal: Target width goal to use for uneven halving.
        :type width_goal: DiscreteWidth
        :returns: New load to use for bisecting.
        :rtype: DiscreteLoad
        :raises RuntimeError: If an internal inconsistency is detected.
        """
        int_self, int_goal = int(self.discrete_width), int(width_goal)
        if int_self <= int_goal:
            raise RuntimeError(f"Do not halve small enough interval: {self!r}")
        if int_self <= 2 * int_goal:
            lo_width = DiscreteWidth(
                rounding=self.discrete_width.rounding, int_width=int_self // 2
            )
            return self.low_end.discrete_load + lo_width
        hi_width = width_goal
        lo_width = self.discrete_width - hi_width
        # We know lo_width > hi_width because we did not do the even split.
        while 1:
            hi2_width = hi_width * 2
            lo2_width = self.discrete_width - hi2_width
            if lo2_width <= hi2_width:
                break
            hi_width, lo_width = hi2_width, lo2_width
        # Which of the two options is more even? Product decides.
        if int(hi_width) * int(lo_width) < int(hi2_width) * int(lo2_width):
            hi_width, lo_width = hi2_width, lo2_width
        return self.low_end.discrete_load + lo_width
