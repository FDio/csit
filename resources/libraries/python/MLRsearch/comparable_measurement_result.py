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

"""Module defining ComparableMeasurementResult class."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import total_ordering
from typing import Optional

from .discrete_load import DiscreteLoad
from .trial_measurement.measurement_result import MeasurementResult


@total_ordering
@dataclass()  # Not using order=True since operations are overridden.
class ComparableMeasurementResult(MeasurementResult):
    """Adding MLRsearch specific comparisons to MeasurementResult.

    Only intended duration and intended load are considered for comparison,
    as MLRsearch should never repeat a trial with the same values.

    Two more fields are added, they are used to hide "incompatible" results,
    e.g. situations where higher load has lower loss rate.

    Overridden loss ratios are to be set before effective ones.
    For details, see normalization in MeasurementDatabase.

    As a convenience, DiscreteLoad form of intended load is also stored,
    to force consistency checks, and there is a factory
    to simplify converting from MeasurementResult.
    """
    # TODO: Allow comparison with DiscreteLoad?

    discrete_load: DiscreteLoad = None
    """Integer form of intended load, the associated rounding is not stored."""
    effective_loss_ratio: float = None
    """Set to a higher value when any lower load has higher overridden loss."""
    overridden_loss_ratio: float = None
    """Set to a lower value when higher duration higher load has lower loss."""
    original_result: Optional[MeasurementResult] = field(
        default=None, repr=False
    )
    """Some measurers contain additional data (e.g. latency).
    This is a way to store them without knowing them (nor assuming deepcopy
    would work correctly)."""

    def __post_init__(self) -> None:
        """Replace None (if present) with the measured loss ratio.

        :raises RuntimeError: If an internal inconsistency is detected.
        """
        super().__post_init__()
        if self.overridden_loss_ratio is None:
            self.overridden_loss_ratio = self.loss_ratio
        if self.effective_loss_ratio is None:
            self.effective_loss_ratio = self.overridden_loss_ratio
        # TODO: Add other checks around discrete load value (type)?
        # The fully correct approach would require setters.
        if not self.discrete_load.is_round:
            raise RuntimeError(f"Load has to be round: {self.discrete_load!r}")
        if self.intended_load != float(self.discrete_load):
            raise RuntimeError(f"Loads do not match: {self.discrete_load}")

    def __eq__(self, other: Optional[ComparableMeasurementResult]) -> bool:
        """Return whether the argument is equivalent to self.

        Types are not compared, so comparisons with subclasses
        may give surprising results.
        The only exception to that rule is None,
        treated as a missing (hence unequal) measurement.

        Other is equal if it has the two primary quantities equal.

        :param other: Other result to compare with.
        :type other: Optional[ComparableMeasurementResult]
        :returns: True if the two primary values are equal.
        :rtype: bool
        """
        return (
            other is not None
            and self.intended_duration == other.intended_duration
            and self.intended_load == other.intended_load
        )

    def __lt__(self, other: ComparableMeasurementResult) -> bool:
        """Return whether self is less than the argument.

        Types are not compared, so comparisons with subclasses
        may give surprising results.
        For the order of comparisons, it is important intended_load is the most
        relevant quantity (duration is the second most relevant).

        If the two quatities are equal, an exception is raised,
        as this means there is an internal error in MLRsearch algorithm.

        :param other: Other result to compare with.
        :type other: ComparableMeasurementResult
        :returns: True if self is considered smaller.
        :rtype: bool
        :raises RuntimeError: If intended_load and duration are not enough.
        """
        if self.intended_load < other.intended_load:
            return True
        if self.intended_load > other.intended_load:
            return False
        if self.intended_duration < other.intended_duration:
            return True
        if self.intended_duration > other.intended_duration:
            return False
        raise RuntimeError(u"Load or duration should differ.")

    @staticmethod
    def construct(
        result: MeasurementResult, discrete_load: DiscreteLoad
    ) -> ComparableMeasurementResult:
        """Factory that gets data from existing (maybe not comparable) result.

        Consistency between loads is checked in constructor.
        Original (argument) reference is also stored,
        so users can access any additional info there.

        :param result: Instanace to copy values from.
        :param discrete_load: Discrete form of load, MLR caller knows it.
        :type result: MeasurementResult
        :type discrete_load: DiscreteLoad
        :return: The copy of argument result, but in comparable class.
        :rtype: ComparableMeasurementResult
        :raises RuntimeError: If intended load and discrete load do not match.
        """
        return ComparableMeasurementResult(
            intended_duration=result.intended_duration,
            intended_load=result.intended_load,
            offered_count=result.offered_count,
            loss_count=result.loss_count,
            forwarding_count=result.forwarding_count,
            discrete_load=discrete_load,
            offered_duration=result.offered_duration,
            intended_count=result.intended_count,
            original_result=result,
        )
