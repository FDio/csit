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

"""Module defining LoadStat class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from .target_spec import TargetSpec
from .target_stat import TargetStat
from .discrete_load import DiscreteLoad
from .trial_measurement import MeasurementResult


@dataclass
class LoadStats(DiscreteLoad):
    """An offered load together with stats for all active targets."""

    target_to_stat: Dict[TargetSpec, TargetStat] = None
    """Mapping from target specification to its current stats for this load."""

    def __post_init__(self):
        """Initialize load value and check there are targets to track."""
        super().__post_init__()
        if not self.target_to_stat:
            raise ValueError(f"No targets: {self.target_to_stat!r}")

    def __str__(self):
        """Convert into a short human-readable string.

        This works well only for trimmed stats,
        as only the stat for the first target present is shown.

        :returns: The short string.
        :rtype: str
        """
        return (
            f"fl={self.float_load}"
            f",s=({next(iter(self.target_to_stat.values()))})"
        )

    def add(self, measurement: MeasurementResult) -> None:
        """Take into account one more trial measurement result.

        :param measurement: The result to take into account.
        :type measurement: MeasurementResult
        """
        if measurement.intended_load != float(self):
            raise RuntimeError(
                f"Attempting to add load {measurement.intended_load}"
                f" to result set for {float(self)}"
            )
        for stat in self.target_to_stat.values():
            stat.add(measurement)

    @staticmethod
    def new_empty(load: DiscreteLoad, targets: Tuple[TargetSpec]) -> LoadStats:
        """Factory method to initialize mapping for given targets.

        :param load: The intended load value for the new instance.
        :param targets: The target specifications to track stats for.
        :type load: DiscreteLoad
        :type targets: Tuple[TargetSpec]
        :returns: New instance with empty stats initialized.
        :rtype: LoadStats
        :raise ValueError: Is the load is not rounded.
        """
        if not load.is_round:
            raise ValueError(f"Not round: {load!r}")
        return LoadStats(
            rounding=load.rounding,
            int_load=int(load),
            target_to_stat={target: TargetStat(target) for target in targets},
        )

    def estimates(self, target: TargetSpec) -> Tuple[bool, bool]:
        """Classify this load according to given target.

        :param target: According to which target this should be classified.
        :type target: TargetSpec
        :returns: Tuple of two estimates whether load can be lower bound.
            (True, False) means target is not reached yet.
        :rtype: Tuple[bool, bool]
        """
        return self.target_to_stat[target].estimates()

    def trimmed_to_target(self, target: TargetSpec) -> LoadStats:
        """Return new instance with only one target in the mapping.

        This is useful for debugging and for constructing MLRsearch output.

        :param target: The one target which should remain in the mapping.
        :type target: TargetSpec
        :return: Newly created instance.
        :rtype: LoadStats
        """
        return LoadStats(
            rounding=self.rounding,
            int_load=self.int_load,
            target_to_stat={target: self.target_to_stat[target]},
        )
