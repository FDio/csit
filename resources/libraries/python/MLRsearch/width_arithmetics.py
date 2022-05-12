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

"""Module defining utility functions for manipulating intervals."""

import math


# TODO: Make the number of nines configurable.
ROUNDING_CONSTANT = 0.999999

def width_in_goals(width: float, goal: float) -> float:
    """Return logarithm of width divided by logarithm of goal.

    This is a common operation, also useful for debugging.

    Implementation uses log1p to avoid rounding errors for small widths,
    while risking rounding errors for big widths.

    :param width: Relative interval width to describe.
    :param goal: Width goal to use for describing.
    :type width: float
    :type goal: float
    :returns: Width expressed in goals.
    :rtype: float
    """
    return math.log1p(-width) / math.log1p(-goal)

def multiply_relative_width(relative_width: float, coefficient: float) -> float:
    """Return relative width corresponding to multiplied logarithmic width.

    The multiplication happens in logarithmic space,
    so the resulting relative width is always less than 1.

    When expanding, it is recommended to multiply coefficient with
    ROUNDING_CONSTANT before passing,
    so the subsequent halving does not result in a wider than goal interval.

    :param relative_width: The base relative width to multiply.
    :param coefficient: Multiply by this in logarithmic space.
    :param rounding_c: Use to manipulate rounding errors.
    :type relative_width: float
    :type coefficient: float
    :returns: The relative width of multiplied logarithmic size.
    :rtype: float
    """
    # Using log1p and expm1 to avoid rounding errors for very small widths.
    old_log_width = math.log1p(-relative_width)
    # Slight decrease to prevent rounding errors from prolonging the search.
    new_log_width = old_log_width * coefficient
    return -math.expm1(new_log_width)

def halve_relative_width(relative_width: float, width_goal: float) -> float:
    """Return relative width corresponding to half logarithmic width.

    The logic attempts to save some halvings in future
    by performing uneven split here.
    If rounding error risk is detected, even split is used.

    With splitting unevenly, the larger width is returned,
    using rounding constant to round down.

    :param relative_width: The base relative width to halve.
    :param width_goal: Width goal for final phase.
    :type relative_width: float
    :type width_goal: float
    :returns: The relative width of half logarithmic size.
    :rtype: float
    """
    wig = width_in_goals(relative_width, width_goal)
    cwig = 2.0 * math.ceil(wig / 2.0)
    # TODO: What is the correct application of rounding constant instead of 2.9?
    if wig <= 2.9:
        # Avoid too uneven splits (under one goal).
        return multiply_relative_width(relative_width, 0.5)
    coefficient = cwig / 2 * ROUNDING_CONSTANT
    new_width = multiply_relative_width(width_goal, coefficient)
    return new_width

def step_down(current_load: float, relative_width: float) -> float:
    """Return rate of logarithmic width below.

    :param current_load: The current intended load to move [tps].
    :param relative_width: The base relative width to use.
    :type current_load: float
    :type relative_width: float
    :returns: New intended load smaller by relative width [tps].
    :rtype: float
    """
    return current_load * (1.0 - relative_width)

def step_up(current_load: float, relative_width: float) -> float:
    """Return rate of logarithmic width above.

    :param current_load: The current intended load to move [tps].
    :param relative_width: The base relative width to use.
    :type current_load: float
    :type relative_width: float
    :returns: New intended load larger by logarithmically double width [tps].
    :rtype: float
    """
    return current_load / (1.0 - relative_width)

def multiple_step_down(
    current_load: float, relative_width: float, coefficient: float
) -> float:
    """Return rate of multiplied logarithmic width below.

    The multiplication happens in logarithmic space,
    so the resulting applied relative width is always less than 1.
    Rounding constant is automatically applied.

    :param relative_width: The base relative width to double.
    :param current_load: The current intended load to move [tps].
    :param coefficient: Multiply by this in logarithmic space.
    :type relative_width: float
    :type current_load: float
    :type coefficient: float
    :returns: New intended load smaller by logarithmically multiplied width [tps].
    :rtype: float
    """
    coeff = coefficient * ROUNDING_CONSTANT
    new_width = multiply_relative_width(relative_width, coeff)
    return step_down(current_load, new_width)

def multiple_step_up(
    current_load: float, relative_width: float, coefficient: float
) -> float:
    """Return rate of double logarithmic width above.

    The multiplication happens in logarithmic space,
    so the resulting applied relative width is always less than 1.
    Rounding constant is automatically applied.

    :param current_load: The current intended load to move [tps].
    :param relative_width: The base relative width to double.
    :param coefficient: Multiply by this in logarithmic space.
    :type current_load: float
    :type relative_width: float
    :type coefficient: float
    :returns: New intended load larger by logarithmically multiplied width [tps].
    :rtype: float
    """
    coeff = coefficient * ROUNDING_CONSTANT
    new_width = multiply_relative_width(relative_width, coeff)
    return step_up(current_load, new_width)

def half_step_down(
    current_load: float, relative_width: float, width_goal: float
) -> float:
    """Return rate of half logarithmic width below.

    This function is smart, using uneven splits to avoid some measurements,
    that is why the width goal is needed.
    As for computing half width it is more convenient to return
    the larger width in case of uneven split,
    and it is more conservative to start with smaller loads,
    only this (and no half_step_up) is defined.

    Not supporting optional strict halving here, because pylint has trouble
    determining where an Optional typed variable can no longer be None.

    :param relative_width: The base relative width to halve.
    :param current_load: The current intended load to move [tps].
    :param width_goal: Apply uneven splits when this is provided.
    :type relative_width: float
    :type current_load: float
    :type width_goal: Optional[float]
    :returns: New intended load larger by logarithmically half width [tps].
    :rtype: float
    """
    new_width = halve_relative_width(relative_width, width_goal)
    return step_down(current_load, new_width)

def strict_half_step_down(current_load: float, relative_width: float) -> float:
    """Return rate of half logarithmic width below.

    This function avoids any smart logic.

    :param relative_width: The base relative width to halve.
    :param current_load: The current intended load to move [tps].
    :type relative_width: float
    :type current_load: float
    :returns: New intended load larger by logarithmically half width [tps].
    :rtype: float
    """
    new_width = multiply_relative_width(relative_width, 0.5)
    return step_down(current_load, new_width)
