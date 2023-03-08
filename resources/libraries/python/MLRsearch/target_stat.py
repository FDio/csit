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

from .target_spec import TargetSpec
from .trial_measurement.measurement_result import MeasurementResult


@dataclass
class TargetStat:
    """FIXME."""

    target_spec: TargetSpec = field(repr=False)
    # Cannot be non-default due to parent.
    """FIXME"""
    abide_dursum: float = 0.0
    """FIXME"""
    exceed_dursum: float = 0.0
    """FIXME"""

    def __str__(self) -> str:
        """FIXME"""
        return f"ad={self.abide_dursum},ed={self.exceed_dursum}"

    def add(self, measurement: MeasurementResult) -> None:
        """FIXME"""
        duration = measurement.duration_with_overheads
        if measurement.loss_ratio > self.target_spec.loss_ratio:
            self.exceed_dursum += duration
        else:
            if duration >= self.target_spec.single_duration_whole:
                self.abide_dursum += duration
            # Else it does not count.

    def satisfied(self):
        """FIXME"""
        effective_dursum = max(
            self.abide_dursum + self.exceed_dursum,
            self.target_spec.sum_duration_whole,
        )
        limit_dursum = effective_dursum * self.target_spec.exceed_ratio
        optimistic = self.exceed_dursum <= limit_dursum
        pessimistic = (effective_dursum - self.abide_dursum) <= limit_dursum
        return optimistic, pessimistic
