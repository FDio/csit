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
    """Stateful state of utilities for rounding intended load values.

    For MLRsearch algorithm logic to be correct, it is important
    interval width expansion and halving are exactly reversible,
    which is not true in general for floating point number arithmetics.

    This class offers conversion to and from an integer quantity,
    where the operations are reversible. What relative width corresponds
    to the unit integer is dynamically computed from width goals,
    striking a balance between memory requirements and precision.

    Even more convenience is offered when (integer) goals are offered
    as DiscreteWidth instances. To avoid circular type hints,
    this class does not offer that convenience, see LoadRounding.
    """

    min_load: float
    """Minimal intended load [tps] to support."""
    max_load: float
    """Maximal intended load [tps] to support."""
    float_goals: List[float]
    """Relative width goals to approximate."""
    quality_lower: float = 0.99
    """Minimal multiple of each goal to be achievable."""
    quality_upper: float = 0.999999
    """Maximal multiple of each goal to be achievable."""
    int_goals: List[int] = field(init=False, repr=False)
    """These amounts of units are withing quality to float goals."""
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
            # TODO: Include values in exception message.
            raise RuntimeError(u"Load limits not supported.")
        self.quality_lower = float(self.quality_lower)
        self.quality_upper = float(self.quality_upper)
        if not 0.0 < self.quality_lower < self.quality_upper < 1.0:
            # TODO: Include values in exception message.
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
        """Find and return values for max_int_load and int goals.

        Separated out of post init, as this is less conversion and checking
        and more math and searching.

        A dumb implementation would start with 1 and kept increasing by 1
        until all goals are within quality limits.
        An actual implementation is smarter with the increment,
        so it is expected to be faster.

        FIXME: While developing, the dumb way is used, as it is less error-prone.

        :returns: Value to be stored as max_int_load and int goals.
        :rtype: Tuple[int, List[int]]
        """
        minmax_log_width = math.log(self.max_load) - math.log(self.min_load)
        log_goals = [-math.log1p(-goal) for goal in self.float_goals]
        candidate = 0
        while 1:
            candidate += 1
            log_width_unit = minmax_log_width / candidate
            int_goals = list()
            for log_goal in log_goals:
                units = log_goal / log_width_unit
                int_units = math.floor(units)
                quality = int_units / units
                if not self.quality_lower <= quality <= self.quality_upper:
                    # Bad candidate, escape for to continue while.
                    break
                int_goals.append(int_units)
            else:
                return candidate, int_goals
            # Continue with next candidate.

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
        lower_index, upper_index = 0, len(self._int2load)
        lower_int, upper_int = 0, self.max_int_load
        lower_load, upper_load = self.min_load, self.max_load
        while upper_int - lower_int >= 2:
            mid_index = (upper_index + lower_index + 1) // 2
            if mid_index >= upper_index:
                mid_int = (upper_int + lower_int) // 2
                log_coeff = math.log(upper_load) - math.log(lower_load)
                log_coeff *= (mid_int - lower_int) / (upper_int - lower_int)
                mid_load = lower_load * math.exp(log_coeff)
                self._int2load.insert(mid_index, (mid_int, mid_load))
                upper_index += 1
            mid_int, mid_load = self._int2load[mid_index]
            if mid_int < int_load:
                lower_index, lower_int, lower_load = mid_index, mid_int, mid_load
                continue
            if mid_int > int_load:
                upper_index, upper_int, upper_load = mid_index, mid_int, mid_load
                continue
            return mid_load
        raise RuntimeError(u"Bisect in int2load failed.")

    def float2int(self, float_load: float) -> int:
        """Convert and round from tps load to int. Maybe internal table.

        Too low or too high load result in zero or max int respectively.

        Rounds to closest (tps for) int in logarithmic tps space.

        :param float_load: Tps quantity to convert into int.
        :type float_load: float
        :returns: Converted integer value suitable for halving.
        :rtype: int
        """
        if float_load <= self.min_load:
            return 0
        if float_load >= self.max_load:
            return self.max_int_load
        lower_index, upper_index = 0, len(self._int2load)
        lower_int, upper_int = 0, self.max_int_load
        lower_load, upper_load = self.min_load, self.max_load
        while upper_int - lower_int >= 2:
            mid_index = (upper_index + lower_index + 1) // 2
            if mid_index >= upper_index:
                mid_int = (upper_int + lower_int) // 2
                log_coeff = math.log(upper_load) - math.log(lower_load)
                log_coeff *= (mid_int - lower_int) / (upper_int - lower_int)
                mid_load = lower_load * math.exp(log_coeff)
                self._int2load.insert(mid_index, (mid_int, mid_load))
                upper_index += 1
            mid_int, mid_load = self._int2load[mid_index]
            if mid_load < float_load:
                lower_index, lower_int, lower_load = mid_index, mid_int, mid_load
                continue
            if mid_load > float_load:
                upper_index, upper_int, upper_load = mid_index, mid_int, mid_load
                continue
            return mid_load
        # Rounding is needed.
        is_big = float_load * float_load > lower_load * upper_load
        return upper_int if is_big else lower_int
