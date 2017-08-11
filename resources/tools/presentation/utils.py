# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""General purpose utilities.
"""


from math import sqrt


def mean(items):
    """Calculate mean value from the items.

    :param items: Mean value is calculated from these items.
    :type items: list
    :returns: MEan value.
    :rtype: float
    """

    return float(sum(items)) / len(items)


def stdev(items):
    """Calculate stdev from the items.

    :param items: Stdev is calculated from these items.
    :type items: list
    :returns: Stdev.
    :rtype: float
    """

    avg = mean(items)
    variance = [(x - avg) ** 2 for x in items]
    stddev = sqrt(mean(variance))
    return stddev
