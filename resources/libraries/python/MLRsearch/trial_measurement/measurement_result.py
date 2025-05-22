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

"""Module defining MeasurementResult class."""

from dataclasses import dataclass


@dataclass
class MeasurementResult:
    """Structure defining the result of a single trial measurement.

    There are few primary (required) quantities. Various secondary (derived)
    quantities are calculated and can be queried.

    The constructor allows broader argument types,
    the post init function converts to the stricter types.

    Integer quantities (counts) are preferred, as float values
    can suffer from rounding errors, and sometimes they are measured
    at unknown (possibly very limited) precision and accuracy.

    There are relations between the counts (e.g. offered count
    should be equal to a sum of forwarding count and loss count).
    This implementation does not perform consistency checks, but uses them
    for computing quantities the caller left unspecified.

    In some cases, the units of intended load are different from units
    of loss count (e.g. load in transactions but loss in packets).
    Quantities with relative_ prefix can be used to get load candidates
    from forwarding results.

    Sometimes, the measurement provider is unable to reach the intended load,
    and it can react by spending longer than intended duration
    to reach its intended count. To signal irregular situations like this,
    several optional fields can be given, and various secondary quantities
    are populated, so the measurement consumer can query the quantity
    it wants to rely on in these irregular situations.

    The current implementation intentionally limits the secondary quantities
    to the few that proved useful in practice.
    """

    # Required primary quantities.
    intended_duration: float
    """Intended trial measurement duration [s]."""
    intended_load: float
    """Intended load [tps]. If bidirectional (or multi-port) traffic is used,
    most users will put unidirectional (single-port) value here,
    as bandwidth and pps limits are usually per-port."""
    # Two of the next three primary quantities are required.
    offered_count: int = None
    """Number of packets actually transmitted (transactions attempted).
    This should be the aggregate (bidirectional, multi-port) value,
    so that asymmetric trafic profiles are supported."""
    loss_count: int = None
    """Number of packets transmitted but not received (transactions failed)."""
    forwarded_count: int = None
    """Number of packets successfully forwarded (transactions succeeded)."""
    # Optional primary quantities.
    offered_duration: float = None
    """Estimate of the time [s] the trial was actually transmitting traffic."""
    duration_with_overheads: float = None
    """Estimate of the time [s] it took to get the trial result
    since the measurement started."""
    intended_count: int = None
    """Expected number of packets to transmit. If not known,
    the value of offered_count is used."""

    def __post_init__(self) -> None:
        """Convert types, compute missing values.

        Current caveats:
        A failing assumption looks like a conversion error.
        Negative counts are allowed, which can lead to errors later.
        """
        self.intended_duration = float(self.intended_duration)
        if self.offered_duration is None:
            self.offered_duration = self.intended_duration
        else:
            self.offered_duration = float(self.offered_duration)
        if self.duration_with_overheads is None:
            self.duration_with_overheads = self.offered_duration
        else:
            self.duration_with_overheads = float(self.duration_with_overheads)
        self.intended_load = float(self.intended_load)
        if self.forwarded_count is None:
            self.forwarded_count = int(self.offered_count) - int(
                self.loss_count
            )
        else:
            self.forwarded_count = int(self.forwarded_count)
        if self.offered_count is None:
            self.offered_count = self.forwarded_count + int(self.loss_count)
        else:
            self.offered_count = int(self.offered_count)
        if self.loss_count is None:
            self.loss_count = self.offered_count - self.forwarded_count
        else:
            self.loss_count = int(self.loss_count)
        if self.intended_count is None:
            self.intended_count = self.offered_count
        else:
            self.intended_count = int(self.intended_count)
            # TODO: Handle (somehow) situations where offered > intended?

    @property
    def unsent_count(self) -> int:
        """How many packets were not transmitted (transactions not started).

        :return: Intended count minus offered count.
        :rtype: int
        """
        return self.intended_count - self.offered_count

    @property
    def loss_ratio(self) -> float:
        """Bad count divided by overall count, zero if the latter is zero.

        The bad count includes not only loss count, but also unsent count.
        If unsent count is negative, its absolute value is used.
        The overall count is intended count or offered count,
        whichever is bigger.

        Together, the resulting formula tends to increase loss ratio
        (but not above 100%) in irregular situations,
        thus guiding search algorithms towards lower loads
        where there should be less irregularities.
        The zero default is there to prevent search algorithms from
        getting stuck on a too low intended load.

        :returns: Bad count divided by overall count.
        :rtype: float
        """
        overall = max(self.offered_count, self.intended_count)
        bad = abs(self.loss_count) + abs(self.unsent_count)
        return bad / overall if overall else 0.0

    @property
    def relative_forwarding_rate(self) -> float:
        """Forwarding rate in load units as if duration and load was intended.

        The result is based purely on intended load and loss ratio.
        While the resulting value may be far from what really happened,
        it has nice behavior with respect to common assumptions
        of search algorithms.

        :returns: Forwarding rate in load units estimated from loss ratio.
        :rtype: float
        """
        return self.intended_load * (1.0 - self.loss_ratio)
