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

"""Module defining SearchGoalTuple class."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Tuple

from .search_goal import SearchGoal


@dataclass(frozen=True)
class SearchGoalTuple:
    """Container class holding multiple search goals.

    Just a convenience for checking their number and types.
    """

    goals: Tuple[SearchGoal, ...]
    """Goals extracted from user-provided Iterable of search goals."""

    def __post_init__(self) -> None:
        """Check type and number of search goals.

        :raises ValueError: If there are no goals.
        :raises TypeError: If a goal is not a SearchGoal.
        """
        super().__setattr__("goals", tuple(self.goals))
        if not self.goals:
            raise ValueError(f"Cannot be empty: {self.goals}")
        for goal in self.goals:
            if not isinstance(goal, SearchGoal):
                raise TypeError(f"Must be a SearchGoal instance: {goal}")
        copied = list(self.goals)
        deduplicated = set(self.goals)
        for goal in copied:
            if goal not in deduplicated:
                raise ValueError(f"Duplicate goal: {goal}")
            deduplicated.remove(goal)
        if deduplicated:
            raise ValueError(f"Error processing goals: {deduplicated}")

    def __iter__(self) -> Iterator[SearchGoal]:
        """Enable itertion over goals.

        :returns: Iterator iteratinc over contained goals.
        :rtype: Iterator[SearchGoal]
        """
        return iter(self.goals)
