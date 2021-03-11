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


# TODO: Say "relative" instead of "logarithmic" where possible.

def step_down(relative_width, current_bound):
    """Return rate of logarithmic width below.

    :param relative_width: The base relative width to use.
    :param current_bound: The current target transmit rate to move [pps].
    :type relative_width: float
    :type current_bound: float
    :returns: Transmit rate smaller by relative width [pps].
    :rtype: float
    """
    return current_bound * (1.0 - relative_width)

def double_relative_width(relative_width):
    """Return relative width corresponding to double logarithmic width.

    :param relative_width: The base relative width to double.
    :type relative_width: float
    :returns: The relative width of double logarithmic size.
    :rtype: float
    """
    return 1.99999 * relative_width - relative_width * relative_width
    # The number should be 2.0, but we want to avoid rounding errors,
    # and ensure half of double is not larger than the original value.

def double_step_down(relative_width, current_bound):
    """Return rate of double logarithmic width below.

    :param relative_width: The base relative width to double.
    :param current_bound: The current target transmit rate to move [pps].
    :type relative_width: float
    :type current_bound: float
    :returns: Transmit rate smaller by logarithmically double width [pps].
    :rtype: float
    """
    return step_down(double_relative_width(relative_width), current_bound)

def step_up(relative_width, current_bound):
    """Return rate of logarithmic width above.

    :param relative_width: The base relative width to use.
    :param current_bound: The current target transmit rate to move [pps].
    :type relative_width: float
    :type current_bound: float
    :returns: Transmit rate larger by logarithmically double width [pps].
    :rtype: float
    """
    return current_bound / (1.0 - relative_width)

def double_step_up(relative_width, current_bound):
    """Return rate of double logarithmic width above.

    :param relative_width: The base relative width to double.
    :param current_bound: The current target transmit rate to move [pps].
    :type relative_width: float
    :type current_bound: float
    :returns: Transmit rate larger by logarithmically double width [pps].
    :rtype: float
    """
    return step_up(double_relative_width(relative_width), current_bound)

def half_relative_width(relative_width):
    """Return relative width corresponding to half logarithmic width.

    :param relative_width: The base relative width to halve.
    :type relative_width: float
    :returns: The relative width of half logarithmic size.
    :rtype: float
    """
    return 1.0 - math.sqrt(1.0 - relative_width)

def half_step_up(relative_width, current_bound):
    """Return rate of half logarithmic width above.

    :param relative_width: The base relative width to halve.
    :param current_bound: The current target transmit rate to move [pps].
    :type relative_width: float
    :type current_bound: float
    :returns: Transmit rate larger by logarithmically half width [pps].
    :rtype: float
    """
    return step_up(half_relative_width(relative_width), current_bound)
