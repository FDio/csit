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

from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth
from .measurement_interval import MeasurementInterval


@dataclass
class DiscreteInterval(MeasurementInterval):
    """Interval class with more computations available.

    Contrary to MeasurementInterval,
    intervals of this class cannot be zero-width.

    Along discrete form of width,
    a MLR specific way for halving the interval is also included.
    """

    discrete_width: DiscreteWidth = field(init=False, repr=False)
    """Discrete width between intended loads (high_end minus low_end)."""

    def __post_init__(self):
        """Compute secondary quantities.

        :raises RuntimeError: If a result used non-rounded load.
        """
        super().__post_init__()
        self.discrete_width = (
            self.high_end.discrete_load - self.low_end.discrete_load
        )

    def middle(self, width_goal: DiscreteWidth) -> DiscreteLoad:
        """Return new intended load (discrete form) in the middle.

        All calculations are based on int forms.

        One of the halfs is rounded to a power-of-two multiple of the goal.
        The power that leads to most even split is used.
        Lower width is the smaller one (if not exactly even).
        This approach prefers lower loads and can save some measurements
        (by minimizing occurences of intervals smaller than the goal).

        If the interval width is one goal (or less), exception is raised.
        If the interval width is between one and two goals (not including),
        a more even split is attempted (as if half of goal was active).

        :param width_goal: Target width goal to use for uneven halving.
        :type width_goal: DiscreteWidth
        :returns: New load to use for bisecting.
        :rtype: DiscreteLoad
        :raises RuntimeError: If an internal inconsistency is detected.
        """
        int_self, int_goal = int(self.discrete_width), int(width_goal)
        if int_self <= int_goal:
            raise RuntimeError(f"Do not halve small enough interval: {self!r}")
        if int_self == 2 * int_goal:
            # Even split, return here simplifies the while loop below.
            return self.low_end.discrete_load + width_goal
        if int_self < 2 * int_goal:
            # This can only happen when int_goal >= 2.
            # In this case, we do not have good enough split at this width goal,
            # but maybe this is not the final phase, so we can attempt
            # a split at half width goal.
            if not int_goal % 2:
                return self.middle(width_goal=width_goal.half_rounded_down())
            # Odd int_goal, so this must by the last phase. Do even split.
            lo_width = self.discrete_width.half_rounded_down()
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
