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
from typing import Dict, Tuple

from .target_spec import TargetSpec
from .discrete_result import DiscreteResult


@dataclass
class TargetStat:
    """Class for aggregating trial results for a single load and target.

    Reference to the target is included for convenience.

    The main usage is for load classification, done in estimates method.
    If both estimates agree, the load is classified as either a lower bound
    or an upper bound. For additional logic for dealing with loss inversion
    see MeasurementDatabase.

    Also, data needed for conditional throughput is gathered here,
    exposed only as a pessimistic loss ratio
    (as the load value is not stored here).
    """

    target: TargetSpec = field(repr=False)
    """The target for which this instance is aggregating results."""
    good_long: float = 0.0
    """Sum of durations of long enough trials satisfying target loss ratio."""
    bad_long: float = 0.0
    """Sum of durations of long trials not satisfying target loss ratio."""
    good_short: float = 0.0
    """Sum of durations of shorter trials satisfying target loss ratio."""
    bad_short: float = 0.0
    """Sum of durations of shorter trials not satisfying target loss ratio."""
    long_losses: Dict[float, float] = field(repr=False, default_factory=dict)
    """If a loss ratio value occured in a long trial, map it to duration sum."""

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
        dwo = result.duration_with_overheads
        rlr = result.loss_ratio
        if result.intended_duration >= self.target.trial_duration:
            if rlr not in self.long_losses:
                self.long_losses[rlr] = 0.0
                self.long_losses = dict(sorted(self.long_losses.items()))
            self.long_losses[rlr] += dwo
            if rlr > self.target.loss_ratio:
                self.bad_long += dwo
            else:
                self.good_long += dwo
        else:
            if rlr > self.target.loss_ratio:
                self.bad_short += dwo
            else:
                self.good_short += dwo

    def estimates(self) -> Tuple[bool, bool]:
        """Return whether this load can become a lower bound.

        This returns two estimates, hence the weird nonverb name of this method.
        One estimate assumes all following results will satisfy the loss ratio,
        the other assumes all results will not satisfy the loss ratio.
        The sum of durations of the assumed results
        is the minimum to reach target duration sum, or zero if already reached.

        If both estimates are the same, it means the load is a definite bound.
        This may happen even when the sum of durations of already
        measured trials is less than the target, when the missing measurements
        cannot change the classification.

        :returns: Tuple of two estimates whether the load can be a lower bound.
            (True, False) means more trial results are needed.
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

    @property
    def pessimistic_loss_ratio(self) -> float:
        """Return the loss ratio for conditional throughput computation.

        It adds missing dursum as full-loss trials to long_losses
        and returns a quantile corresponding to exceed ratio.
        In case of tie (as in median for even number of samples),
        this returns the lower value (as being equal to goal exceed ratio
        is allowed).

        For loads classified as a lower bound, the return value
        ends up being no larger than the target loss ratio.
        This is because the excess short bad trials would only come
        after the quantile in question (as would full-loss missing trials).
        For other loads, anything can happen, but conditional throughput
        should not be computed for those anyway.
        Those two facts allow the logic here be simpler than in estimates().

        :returns: Effective loss ratio based on long trial results.
        :rtype: float
        """
        all_long = max(self.target.duration_sum, self.good_long + self.bad_long)
        remaining = all_long * (1.0 - self.target.exceed_ratio)
        ret = None
        for ratio, dursum in self.long_losses.items():
            if ret is None or remaining > 0.0:
                ret = ratio
                remaining -= dursum
            else:
                break
        else:
            if remaining > 0.0:
                ret = 1.0
        return ret
