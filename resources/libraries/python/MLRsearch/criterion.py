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

"""Module defining Criterion class."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, eq=True)
class Criterion:
    """FIXME."""

    loss_ratio: float = field(default=0.0)
    """FIXME."""
    exceed_ratio: float = field(default=0.5)
    """FIXME."""
    relative_width: float = field(default=0.005)
    """FIXME."""
    single_duration_min: float = field(default=1.0)
    """FIXME."""
    single_duration_max: float = field(default=5.0)
    """FIXME."""
    sum_duration_min: float = field(default=61.0)
    """FIXME."""
    intermediate_phases: int = field(default=2)
    """Number of intermediate phases to perform before the final phase."""
    expansion_coefficient: int = field(default=4)
    """External search multiplies width (in logarithmic space) by this."""

    def __post_init__(self):
        """FIXME"""
        super().__setattr__("loss_ratio", float(self.loss_ratio))
        super().__setattr__("exceed_ratio", float(self.exceed_ratio))
        super().__setattr__("relative_width", float(self.relative_width))
        super().__setattr__(
            "single_duration_max", float(self.single_duration_max)
        )
        super().__setattr__(
            "single_duration_min", float(self.single_duration_min)
        )
        super().__setattr__("sum_duration_min", float(self.sum_duration_min))
        super().__setattr__(
            "intermediate_phases", int(self.intermediate_phases)
        )
        super().__setattr__(
            "expansion_coefficient", int(self.expansion_coefficient)
        )
        self.validate()

    def validate(self):
        """FIXME"""
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
        if self.single_duration_min <= 0.0:
            raise ValueError(f"Single duration min must be positive: {self}")
        if self.single_duration_max < self.single_duration_min:
            raise ValueError(
                f"Single duration max must be at least min: {self}"
            )
        if self.sum_duration_min < self.single_duration_max:
            raise ValueError(
                f"Sum duration min must be at least single max: {self}"
            )
        if self.expansion_coefficient <= 1:
            raise ValueError(f"Expansion coefficient is too small: {self}")
        too_small = False
        if self.intermediate_phases < 0:
            too_small = True
        elif self.intermediate_phases < 1:
            if self.single_duration_min < self.sum_duration_min:
                too_small = True
        if too_small:
            raise ValueError(f"Number of intermediate phases too small: {self}")
