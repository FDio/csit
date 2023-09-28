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

"""Module defining SearchGoal class."""

from dataclasses import dataclass, field


@dataclass(frozen=True, eq=True)
class SearchGoal:
    """
    This is the part of controller inputs that can be repeated
    with different values. MLRsearch saves time by searching
    for conditional throughput for each goal at the same time,
    compared to repeated calls with separate goals.

    Most fields (called attributes) of this composite
    are relevant to the definition of conditional throughput.
    The rest does not, but can affect the overal search time.

    TODO: Move larger explanations here, keep field descriptions brief?
    """

    loss_ratio: float = 0.0
    """The loss ratio goal.
    A trial can satisfy the goal only when its trial loss ratio is not higher
    than this. See MeasurementResult.loss_ratio for details.
    A trial that does not satisfy this goal is called a bad trial."""
    exceed_ratio: float = 0.5
    """What portion of the duration sum can consist of bad trial seconds
    while still being classified as lower bound (assuming no short trials)."""
    relative_width: float = 0.005
    """Target is achieved when the tightest lower bound
    is no more than this far from the tightest upper bound
    (in units of the tightest upper bound)."""
    initial_trial_duration: float = 1.0
    """Shortest trial duration employed when searching for this goal."""
    final_trial_duration: float = 5.0
    """Longest trial duration employed when searching for this goal."""
    duration_sum: float = 61.0
    """Minimal sum of durations of relevant trials needed to declare a load
    to be upper or lower bound for this goal."""
    preceding_targets: int = 2
    """Number of increasingly coarser search targets to insert,
    hoping to speed up searching for the final target of this goal."""
    expansion_coefficient: int = 4
    """External search multiplies width (in logarithmic space) by this."""

    def __post_init__(self):
        """Convert fields to correct types and call validate."""
        super().__setattr__("loss_ratio", float(self.loss_ratio))
        super().__setattr__("exceed_ratio", float(self.exceed_ratio))
        super().__setattr__("relative_width", float(self.relative_width))
        super().__setattr__(
            "final_trial_duration", float(self.final_trial_duration)
        )
        super().__setattr__(
            "initial_trial_duration", float(self.initial_trial_duration)
        )
        super().__setattr__("duration_sum", float(self.duration_sum))
        super().__setattr__("preceding_targets", int(self.preceding_targets))
        super().__setattr__(
            "expansion_coefficient", int(self.expansion_coefficient)
        )
        self.validate()

    def validate(self):
        """Raise value error if a field value is outside allowed bounds."""
        if self.loss_ratio < 0.0:
            raise ValueError(f"Loss ratio cannot be negative: {self}")
        if self.loss_ratio >= 1.0:
            raise ValueError(f"Loss ratio must be lower than 1: {self}")
        if self.exceed_ratio < 0.0:
            raise ValueError(f"Exceed ratio cannot be negative: {self}")
        if self.exceed_ratio >= 1.0:
            raise ValueError(f"Exceed ratio must be lower than 1: {self}")
        if self.relative_width <= 0.0:
            raise ValueError(f"Relative width must be positive: {self}")
        if self.relative_width >= 1.0:
            raise ValueError(f"Relative width must be less than 1: {self}")
        if self.initial_trial_duration <= 0.0:
            raise ValueError(f"Initial trial duration must be positive: {self}")
        if self.final_trial_duration < self.initial_trial_duration:
            raise ValueError(
                f"Single duration max must be at least initial: {self}"
            )
        if self.duration_sum < self.final_trial_duration:
            raise ValueError(
                "Min duration sum cannot be smaller"
                f" than final trial duration: {self}"
            )
        if self.expansion_coefficient <= 1:
            raise ValueError(f"Expansion coefficient is too small: {self}")
        too_small = False
        if self.preceding_targets < 0:
            too_small = True
        elif self.preceding_targets < 1:
            if self.initial_trial_duration < self.duration_sum:
                too_small = True
        if too_small:
            raise ValueError(
                f"Number of preceding targets is too small: {self}"
            )
