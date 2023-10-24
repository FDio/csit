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

"""Module defining GoalResult class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .discrete_load import DiscreteLoad
from .relevant_bounds import RelevantBounds
from .trimmed_load import TrimmedLoad

@dataclass
class GoalResult:
    """Composite to be mapped for each search goal at the end of the search.

    The values are stored as trimmed stats,
    the conditional throughput is returned as a discrete loads.
    Thus, users interested only in float values have to convert explicitly.

    Irregular goal results are supported as instances with a bound missing.
    """

    relevant_lower_bound: Optional[DiscreteLoad]
    """The relevant lower bound for the search goal."""
    relevant_upper_bound: Optional[DiscreteLoad]
    """The relevant lower upper for the search goal."""

    @staticmethod
    def from_bounds(bounds: RelevantBounds) -> GoalResult:
        """Factory, so that the call site can be shorter.

        :param bounds: The relevant bounds as found in measurement database.
        :type bounds: RelevantBounds
        :returns: Newly created instance based on the bounds.
        :rtype: GoalResult
        """
        return GoalResult(
            relevant_lower_bound = bounds.clo,
            relevant_upper_bound = bounds.chi,
        )

    @property
    def conditional_throughput(self) -> Optional[DiscreteLoad]:
        """Compute conditional throughput from the relevant lower bound.

        If the relevant lower bound is missing, None is returned.

        The conditional throughput has the same semantics as load,
        so if load is unidirectional and user wants bidirectional
        throughput, the manager has to compensate.

        :return: Conditional throughput at the relevant lower bound.
        :rtype: Optional[DiscreteLoad]
        """
        if not (rlb := self.relevant_lower_bound):
            return None
        loss_ratio = next(rlb.target_to_stat.values()).pessimistic_loss_ratio
        return rlb * (1.0 - loss_ratio)
