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

"""Module defining TargetScaling class."""

from dataclasses import dataclass, field
from typing import Dict, Tuple

from .discrete_width import DiscreteWidth
from .load_rounding import LoadRounding
from .search_goal import SearchGoal
from .search_goal_tuple import SearchGoalTuple
from .target_spec import TargetSpec


@dataclass
class TargetScaling:
    """Encapsulate targets derived from goals.

    No default values for primaries, contructor call has to specify everything.
    """

    goals: SearchGoalTuple
    """Set of goals to generate targets for."""
    rounding: LoadRounding
    """Rounding instance to use (targets have discrete width)."""
    # Derived quantities.
    targets: Tuple[TargetSpec] = field(repr=False, init=False)
    """The generated targets, linked into chains."""
    goal_to_final_target: Dict[SearchGoal, TargetSpec] = field(
        repr=False, init=False
    )
    """Mapping from a goal to its corresponding final target."""

    def __post_init__(self) -> None:
        """For each goal create final, and non-final targets and link them."""
        linked_targets = []
        self.goal_to_final_target = {}
        for goal in self.goals:
            standalone_targets = []
            # Final target.
            width = DiscreteWidth(
                rounding=self.rounding,
                float_width=goal.relative_width,
            ).rounded_down()
            duration_sum = goal.duration_sum
            target = TargetSpec(
                loss_ratio=goal.loss_ratio,
                exceed_ratio=goal.exceed_ratio,
                discrete_width=width,
                trial_duration=goal.final_trial_duration,
                duration_sum=duration_sum,
                expansion_coefficient=goal.expansion_coefficient,
                preceding=None,
            )
            standalone_targets.append(target)
            # Non-final targets.
            preceding_targets = goal.preceding_targets
            multiplier = (
                pow(
                    goal.initial_trial_duration / duration_sum,
                    1.0 / preceding_targets,
                )
                if preceding_targets
                else 1.0
            )
            for count in range(preceding_targets):
                preceding_sum = duration_sum * pow(multiplier, count + 1)
                if count + 1 >= preceding_targets:
                    preceding_sum = goal.initial_trial_duration
                trial_duration = min(goal.final_trial_duration, preceding_sum)
                width *= 2
                target = TargetSpec(
                    loss_ratio=goal.loss_ratio,
                    exceed_ratio=goal.exceed_ratio,
                    discrete_width=width,
                    trial_duration=trial_duration,
                    duration_sum=preceding_sum,
                    expansion_coefficient=goal.expansion_coefficient,
                    preceding=None,
                )
                standalone_targets.append(target)
            # Link preceding targets.
            per_goal_targets = []
            preceding_target = None
            for target in reversed(standalone_targets):
                linked_target = target.with_preceding(preceding_target)
                linked_targets.append(linked_target)
                per_goal_targets.append(linked_target)
                preceding_target = linked_target
            # Associate final target to the goal.
            self.goal_to_final_target[goal] = per_goal_targets[-1]
        # Store all targets as a tuple.
        self.targets = tuple(linked_targets)
