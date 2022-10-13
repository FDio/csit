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

"""Module defining LoadStat class."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import List

from .criteria import Criteria
from .discrete_load import DiscreteLoad
from .trial_measurement.measurement_result import MeasurementResult


@dataclass
class LoadStat(DiscreteLoad):
    """FIXME."""

    loss_ratios: List[float]
    good_counts: List[int] = None
    bad_counts: List[int] = None
    all_duration: float = 0.0
    all_count: int = field(init=False, repr=False)
    duration_per_trial: float = field(init=False, repr=False, default=None)

    def __post_init__(self):
        """FIXME"""
        super().__post_init__()
        if not self.good_counts:
            self.good_counts = [0 for ratio in self.loss_ratios]
        if not self.bad_counts:
            self.bad_counts = [0 for ratio in self.loss_ratios]
        good_count = sum(self.good_counts)
        bad_count = sum(self.bad_counts)
        self.all_count = (good_count + bad_count) // len(self.loss_ratios)
        if self.all_count:
            self.duration_per_trial = self.all_duration / self.all_count
        for index, ratio in enumerate(self.loss_ratios):
            good_count = self.good_counts[index]
            bad_count = self.bad_counts[index]
            if good_count + bad_count != self.all_count:
                raise RuntimeError(f"Unbalanced counts: {self}")

    def add(self, measurement: MeasurementResult) -> None:
        """FIXME"""
        if measurement.intended_load != float(self):
            raise RuntimeError(
                f"Attempting to add load {measurement.intended_load}"
                f" to result set for {float(self)}"
            )
        for index, loss_ratio in enumerate(self.loss_ratios):
            if measurement.loss_ratio > loss_ratio:
                self.bad_counts[index] += 1
            else:
                self.good_counts[index] += 1
        self.all_count += 1
        self.all_duration += measurement.offered_duration
        self.duration_per_trial = self.all_duration / self.all_count

    def satisfies(self, criterion, duration_final):
        """FIXME"""
        final_count = int(ceil(duration_final / self.duration_per_trial))
        final_count = max(final_count, self.all_count)
        index = self.loss_ratios.index(criterion.loss_ratio)
        good_count = self.good_counts[index]
        bad_count = self.bad_counts[index]
        percentage = criterion.bad_ratio
        optimistic = (bad_count / final_count) <= percentage
        pessimistic = ((final_count - good_count) / final_count) <= percentage
        return optimistic, pessimistic

    @staticmethod
    def new_empty(discrete_load: DiscreteLoad, criteria: Criteria) -> LoadStat:
        """FIXME"""
        if not discrete_load.is_round:
            raise ValueError(f"LoadStat needs round: {discrete_load}")
        return LoadStat(
            rounding=discrete_load.rounding,
            float_load=float(discrete_load),
            int_load=int(discrete_load),
            loss_ratios=criteria.loss_ratios,
        )
