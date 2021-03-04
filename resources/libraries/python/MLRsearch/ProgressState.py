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

"""Module defining ProgressState class."""


class ProgressState:
    """Structure containing data to be passed around in recursion.

    This is basically a private class of MultipleRatioSearch,
    but keeping it in a separate file makes things more readable.
    """

    def __init__(
            self, database, phases, duration, width_goal, packet_loss_ratios,
            min_rate, max_rate):
        """Convert and store the argument values.

        Also initializa the stored width for external search.

        :param result: Structure containing measured results.
        :param phases: How many intermediate phases to perform
            before the current one.
        :param duration: Trial duration to use in the current phase [s].
        :param width_goal: The goal relative width for the curreent phase.
        :param packet_loss_ratios: List of ratios for the current search.
        :param min_rate: Minimal target transmit rate available
            for the current search [tps].
        :param max_rate: Maximal target transmit rate available
            for the current search [tps].
        :type result: MeasurementDatabase
        :type phases: int
        :type duration: float
        :type width_goal: float
        :type packet_loss_ratios: Iterable[float]
        :type min_rate: float
        :type max_rate: float
        """
        self.database = database
        self.phases = int(phases)
        self.duration = float(duration)
        self.width_goal = float(width_goal)
        self.packet_loss_ratios = [
            float(ratio) for ratio in packet_loss_ratios
        ]
        self.min_rate = float(min_rate)
        self.max_rate = float(max_rate)
