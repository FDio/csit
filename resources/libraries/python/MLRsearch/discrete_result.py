# Copyright (c) 2025 Cisco and/or its affiliates.
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

"""Module defining DiscreteResult class."""

from __future__ import annotations

from dataclasses import dataclass

from .discrete_load import DiscreteLoad
from .trial_measurement import MeasurementResult


@dataclass
class DiscreteResult(MeasurementResult):
    """A measurement result where intended load is also given as discrete load.

    The discrete load has to be round and has to match the intended load.
    """

    # Must have default as superclass has fields with default values.
    discrete_load: DiscreteLoad = None
    """Intended load [tps]; discrete, round and equal to intended load."""

    def __post_init__(self) -> None:
        """Call super, verify intended and discrete loads are the same.

        :raises TypeError: If discrete load is not DiscreteLoad.
        :raises ValueError: If the discrete load is not round.
        :raises ValueError: If the load does not match intended load.
        """
        super().__post_init__()
        if not isinstance(self.discrete_load, DiscreteLoad):
            raise TypeError(f"Not a discrete load: {self.discrete_load!r}")
        if not self.discrete_load.is_round:
            raise ValueError(f"Discrete load not round: {self.discrete_load!r}")
        if float(self.discrete_load) != self.intended_load:
            raise ValueError(f"Load mismatch: {self!r}")

    @staticmethod
    def with_load(
        result: MeasurementResult, load: DiscreteLoad
    ) -> DiscreteResult:
        """Return result with added load.

        :param result: A result, possibly without discrete load.
        :param load: Discrete load to add.
        :type result: MeasurementResult
        :type load: DiscreteLoad
        :returns: Equivalent result with matching discrete load.
        :rtype: DiscreteResult
        :raises TypeError: If discrete load is not DiscreteLoad.
        :raises ValueError: If the discrete load is not round.
        :raises ValueError: If the load does not match intended load.
        """
        return DiscreteResult(
            intended_duration=result.intended_duration,
            intended_load=result.intended_load,
            offered_count=result.offered_count,
            loss_count=result.loss_count,
            forwarded_count=result.forwarded_count,
            offered_duration=result.offered_duration,
            duration_with_overheads=result.duration_with_overheads,
            intended_count=result.intended_count,
            discrete_load=load,
        )
