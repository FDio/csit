# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""Module defining ReceiveRateMeasurement class."""


class ReceiveRateMeasurement:
    """Structure defining the result of single Rr measurement."""

    def __init__(
            self, duration, target_tr, transmit_count, loss_count,
            approximated_duration=0.0):
        """Constructor, normalize primary and compute secondary quantities.

        If approximated_duration is nonzero, it is stored.
        If approximated_duration is zero, duration value is stored.
        Either way, additional secondary quantities are computed
        from the store value.

        TODO: Use None instead of zero?

        :param duration: Measurement duration [s].
        :param target_tr: Target transmit rate [pps].
            If bidirectional traffic is measured, this is bidirectional rate.
        :param transmit_count: Number of packets transmitted [1].
        :param loss_count: Number of packets transmitted but not received [1].
        :param approximated_duration: Estimate of the actual time of the trial.
        :type duration: float
        :type target_tr: float
        :type transmit_count: int
        :type loss_count: int
        :type approximated_duration: float
        """
        self.duration = float(duration)
        self.target_tr = float(target_tr)
        self.transmit_count = int(transmit_count)
        self.loss_count = int(loss_count)
        self.receive_count = transmit_count - loss_count
        self.transmit_rate = transmit_count / self.duration
        self.loss_rate = loss_count / self.duration
        self.receive_rate = self.receive_count / self.duration
        self.loss_fraction = float(self.loss_count) / self.transmit_count
        self.receive_fraction = float(self.receive_count) / self.transmit_count
        # If the traffic generator is unreliable and sends less packets,
        # the absolute receive rate might be too low for next target.
        self.relative_receive_rate = self.target_tr * self.receive_fraction
        if approximated_duration:
            self.approximated_duration = approximated_duration
        else:
            self.approximated_duration = duration
        self.approximated_receive_rate = self.receive_count
        self.approximated_receive_rate /= self.approximated_duration

    def __str__(self):
        """Return string reporting input and loss fraction."""
        return f"d={self.duration!s},Tr={self.target_tr!s}," \
            f"Df={self.loss_fraction!s},ad={self.approximated_duration}"

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return f"ReceiveRateMeasurement(duration={self.duration!r}," \
            f"target_tr={self.target_tr!r}," \
            f"transmit_count={self.transmit_count!r}," \
            f"loss_count={self.loss_count!r}," \
            f"approximated_duration={self.approximated_duration!r})"
