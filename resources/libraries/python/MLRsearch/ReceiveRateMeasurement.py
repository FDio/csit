# Copyright (c) 2021 Cisco and/or its affiliates.
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
            approximated_duration=0.0, partial_transmit_count=0,
            effective_loss_ratio=None):
        """Constructor, normalize primary and compute secondary quantities.

        If approximated_duration is nonzero, it is stored.
        If approximated_duration is zero, duration value is stored.
        Either way, additional secondary quantities are computed
        from the store value.

        If there is zero transmit_count, ratios are set to zero.

        In some cases, traffic generator does not attempt all the needed
        transactions. In that case, nonzero partial_transmit_count
        holds (an estimate of) count of the actually attempted transactions.
        This is used to populate some secondary quantities.

        TODO: Use None instead of zero?

        Field effective_loss_ratio is specific for use in MLRsearch,
        where measurements with lower loss ratio at higher target_tr
        cannot be relied upon if there is a measurement with higher loss ratio
        at lower target_tr. in this case, the higher loss ratio from
        other measurement is stored as effective loss ratio in this measurement.
        If None, the computed loss ratio of this measurement is used.
        If not None, the computed ratio can still be apllied if it is larger.

        :param duration: Measurement duration [s].
        :param target_tr: Target transmit rate [pps].
            If bidirectional traffic is measured, this is bidirectional rate.
        :param transmit_count: Number of packets transmitted [1].
        :param loss_count: Number of packets transmitted but not received [1].
        :param approximated_duration: Estimate of the actual time of the trial.
        :param partial_transmit_count: Estimate count of actually attempted
            transactions.
        :param effective_loss_ratio: None or highest loss ratio so far.
        :type duration: float
        :type target_tr: float
        :type transmit_count: int
        :type loss_count: int
        :type approximated_duration: float
        :type partial_transmit_count: int
        """
        self.duration = float(duration)
        self.target_tr = float(target_tr)
        self.transmit_count = int(transmit_count)
        self.loss_count = int(loss_count)
        self.receive_count = transmit_count - loss_count
        self.transmit_rate = transmit_count / self.duration
        self.loss_rate = loss_count / self.duration
        self.receive_rate = self.receive_count / self.duration
        self.loss_ratio = (
            float(self.loss_count) / self.transmit_count
            if self.transmit_count > 0 else 1.0
        )
        self.effective_loss_ratio = self.loss_ratio
        if effective_loss_ratio is not None:
            if effective_loss_ratio > self.loss_ratio:
                self.effective_loss_ratio = float(effective_loss_ratio)
        self.receive_ratio = (
            float(self.receive_count) / self.transmit_count
            if self.transmit_count > 0 else 0.0
        )
        self.approximated_duration = (
            float(approximated_duration) if approximated_duration
            else self.duration
        )
        self.approximated_receive_rate = (
            self.receive_count / self.approximated_duration
            if self.approximated_duration > 0.0 else 0.0
        )
        # If the traffic generator is unreliable and sends less packets,
        # the absolute receive rate might be too low for next target.
        self.partial_transmit_count = (
            int(partial_transmit_count) if partial_transmit_count
            else self.transmit_count
        )
        self.partial_receive_ratio = (
            float(self.receive_count) / self.partial_transmit_count
            if self.partial_transmit_count > 0 else 0.0
        )
        self.partial_receive_rate = (
            self.target_tr * self.partial_receive_ratio
        )
        # We use relative packet ratios in order to support cases
        # where target_tr is in transactions per second,
        # but there are multiple packets per transaction.
        self.relative_receive_rate = (
            self.target_tr * self.receive_count / self.transmit_count
        )

    def __str__(self):
        """Return string reporting input and loss ratio."""
        return f"d={self.duration!s},Tr={self.target_tr!s}," \
            f"Df={self.loss_ratio!s}"

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return f"ReceiveRateMeasurement(duration={self.duration!r}," \
            f"target_tr={self.target_tr!r}," \
            f"transmit_count={self.transmit_count!r}," \
            f"loss_count={self.loss_count!r}," \
            f"approximated_duration={self.approximated_duration!r}," \
            f"partial_transmit_count={self.partial_transmit_count!r}," \
            f"effective_loss_ratio={self.effective_loss_ratio!r})"

    def copy(self):
        """Return new instance with identical fields."""
        return self.__class__(
            duration=self.duration,
            target_tr=self.target_tr,
            transmit_count=self.transmit_count,
            loss_count=self.loss_count,
            approximated_duration=self.approximated_duration,
            partial_transmit_count=self.partial_transmit_count,
            effective_loss_ratio=self.effective_loss_ratio,
        )
