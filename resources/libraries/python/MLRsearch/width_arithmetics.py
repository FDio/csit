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


ROUNDING_CONSTANT = 0.999999

def multiply_relative_width(relative_width, coefficient):
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
    # Using log1p and expm1 to avoid rounding errors for small widths.
    old_log_width = math.log1p(-relative_width)
    # Slight decrease to prevent rounding errors from prolonging the search.
    # TODO: Make the nines configurable.
    new_log_width = old_log_width * coefficient
    return -math.expm1(new_log_width)

def halve_relative_width(relative_width, width_goal):
    """Return relative width corresponding to half logarithmic width.

    The logic attempts to save some halvings in future
    by performing uneven split here.
    If rounding error risk is detected even split is used.

    :param relative_width: The base relative width to halve.
    :param width_goal: Width goal for final phase.
    :type relative_width: float
    :type width_goal: float
    :returns: The relative width of half logarithmic size.
    :rtype: float
    """
    wig = math.log1p(-relative_width) / math.log1p(-width_goal)
    # Wig means Width In Goals.
    cwig = 2.0 * math.ceil(wig / 2.0)
    fwig = 2.0 * math.ceil(wig * ROUNDING_CONSTANT * ROUNDING_CONSTANT / 2.0)
    if wig <= 2.0 or cwig != fwig:
        # Avoid too uneven splits.
        return multiply_relative_width(relative_width, 0.5)
    coefficient = cwig / 2
    new_width = multiply_relative_width(width_goal, coefficient)
    return new_width

def step_down(current_bound, relative_width):
    """Return rate of logarithmic width below.

    :param current_bound: The current target transmit rate to move [pps].
    :param relative_width: The base relative width to use.
    :type current_bound: float
    :type relative_width: float
    :returns: Transmit rate smaller by relative width [pps].
    :rtype: float
    """
    return current_bound * (1.0 - relative_width)

def step_up(current_bound, relative_width):
    """Return rate of logarithmic width above.

    :param current_bound: The current target transmit rate to move [pps].
    :param relative_width: The base relative width to use.
    :type current_bound: float
    :type relative_width: float
    :returns: Transmit rate larger by logarithmically double width [pps].
    :rtype: float
    """
    return current_bound / (1.0 - relative_width)

def multiple_step_down(current_bound, relative_width, coefficient):
    """Return rate of multiplied logarithmic width below.

    The multiplication happens in logarithmic space,
    so the resulting applied relative width is always less than 1.
    Rounding constant is automatically applied.

    :param relative_width: The base relative width to double.
    :param current_bound: The current target transmit rate to move [pps].
    :param coefficient: Multiply by this in logarithmic space.
    :type relative_width: float
    :type current_bound: float
    :type coefficient: float
    :returns: Transmit rate smaller by logarithmically multiplied width [pps].
    :rtype: float
    """
    coeff = coefficient * ROUNDING_CONSTANT
    new_width = multiply_relative_width(relative_width, coeff)
    return step_down(current_bound, new_width)

def multiple_step_up(current_bound, relative_width, coefficient):
    """Return rate of double logarithmic width above.

    The multiplication happens in logarithmic space,
    so the resulting applied relative width is always less than 1.
    Rounding constant is automatically applied.

    :param current_bound: The current target transmit rate to move [pps].
    :param relative_width: The base relative width to double.
    :param coefficient: Multiply by this in logarithmic space.
    :type current_bound: float
    :type relative_width: float
    :type coefficient: float
    :returns: Transmit rate larger by logarithmically multiplied width [pps].
    :rtype: float
    """
    coeff = coefficient * ROUNDING_CONSTANT
    new_width = multiply_relative_width(relative_width, coeff)
    return step_up(current_bound, new_width)

def half_step_up(current_bound, relative_width, width_goal):
    """Return rate of half logarithmic width above.

    This function is smart, using uneven splits to avoid some measurements,
    that is why the width goal is needed.

    Not supporting optional strict halving here, because pylint has trouble
    determining where an Optional typed variable can no longer be None.

    :param relative_width: The base relative width to halve.
    :param current_bound: The current target transmit rate to move [pps].
    :param width_goal: Apply uneven splits when this is provided.
    :type relative_width: float
    :type current_bound: float
    :type width_goal: Optional[float]
    :returns: Transmit rate larger by logarithmically half width [pps].
    :rtype: float
    """
    new_width = halve_relative_width(relative_width, width_goal)
    return step_up(current_bound, new_width)

def strict_half_step_up(current_bound, relative_width):
    """Return rate of half logarithmic width above.

    This function avoids the smart logic.

    :param relative_width: The base relative width to halve.
    :param current_bound: The current target transmit rate to move [pps].
    :type relative_width: float
    :type current_bound: float
    :returns: Transmit rate larger by logarithmically half width [pps].
    :rtype: float
    """
    new_width = multiply_relative_width(relative_width, 0.5)
    return step_up(current_bound, new_width)
