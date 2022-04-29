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

"""Module defining a class dealing with duration scaling and width scaling."""

from .WidthArithmetics import multiply_relative_width


class DurationAndWidthScaling:
    """Encapsulate values that depend on MLRsearch phase.

    Phase 0 is the first intermediate phase, the duration is also used
    for the initial phase.
    If there are 2 intermediate phases, the final phase is phase 2,
    so 3 phases overall.
    """

    def __init__(self, phases, initial_duration, final_duration, final_width):
        """Compute the dicts with results.

        :param phases: Number of intermediate phases, at least 1.
        :param initial_duration: Duration [s] for first intermediate phase.
        :param final_duration: Duration [s] for the final phase.
        :param final_width: Relative width goal for the final phase.
        :type phases: int
        :type initial_duration: float
        :type final_dutration: float
        :type final_width: float
        """
        self.intermediate_phases = int(phases)
        self.initial_duration = float(initial_duration)
        self.final_duration = float(final_duration)
        self.final_width = float(final_width)
        self.duration_by_phase = dict()
        multiplier = pow(final_duration / initial_duration, 1.0 / phases)
        duration = self.initial_duration
        for phase in range(self.intermediate_phases + 1):
            self.duration_by_phase[phase] = duration
            duration *= multiplier
        self.width_by_phase = dict()
        width = self.final_width
        for phase in range(self.intermediate_phases, -1, -1):
            self.width_by_phase[phase] = width
            width = multiply_relative_width(width, 2.0)

    def duration(self, phase):
        """Return the trial duration for this phase.

        :param phase: Number of phase, 0 is the first intermediate one.
        :type phase: int
        :returns: Trial duration [s] for this phase.
        :rtype: float
        :raises IndexError: If the phase is outside the constructed data.
        """
        return self.duration_by_phase[phase]

    def width_goal(self, phase):
        """Return the target relative width for this phase.

        :param phase: Number of phase, 0 is the first intermediate one.
        :type phase: int
        :returns: Target relative width for this phase.
        :rtype: float
        :raises IndexError: If the phase is outside the constructed data.
        """
        return self.width_by_phase[phase]
