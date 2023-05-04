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
from typing import Dict, Tuple

from .target_spec import TargetSpec
from .target_stat import TargetStat
from .discrete_load import DiscreteLoad
from .trial_measurement.measurement_result import MeasurementResult


@dataclass
class LoadStats(DiscreteLoad):
    """FIXME."""

    spec_to_stat: Dict[TargetSpec, TargetStat] = None
    """FIXME"""

    def __post_init__(self):
        """FIXME"""
        super().__post_init__()
        if not self.spec_to_stat:
            raise ValueError(f"No specs: {self.spec_to_stat!r}")

    def __str__(self):
        """FIXME"""
        return f"fl={self.float_load},s=({next(iter(self.spec_to_stat.values()))})"

    def add(self, measurement: MeasurementResult) -> None:
        """FIXME"""
        if measurement.intended_load != float(self):
            raise RuntimeError(
                f"Attempting to add load {measurement.intended_load}"
                f" to result set for {float(self)}"
            )
        for stat in self.spec_to_stat.values():
            stat.add(measurement)

    @staticmethod
    def new_empty(load: DiscreteLoad, specs: Tuple[TargetSpec]) -> LoadStats:
        """FIXME"""
        if not load.is_round:
            raise ValueError(f"Not round: {load!r}")
        return LoadStats(
            rounding=load.rounding,
            int_load=int(load),
            spec_to_stat={target: TargetStat(target) for target in specs},
        )

    def satisfied(self, target_spec: TargetSpec) -> Tuple[bool, bool]:
        """FIXME"""
        return self.spec_to_stat[target_spec].satisfied()

    def trimmed_to_spec(self, target_spec: TargetSpec) -> LoadStats:
        """FIXME"""
        return LoadStats(
            rounding=self.rounding,
            int_load=self.int_load,
            spec_to_stat={target_spec: self.spec_to_stat[target_spec]},
        )
