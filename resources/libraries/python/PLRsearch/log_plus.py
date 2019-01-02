# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Module holding functions for avoiding rounding underflows.

Some applications wish to manipulate non-negative numbers
which are many orders of magnitude apart.
In those circumstances, it is useful to store
the logarithm of the intended number.

As math.log(0.0) raises an exception (instead returning -inf or nan),
and 0.0 might be a result of computation caused only by rounding error,
functions of this module use None as -inf.

TODO: Figure out a more performant way of handling -inf.

The functions handle the common task of adding or substracting
two numbers where both operands and the result is given in logarithm form.
There are conditionals to make sure overflow does not happen (if possible)
during the computation."""

import math


def log_plus(first, second):
    """Return logarithm of the sum of two exponentials.

    Basically math.log(math.exp(first) + math.exp(second))
    which avoids overflow and uses None as math.log(0.0).

    TODO: replace with scipy.special.logsumexp ? Test it.

    :param first: Logarithm of the first number to add (or None if zero).
    :param second: Logarithm of the second number to add (or None if zero).
    :type first: float
    :type second: float
    :returns: Logarithm of the sum (or None if zero).
    :rtype: float
    """

    if first is None:
        return second
    if second is None:
        return first
    if second > first:
        return second + math.log(1.0 + math.exp(first - second))
    else:
        return first + math.log(1.0 + math.exp(second - first))


def log_minus(first, second):
    """Return logarithm of the difference of two exponentials.

    Basically math.log(math.exp(first) - math.exp(second))
    which avoids overflow and uses None as math.log(0.0).

    TODO: Support zero difference?
    TODO: replace with scipy.special.logsumexp ? Test it.

    :param first: Logarithm of the number to subtract from (or None if zero).
    :param second: Logarithm of the number to subtract (or None if zero).
    :type first: float
    :type second: float
    :returns: Logarithm of the difference.
    :rtype: float
    :raises RuntimeError: If the difference would be non-positive.
    """

    if first is None:
        raise RuntimeError("log_minus: does not suport None first")
    if second is None:
        return first
    if second >= first:
        raise RuntimeError("log_minus: first has to be bigger than second")
    factor = -math.expm1(second - first)
    if factor <= 0.0:
        raise RuntimeError("log_minus: non-positive number to log")
    else:
        return first + math.log(factor)


def safe_exp(log_value):
    """Return exponential of the argument, or zero if the argument is None.

    :param log_value: The value to exponentiate.
    :type log_value: NoneType or float
    :returns: The exponentiated value.
    :rtype: float
    """
    if log_value is None:
        return 0.0
    return math.exp(log_value)
