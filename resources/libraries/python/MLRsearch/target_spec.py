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

"""Module defining TargetSpec class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .discrete_width import DiscreteWidth


@dataclass(frozen=True, eq=True)
class TargetSpec:
    """FIXME."""

    loss_ratio: float
    """FIXME."""
    exceed_ratio: float
    """FIXME."""
    discrete_width: DiscreteWidth
    """FIXME."""
    single_duration_whole: float
    """FIXME."""
    sum_duration_whole: float
    """FIXME."""
    expansion_coefficient: int = field(repr=False)
    """FIXME"""
    coarser: Optional[TargetSpec] = field(repr=False)
    """FIXME."""

    # No conversions or validations as this is internal structure.

    def with_coarser(self, coarser: TargetSpec) -> TargetSpec:
        """FIXME"""
        return TargetSpec(
            loss_ratio=self.loss_ratio,
            exceed_ratio=self.exceed_ratio,
            discrete_width=self.discrete_width,
            single_duration_whole=self.single_duration_whole,
            sum_duration_whole=self.sum_duration_whole,
            expansion_coefficient=self.expansion_coefficient,
            coarser=coarser,
        )
