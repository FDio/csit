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

"""Module defining Criteria class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .criterion import Criterion


@dataclass(frozen=True)
class Criteria:
    """FIXME."""

    criteria: Tuple[Criterion, ...]
    """FIXME."""
    loss_ratios: Tuple[float, ...] = field(repr=False, init=False)
    """FIXME."""

    def __post_init__(self):
        """FIXME"""
        self.criteria = tuple(self.criteria)  # To support generators.
        criteria = tuple(sorted(set(self.criteria)))
        if not criteria:
            raise ValueError(f"Cannot be empty: {self.criteria}")
        if len(criteria) != len(self.criteria):  # Generators do not have len.
            raise ValueError(f"Duplicate or conflicting: {self.criteria}")
        for index in range(len(criteria) - 1):
            cr0, cr1 = criteria[index], criteria[index + 1]
            not_ok = False
            if cr1.trials_duration > cr0.trials_duration:
                not_ok = True
            if cr1.bad_ratio < cr0.bad_ratio:
                not_ok = True
            if not_ok:
                raise ValueError(f"Unsafe criteria at {index}: {criteria}")
        super().__setattr__("criteria", criteria)
        loss_ratios = (criterion.loss_ratio for criterion in self)
        super().__setattr__("loss_ratios", tuple(sorted(set(loss_ratios))))

    def __iter__(self):
        """FIXME"""
        return iter(self.criteria)
