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

"""Module defining SearchGoalSet class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Set

from .search_goal import SearchGoal


@dataclass(frozen=True)
class SearchGoalSet:
    """Container class holding multiple search goals.

    Just a convenience for checking their number and types.
    """

    goals: Set[SearchGoal]
    """Unordered de-duplicated set of search goals."""

    def __post_init__(self):
        """Check type and number of search goals.

        :raises ValueError: If there are no goals.
        :raises TypeError: If a goal is not a SearchGoal.
        """
        super().__setattr__("goals", set(self.goals))
        if not self.goals:
            raise ValueError(f"Cannot be empty: {self.goals}")
        for goal in self.goals:
            if not isinstance(goal, SearchGoal):
                raise TypeError(f"Must be a SearchGoal instance: {goal}")

    def __iter__(self):
        """Enable itertion over goals."""
        return iter(self.goals)
