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

from dataclasses import dataclass, field
from math import ceil


@dataclass(frozen=True, eq=True, order=True)
class Criterion:
    """FIXME."""

    loss_ratio: float = 0.0
    """FIXME."""
    bad_ratio: float = 0.5
    """FIXME."""
    relative_width: float = field(compare=False, default=0.005)
    """FIXME."""
    trials_duration: float = field(compare=False, default=61.0)
    """FIXME."""
    intermediate_phases: int = field(compare=False, default=2)
    """Number of intermediate phases to perform before the final phase."""
    expansion_coefficient: int = field(compare=False, default=4)
    """External search multiplies width (in logarithmic space) by this."""

    def __post_init__(self):
        """FIXME"""
        super().__setattr__("loss_ratio", float(self.loss_ratio))
        super().__setattr__("bad_ratio", float(self.bad_ratio))
        super().__setattr__("relative_width", float(self.relative_width))
        super().__setattr__(
            "self.trials_duration", int(ceil(float(self.trials_duration)))
        )
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
        if self.bad_ratio < 0.0:
            raise ValueError(f"Bad ratio cannot be negative: {self}")
        if self.bad_ratio >= 1.0:
            raise ValueError(f"Bad ratio must be lower than 1: {self}")
        if self.relative_width <= 0.0:
            raise ValueError(f"Relative width must be positive: {self}")
        if self.relative_width >= 1.0:
            raise ValueError(f"Relative width must be less than 1: {self}")
        if self.trials_duration < 1:
            raise ValueError(f"Trial count must be at least 1: {self}")
        if self.expansion_coefficient < 1:
            raise ValueError(f"Expansion coefficient is too small: {self}")
        too_small = False
        if self.intermediate_phases < 0:
            too_small = True
        elif self.intermediate_phases < 1:
            if 1 != self.trials_duration:
                too_small = True
        if too_small:
            raise ValueError(f"Number of intermediate phases too small: {self}")
