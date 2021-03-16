# Copyright (c) 2021 Cisco and/or its affiliates.
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

from robot.api import logger


ROUNDING_CONSTANT = 0.999999

def multiply_relative_width(relative_width, coefficient):
    """Return relative width corresponding to multiplied logarithmic width.

    The multiplication happens in logarithmic space,
    so the resulting relative width is always less than 1.

    :param relative_width: The base relative width to multiply.
    :param coefficient: Multiply by this in logarithmic space.
    :type relative_width: float
    :type coefficient: float
    :returns: The relative width of multiplied logarithmic size.
    :rtype: float
    """
    old_log_width = math.log(1.0 - relative_width)
    # Slight decrease to prevent rounding errors from prolonging the search.
    # TODO: Make the nines configurable.
    new_log_width = old_log_width * coefficient * ROUNDING_CONSTANT
    return 1.0 - math.exp(new_log_width)

def halve_relative_width(relative_width, goal_width):
    """Return relative width corresponding to half logarithmic width.

    The logic attempts to save some halvings in future by performing
    uneven split. If rounding error risk is detected,
    even split is used.

    :param relative_width: The base relative width to halve.
    :param goal_width: Width goal for final phase.
    :type relative_width: float
    :type goal_width: float
    :returns: The relative width of half logarithmic size.
    :rtype: float
    """
    logger.debug(f"halve_relative_width({relative_width}, {goal_width}):")
    fallback_width = 1.0 - math.sqrt(1.0 - relative_width)
    logger.debug(f"fallback_width: {fallback_width}")
    # Wig means Width In Goals.
    wig = math.log(1.0 - relative_width) / math.log(1.0 - goal_width)
    logger.debug(f"wig: {wig}")
    cwig = math.ceil(wig)
    logger.debug(f"cwig: {cwig}")
    if wig <= 2.0 or cwig != math.ceil(wig * ROUNDING_CONSTANT):
        logger.debug(u"returning fallback")
        return fallback_width
    coefficient = cwig // 2
    logger.debug(f"coefficient: {coefficient}")
    new_width = multiply_relative_width(goal_width, coefficient)
    logger.debug(f"returning new width: {new_width}")
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

    :param relative_width: The base relative width to double.
    :param current_bound: The current target transmit rate to move [pps].
    :param coefficient: Multiply by this in logarithmic space.
    :type relative_width: float
    :type current_bound: float
    :type coefficient: float
    :returns: Transmit rate smaller by logarithmically multiplied width [pps].
    :rtype: float
    """
    new_width = multiply_relative_width(relative_width, coefficient)
    return step_down(current_bound, new_width)

def multiple_step_up(current_bound, relative_width, coefficient):
    """Return rate of double logarithmic width above.

    The multiplication happens in logarithmic space,
    so the resulting applied relative width is always less than 1.

    :param current_bound: The current target transmit rate to move [pps].
    :param relative_width: The base relative width to double.
    :param coefficient: Multiply by this in logarithmic space.
    :type current_bound: float
    :type relative_width: float
    :type coefficient: float
    :returns: Transmit rate larger by logarithmically multiplied width [pps].
    :rtype: float
    """
    new_width = multiply_relative_width(relative_width, coefficient)
    return step_up(current_bound, new_width)

def half_step_up(current_bound, relative_width, goal_width):
    """Return rate of half logarithmic width above.

    :param relative_width: The base relative width to halve.
    :param current_bound: The current target transmit rate to move [pps].
    :type relative_width: float
    :type current_bound: float
    :returns: Transmit rate larger by logarithmically half width [pps].
    :rtype: float
    """
    new_width = halve_relative_width(relative_width, goal_width)
    return step_up(current_bound, new_width)
