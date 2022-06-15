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

"""Module defining BaseLoadRounding class."""

import math

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class BaseLoadRounding:
    """State for stateful utilities that round intended load values.

    For MLRsearch algorithm logic to be correct, it is important
    interval width expansion and narrowing are exactly reversible,
    which is not true in general for floating point number arithmetics.

    This class offers conversion to and from an integer quantity.
    Operations in the integer realm are guaranteed to be reversible,
    so the only risk is when converting betwwn float and integer realm.

    What relative width corresponds to the unit integer
    is dynamically computed from width goals,
    striking a balance between memory requirements and precision.

    There are two quality goals. One restricts how far
    can an integer be from the exact float value.
    The other restrict how close it can be. That is to make sure
    even with unpredictable rounding errors during the conversion,
    the converted integer value is never bigger than the intended float value,
    to ensure the resulting intervals from MLRsearch will always
    meet the relative width goal.

    Even more convenience is offered when (integer) goals are offered
    as DiscreteWidth instances. To avoid circular dependencies (type hints),
    this class does not offer that convenience; see LoadRounding.
    """

    min_load: float
    """Minimal intended load [tps] to support, must be positive."""
    max_load: float
    """Maximal intended load [tps] to support, must be bigger than min load."""
    float_goals: List[float]
    """Relative width goals to approximate, each must be positive."""
    quality_lower: float = 0.99
    """Minimal multiple of each goal to be achievable."""
    quality_upper: float = 0.999999
    """Maximal multiple of each goal to be achievable."""
    int_goals: List[int] = field(init=False, repr=False)
    """These amounts of units are within quality to float goals."""
    max_int_load: int = field(init=False, repr=False)
    """Integer for max load (min load is int zero)."""
    _int2load: List[Tuple[int, float]] = field(init=False, repr=False)
    """Known int values (sorted) and their float equivalents."""

    def __post_init__(self) -> None:
        """Ensure types, perform checks, initialize conversion structures.

        :raises RuntimeError: If a requirement is not met.
        """
        self.min_load = float(self.min_load)
        self.max_load = float(self.max_load)
        if not 0.0 < self.min_load < self.max_load:
            raise RuntimeError(u"Load limits not supported.")
        self.quality_lower = float(self.quality_lower)
        self.quality_upper = float(self.quality_upper)
        if not 0.0 < self.quality_lower < self.quality_upper < 1.0:
            raise RuntimeError(u"Qualities not supported.")
        goals = list()
        for goal in self.float_goals:
            goal = float(goal)
            if not 0.0 < goal < 1.0:
                raise RuntimeError(f"Goal width {goal} is not supported.")
            goals.append(goal)
        self.float_goals = goals
        self.max_int_load, self.int_goals = self._find_ints()
        self._int2load = list()
        self._int2load.append((0, self.min_load))
        self._int2load.append((self.max_int_load, self.max_load))

    def _find_ints(self) -> Tuple[int, List[int]]:
        """Find and return values for max_int_load and int_goals.

        Separated out of post init, as this is less conversion and checking
        and more math and searching.

        A dumb implementation would start with 1 and kept increasing by 1
        until all goals are within quality limits.
        An actual implementation is smarter with the increment,
        so it is expected to find the resulting values faster.

        :returns: Value to be stored as max_int_load and int goals.
        :rtype: Tuple[int, List[int]]
        """
        minmax_log_width = math.log(self.max_load) - math.log(self.min_load)
        # We could remove duplicated goal values here,
        # and re-duplicate return values.
        # But the current code should be fast enough even with duplicates,
        # so few milliseconds are not worth making the code more complicated.
        log_goals = [-math.log1p(-goal) for goal in self.float_goals]
        candidate = 1
        while 1:
            log_width_unit = minmax_log_width / candidate
            int_goals, next_tries = list(), list()
            acceptable = True
            for log_goal in log_goals:
                units = log_goal / log_width_unit
                int_units = math.floor(units)
                quality = int_units / units
                if not self.quality_lower <= quality <= self.quality_upper:
                    acceptable = False
                    target = (int_units + 1) / self.quality_upper
                    next_try = (target / units) * candidate
                    next_tries.append(next_try)
                else:
                    # Quality acceptable, not bumping the candidate.
                    next_tries.append(candidate)
                int_goals.append(int_units)
            if acceptable:
                return candidate, int_goals
            next_try = int(math.ceil(max(next_tries)))
            # Fallback to increment by one if rounding errors made tries bad.
            candidate = max(next_try, candidate + 1)

    def int2float(self, int_load: int) -> float:
        """Convert from int to tps load. Expand internal table as needed.

        Too low or too high ints result in min or max load respectively.

        :param int_load: Integer quantity to turn back into float load.
        :type int_load: int
        :returns: Converted load in tps.
        :rtype: float
        :raises RuntimeError: If internal inconsistency is detected.
        """
        if int_load <= 0:
            return self.min_load
        if int_load >= self.max_int_load:
            return self.max_load
        lo_index, hi_index = 0, len(self._int2load)
        lo_int, hi_int = 0, self.max_int_load
        lo_load, hi_load = self.min_load, self.max_load
        while hi_int - lo_int >= 2:
            mid_index = (hi_index + lo_index + 1) // 2
            if mid_index >= hi_index:
                mid_int = (hi_int + lo_int) // 2
                log_coeff = math.log(hi_load) - math.log(lo_load)
                log_coeff *= (mid_int - lo_int) / (hi_int - lo_int)
                mid_load = lo_load * math.exp(log_coeff)
                self._int2load.insert(mid_index, (mid_int, mid_load))
                hi_index += 1
            mid_int, mid_load = self._int2load[mid_index]
            if mid_int < int_load:
                lo_index, lo_int, lo_load = mid_index, mid_int, mid_load
                continue
            if mid_int > int_load:
                hi_index, hi_int, hi_load = mid_index, mid_int, mid_load
                continue
            return mid_load
        raise RuntimeError(u"Bisect in int2load failed.")

    def float2int(self, float_load: float) -> int:
        """Convert and round from tps load to int. Maybe internal table.

        Too low or too high load result in zero or max int respectively.

        Rounds to closest (tps for the) integer, in logarithmic tps space.

        :param float_load: Tps quantity to convert into int.
        :type float_load: float
        :returns: Converted integer value suitable for halving.
        :rtype: int
        """
        if float_load <= self.min_load:
            return 0
        if float_load >= self.max_load:
            return self.max_int_load
        lo_index, hi_index = 0, len(self._int2load)
        lo_int, hi_int = 0, self.max_int_load
        lo_load, hi_load = self.min_load, self.max_load
        while hi_int - lo_int >= 2:
            mid_index = (hi_index + lo_index + 1) // 2
            if mid_index >= hi_index:
                mid_int = (hi_int + lo_int) // 2
                log_coeff = math.log(hi_load) - math.log(lo_load)
                log_coeff *= (mid_int - lo_int) / (hi_int - lo_int)
                mid_load = lo_load * math.exp(log_coeff)
                self._int2load.insert(mid_index, (mid_int, mid_load))
                hi_index += 1
            mid_int, mid_load = self._int2load[mid_index]
            if mid_load < float_load:
                lo_index, lo_int, lo_load = mid_index, mid_int, mid_load
                continue
            if mid_load > float_load:
                hi_index, hi_int, hi_load = mid_index, mid_int, mid_load
                continue
            return mid_load
        # Rounding is needed.
        is_big = float_load * float_load > lo_load * hi_load
        return hi_int if is_big else lo_int
