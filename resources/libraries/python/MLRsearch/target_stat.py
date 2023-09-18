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

from dataclasses import dataclass, field

from .target_spec import TargetSpec
from .discrete_result import DiscreteResult


@dataclass
class TargetStat:
    """Class for aggregating trial results for a single load and target."""

    target: TargetSpec = field(repr=False)
    # Cannot be non-default due to parent.
    """The target for which this instance is aggregating results."""
    good_long: float = 0.0
    """Sum of durations of long enough trials satisfying target loss ratio."""
    bad_long: float = 0.0
    """Sum of durations of long trials not satisfying target loss ratio."""
    good_short: float = 0.0
    """Sum of durations of shorter trials satisfying target loss ratio."""
    bad_short: float = 0.0
    """Sum of durations of shorter trials not satisfying target loss ratio."""

    def __str__(self) -> str:
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return (
            f"gl={self.good_long},bl={self.bad_long}"
            f",gs={self.good_short},bs={self.bad_short}"
        )

    def add(self, result: DiscreteResult) -> None:
        """Take into account one more trial result.

        Use intended duration for deciding between long and short trials,
        but use offered duation (with overheads) to increase the duration sums.

        :param result: The trial result to add to the stats.
        :type result: DiscreteResult
        """
        if result.intended_duration >= self.target.trial_duration:
            if result.loss_ratio > self.target.loss_ratio:
                self.bad_long += result.duration_with_overheads
            else:
                self.good_long += result.duration_with_overheads
        else:
            if result.loss_ratio > self.target.loss_ratio:
                self.bad_short += result.duration_with_overheads
            else:
                self.good_short += result.duration_with_overheads

    def estimates(self):
        """Return whether this load can become a lower bound.

        This return two estimates, one assumes all following results
        will satisfy the loss ratio, the other assumes all results
        will not satisfy the loss ratio. The sum of durations
        of the assumed results is the minimum to reach target duration sum.

        If both estimates are the same, it means the load is a definite bound.
        This may happen even when the sum of durations of already
        measured trials is less than the target, when the missing measurements
        cannot change the classification.

        :returns: Tuple of two estimates whether load can be lower bound.
            (True, False) means target is not reached yet.
        :rtype: Tuple[bool, bool]
        """
        coeff = self.target.exceed_ratio
        decrease = self.good_short * coeff / (1.0 - coeff)
        short_excess = self.bad_short - decrease
        effective_excess = self.bad_long + max(0.0, short_excess)
        effective_dursum = max(
            self.good_long + effective_excess,
            self.target.duration_sum,
        )
        limit_dursum = effective_dursum * self.target.exceed_ratio
        optimistic = effective_excess <= limit_dursum
        pessimistic = (effective_dursum - self.good_long) <= limit_dursum
        return optimistic, pessimistic
