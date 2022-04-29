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

"""Module defining OtherConfig class."""

import time


class OtherConfig:
    """Structure containing numerous static config items.

    This is just a way to decrease number of fields for the main class.
    Important items and dynamic items are not here.
    Fields relevant to phase scaling are also elsewhere.
    """

    def __init__(
        self, packet_loss_ratios, min_rate, max_rate, timeout
    ):
        """Convert, check and store the argument values.

        Basic consistency checks are performed, raising RuntimeError.

        One derived quantity is also stored: stop time,
        timeout is not stored (as it is already stored elsewhere).

        :param packet_loss_ratios: List of ratios for the current search.
        :param min_rate: Minimal target transmit rate available
            for the current search [tps].
        :param max_rate: Maximal target transmit rate available
            for the current search [tps].
        :param timeout: Time [s] after which the search fails.
        :type packet_loss_ratios: Iterable[float]
        :type min_rate: float
        :type max_rate: float
        :type timeout: float
        :raises RuntimeError: If there is no ratio or the ratios are not sorted.
        """
        self.min_rate = float(min_rate)
        self.max_rate = float(max_rate)
        self.stop_time = time.monotonic() + timeout
        """Monotonic time [s] at which we should fail on timeout."""

        self.packet_loss_ratios = [float(ratio) for ratio in packet_loss_ratios]
        if len(self.packet_loss_ratios) < 1:
            raise RuntimeError(u"At least one ratio is required!")
        if self.packet_loss_ratios != sorted(set(self.packet_loss_ratios)):
            raise RuntimeError(u"Input ratios have to be sorted and unique!")
