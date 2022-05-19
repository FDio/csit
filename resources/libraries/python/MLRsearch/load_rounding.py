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

"""Module defining LoadRounding class."""

from dataclasses import dataclass, field
from typing import List

from .base_load_rounding import BaseLoadRounding
from .discrete_width import DiscreteWidth


@dataclass
class LoadRounding(BaseLoadRounding):
    """BaseLoadRounding with additional discrete_golas field.
    """

    discrete_goals: List[DiscreteWidth] = field(init=False, repr=False)
    """Discrete dorm og int_goals."""

    def __post_init__(self) -> None:
        """Ensure types, perform checks, initialize conversion structures.

        :raises RuntimeError: If a requirement is not met.
        """
        super().__post_init__()
        self.discrete_goals = list()
        for int_goal in self.int_goals:
            discrete_goal = DiscreteWidth(rounding=self, int_width=int_goal)
            self.discrete_goals.append(discrete_goal)
