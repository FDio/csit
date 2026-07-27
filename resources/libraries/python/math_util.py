# Copyright (c) 2026 Cisco and/or its affiliates.
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

"""Utility functions for common mathematical operations.

The functions are useful when hardware offers few "providers" with larger limits,
but the test has to use multiple "resources" and set up their smaller limits.
"""

import math


def div_round_up(
    needed: int, providers: int, zero_allowed: bool = False
) -> int:
    """Return sufficient number of resources per one available provider.

    Typically used to distribute per-worker queues over hardware devices.
    If plain division would not be an integer, the value is rounded up,
    so every resource has a provider but the providers are not loaded evenly.

    Some tests tolerate zero resources, some not, so behavior is configurable.

    :param needed: How many resources need a provider.
    :param providers: How many providers can provide resources.
    :param zero_allowed: Whether zero resources are tolerable outcome.
    :type needed: int
    :type providers: int
    :type zero_allowed: bool
    :returns: Minimal number of resources per provider to cover the need.
    :rtype: int
    :raises ValueError: If zero resources per provider are not tolerated.
    """
    ret = int(math.ceil(needed / providers))
    if ret < 1 and not zero_allowed:
        raise ValueError(f"Cannot tolerate dividing {needed} into {providers}")
    return ret


def div_round_down(limit: int, resources: int) -> int:
    """Return the per-resource limit to satisfy the per-provider limit.

    Typically used to make sure a test setting the per-resource limit
    does not overstep the per-provider limit.
    If plain division would not be an integer, the value is rounded down.

    Zero limit is never supported.

    :param limit: How many resources can the providers support overall.
    :param resources: How many different has the provider support.
    :type needed: int
    :type providers: int
    :returns: Maximal limit the test should not overstep per resource.
    :rtype: int
    :raises ValueError: If the limit would be zero.
    """
    ret = int(limit / resources)
    if ret < 1:
        raise ValueError(f"Cannot tolerate dividing {limit} over {resources}")
    return ret
