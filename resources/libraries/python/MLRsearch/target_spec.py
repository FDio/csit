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

"""Module defining TargetSpec class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .discrete_width import DiscreteWidth


@dataclass(frozen=True, eq=True)
class TargetSpec:
    """Composite object holding attributes specifying one search target.

    Abstractly, this has several similar meanings.
    With discrete_width attribute this specifies when a selector is Done.
    With expansion_coefficient attribute is tells selector how quickly
    should it expand interval in external search.
    With "preceding" attribute it helps selector, so it does not need to point
    to preceding target separately from its current target.
    Without those three attributes this object is still sufficient
    for LoadStats to classify loads as lower bound, upper bound, or unknown.
    """

    loss_ratio: float
    """Target loss ratio. Equal and directly analogous to goal loss ratio,
    but applicable also for non-final targets."""
    exceed_ratio: float
    """Target exceed ratio. Equal and directly analogous to goal exceed ratio,
    but applicable also for non-final targets."""
    discrete_width: DiscreteWidth
    """Target relative width. Analogous to goal relative width,
    but coarser for non-final targets."""
    trial_duration: float
    """Duration to use for trials for this target. Shorter trials may not count
    when determining upper and lower bounds."""
    duration_sum: float
    """Sum of trial durations sufficient to classify a load
    as an upper or lower bound.
    For non-final targets, this is shorter than goal duration_sum."""
    expansion_coefficient: int = field(repr=False)
    """Equal and directly analogous to goal expansion coefficient,
    but applicable also for non-final targets."""
    fail_fast: bool = False
    """Copied from goal. If true and min load is not an upper bound, raise."""
    preceding: Optional[TargetSpec] = field(repr=False)
    """Reference to next coarser target (if any) belonging to the same goal."""

    # No conversions or validations, as this is an internal structure.

    def __str__(self) -> str:
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return (
            f"lr={self.loss_ratio},er={self.exceed_ratio}"
            f",ds={self.duration_sum}"
        )

    def with_preceding(self, preceding: Optional[TargetSpec]) -> TargetSpec:
        """Create an equivalent instance but with different preceding field.

        This is useful in initialization. Create semi-initialized targets
        starting from final one, than add references in reversed order.

        :param preceding: New value for preceding field, cannot be None.
        :type preceding: Optional[TargetSpec]
        :returns: Instance with the new value applied.
        :rtype: TargetSpec
        """
        return TargetSpec(
            loss_ratio=self.loss_ratio,
            exceed_ratio=self.exceed_ratio,
            discrete_width=self.discrete_width,
            trial_duration=self.trial_duration,
            duration_sum=self.duration_sum,
            expansion_coefficient=self.expansion_coefficient,
            fail_fast=self.fail_fast,
            preceding=preceding,
        )
