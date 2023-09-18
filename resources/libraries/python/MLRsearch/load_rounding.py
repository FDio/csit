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

"""Module defining LoadRounding class."""

import math

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class LoadRounding:
    """State for stateful utilities that round intended load values.

    For MLRsearch algorithm logic to be correct, it is important
    interval width expansion and narrowing are exactly reversible,
    which is not true in general for floating point number arithmetics.

    This class offers conversion to and from an integer quantity.
    Operations in the integer realm are guaranteed to be reversible,
    so the only risk is when converting between float and integer realm.

    Which relative width corresponds to the unit integer
    is dynamically computed from width goals,
    striking a balance between memory requirements and precision.

    There are two quality knobs. One restricts how far
    can an integer be from the exact float value.
    The other restrict how close it can be. That is to make sure
    even with unpredictable rounding errors during the conversion,
    the converted integer value is never bigger than the intended float value,
    to ensure the resulting intervals from MLRsearch will always
    meet the relative width goal.

    An instance of this class is mutable only in the sense it contains
    a growing cache of previously computed values.
    TODO: Hide the cache and present as frozen hashable object.
    """

    min_load: float
    """Minimal intended load [tps] to support, must be positive."""
    max_load: float
    """Maximal intended load [tps] to support, must be bigger than min load."""
    float_goals: Tuple[float]
    """Relative width goals to approximate, each must be positive
    and smaller than one."""
    quality_lower: float = 0.99
    """Minimal multiple of each goal to be achievable."""
    quality_upper: float = 0.999999
    """Maximal multiple of each goal to be achievable."""
    int_goals: List[int] = field(init=False, repr=False)
    """These amounts of units are within quality to float goals."""
    max_int_load: int = field(init=False, repr=False)
    """Integer for max load (min load int is zero)."""
    _int2load: List[Tuple[int, float]] = field(init=False, repr=False)
    """Known int values (sorted) and their float equivalents."""

    def __post_init__(self) -> None:
        """Ensure types, perform checks, initialize conversion structures.

        :raises RuntimeError: If a requirement is not met.
        """
        self.min_load = float(self.min_load)
        self.max_load = float(self.max_load)
        if not 0.0 < self.min_load < self.max_load:
            raise RuntimeError("Load limits not supported: {self}")
        self.quality_lower = float(self.quality_lower)
        self.quality_upper = float(self.quality_upper)
        if not 0.0 < self.quality_lower < self.quality_upper < 1.0:
            raise RuntimeError("Qualities not supported: {self}")
        goals = []
        for goal in self.float_goals:
            goal = float(goal)
            if not 0.0 < goal < 1.0:
                raise RuntimeError(f"Goal width {goal} is not supported.")
            goals.append(goal)
        self.float_goals = tuple(sorted(set(goals)))
        self.max_int_load = self._find_ints()
        self._int2load = []
        self._int2load.append((0, self.min_load))
        self._int2load.append((self.max_int_load, self.max_load))

    def _find_ints(self) -> int:
        """Find and return value for max_int_load.

        Separated out of post init, as this is less conversion and checking,
        and more math and searching.

        A dumb implementation would start with 1 and kept increasing by 1
        until all goals are within quality limits.
        An actual implementation is smarter with the increment,
        so it is expected to find the resulting values somewhat faster.

        :returns: Value to be stored as max_int_load.
        :rtype: int
        """
        minmax_log_width = math.log(self.max_load) - math.log(self.min_load)
        log_goals = [-math.log1p(-goal) for goal in self.float_goals]
        candidate = 1
        while 1:
            log_width_unit = minmax_log_width / candidate
            # Fallback to increment by one if rounding errors make tries bad.
            next_tries = [candidate + 1]
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
                # Else quality acceptable, not bumping the candidate.
            if acceptable:
                return candidate
            candidate = int(math.ceil(max(next_tries)))

    def int2float(self, int_load: int) -> float:
        """Convert from int to float tps load. Expand internal table as needed.

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
        raise RuntimeError("Bisect in int2float failed.")

    def float2int(self, float_load: float) -> int:
        """Convert and round from tps load to int. Maybe expand internal table.

        Too low or too high load result in zero or max int respectively.

        Result value is rounded down to an integer.

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
            return mid_int
        return lo_int
