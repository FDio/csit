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

"""Module defining DiscreteInterval class."""

from dataclasses import dataclass

from .dataclass import secondary_field
from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth


# TODO: Can this be frozen?
@dataclass
class DiscreteInterval:
    """Interval class with more computations available.

    Along discrete form of width,
    a MLR specific way for halving the interval is also included.

    The two primary field values do not have to be valid relevant bounds,
    but at the end of the search, they usually are.

    The load values must be round.
    """

    lower_bound: DiscreteLoad
    """Value for the lower intended load (or load stats or similar)."""
    upper_bound: DiscreteLoad
    """Value for the higher intended load (or load stats or similar)."""
    # Primary fields above, derived below.
    discrete_width: DiscreteWidth = secondary_field()
    """Discrete width between intended loads (upper_bound minus lower_bound)."""

    def __post_init__(self) -> None:
        """Sort bounds by intended load, compute secondary quantities.

        :raises RuntimeError: If a result used non-rounded load.
        """
        if not self.lower_bound.is_round:
            raise RuntimeError(f"Non-round lower bound: {self.lower_bound!r}")
        if not self.upper_bound.is_round:
            raise RuntimeError(f"Non-round upper bound: {self.upper_bound!r}")
        if self.lower_bound > self.upper_bound:
            tmp = self.lower_bound
            self.lower_bound = self.upper_bound
            self.upper_bound = tmp
        self.discrete_width = self.upper_bound - self.lower_bound

    def __str__(self) -> str:
        """Convert to a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return (
            f"lower_bound=({self.lower_bound}),upper_bound=({self.upper_bound})"
        )

    # TODO: Use "target" instad of "goal" in argument and variable names.

    def width_in_goals(self, goal: DiscreteWidth) -> float:
        """Return relative width as a multiple of the given goal (int form).

        Integer forms are used for computation, safe as loads are rounded.
        The result is a float, as self int may not be divisible by goal int.

        :param goal: A relative width amount to be used as a unit.
        :type goal: DiscreteWidth
        :returns: Self width in multiples of (integer form of) goal width.
        :rtype: float
        """
        return int(self.discrete_width) / int(goal)

    def middle(self, goal: DiscreteWidth) -> DiscreteLoad:
        """Return new intended load (discrete form) in the middle.

        All calculations are based on int forms.

        One of the halfs is rounded to a power-of-two multiple of the goal.
        The power that leads to most even split is used.
        Lower width is the smaller one (if not exactly even).

        This approach prefers lower loads (to remain conservative) and can save
        some measurements (when all middle measurements have high loss).
        Note that when competing with external search from above,
        that search is already likely to produce widths that are
        power-of-two multiples of the target width.

        If the interval width is one goal (or less), RuntimeError is raised.
        If the interval width is between one and two goals (not including),
        a more even split is attempted (using half the goal value).

        :param goal: Target width goal to use for uneven halving.
        :type goal: DiscreteWidth
        :returns: New load to use for bisecting.
        :rtype: DiscreteLoad
        :raises RuntimeError: If an internal inconsistency is detected.
        """
        int_self, int_goal = int(self.discrete_width), int(goal)
        if int_self <= int_goal:
            raise RuntimeError(f"Do not halve small enough interval: {self!r}")
        if int_self == 2 * int_goal:
            # Even split, return here simplifies the while loop below.
            return self.lower_bound + goal
        if int_self < 2 * int_goal:
            # This can only happen when int_goal >= 2.
            # In this case, we do not have good enough split at this width goal,
            # but maybe this is not the final target, so we can attempt
            # a split at half width goal.
            if not int_goal % 2:
                return self.middle(goal=goal.half_rounded_down())
            # Odd int_goal, so this must by the last phase. Do even split.
            lo_width = self.discrete_width.half_rounded_down()
            return self.lower_bound + lo_width
        hi_width = goal
        lo_width = self.discrete_width - hi_width
        # We know lo_width > hi_width because we did not do the even split.
        while 1:
            hi2_width = hi_width * 2
            lo2_width = self.discrete_width - hi2_width
            if lo2_width <= hi2_width:
                break
            hi_width, lo_width = hi2_width, lo2_width
        # Which of the two options is more even? Product decides.
        if int(hi_width) * int(lo_width) > int(hi2_width) * int(lo2_width):
            # Previous attempt was more even, but hi_width was the smaller one.
            lo2_width = hi_width
        # Else lo2_width is more even and no larger than hi2_width.
        return self.lower_bound + lo2_width
