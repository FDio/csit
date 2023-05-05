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

"""Module defining TargetScaling class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from .criteria import Criteria
from .criterion import Criterion
from .discrete_width import DiscreteWidth
from .load_rounding import LoadRounding
from .target_spec import TargetSpec


@dataclass
class TargetScaling:
    """Encapsulate target specs derived from criteria.

    No default values for primaries, contructor call has to specify everything.
    """

    criteria: Criteria
    """FIXME"""
    rounding: LoadRounding
    """FIXME"""
    # Derived quantities.
    specs: Tuple[TargetSpec] = field(repr=False, init=False)
    """FIXME"""
    criterion_to_spec: Dict[Criterion, TargetSpec] = field(
        repr=False, init=False
    )
    """FIXME"""

    def __post_init__(self) -> None:
        """Ensure correct primary types and compute the secondary quantities.

        :raises RuntimeError: If an unsupported argument value is detected.
        """
        specs = list()
        c2s = dict()
        for criterion in self.criteria:
            sublist = list()
            width = DiscreteWidth(
                rounding=self.rounding,
                float_width=criterion.relative_width,
            ).rounded_down()
            dursum = criterion.sum_duration_min
            spec = self._from_criterion(
                criterion=criterion,
                width=width,
                dursum=dursum,
            )
            sublist.append(spec)
            n_phases = criterion.intermediate_phases
            multiplier = (
                pow(
                    criterion.single_duration_min / dursum,
                    1.0 / n_phases,
                )
                if n_phases
                else 1.0
            )
            for count in range(n_phases):
                subsum = dursum * pow(multiplier, count + 1)
                if count + 1 >= n_phases:
                    subsum = criterion.single_duration_min
                width *= 2
                spec = self._from_criterion(
                    criterion=criterion,
                    width=width,
                    dursum=subsum,
                )
                sublist.append(spec)
            previous = None
            for standalone_spec in reversed(sublist):
                linked_spec = standalone_spec.with_coarser(previous)
                previous = linked_spec
                specs.append(linked_spec)
            c2s[criterion] = specs[-1]
        self.specs = tuple(specs)
        self.criterion_to_spec = c2s

    def _from_criterion(
        self,
        criterion: Criterion,
        width: DiscreteWidth,
        dursum: float,
    ) -> TargetSpec:
        """FIXME"""
        dursing = min(criterion.single_duration_max, dursum)
        return TargetSpec(
            loss_ratio=criterion.loss_ratio,
            exceed_ratio=criterion.exceed_ratio,
            discrete_width=width,
            single_duration_whole=dursing,
            sum_duration_whole=dursum,
            expansion_coefficient=criterion.expansion_coefficient,
            coarser=None,
        )
