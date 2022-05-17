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

from dataclasses import dataclass, field
from typing import Dict

from .width_arithmetics import multiply_relative_width, ROUNDING_CONSTANT


@dataclass
class DurationAndWidthScaling:
    """Encapsulate values that depend on MLRsearch phase.

    Phase 0 is the first intermediate phase, the duration is also used
    for the initial phase.
    If there are 2 intermediate phases, the final phase is phase 2,
    so 3 phases overall.

    No default values, contructor call has to specify everything.

    The caller may need multiple instances if different ratios
    require different final width goal.
    """

    intermediate_phases: int
    """Number of intermediate phases, at least 1."""
    initial_duration: float
    """Duration [s] for first intermediate phase."""
    final_duration: float
    """Duration [s] for the final phase."""
    final_width: float
    """Relative width goal for the final phase."""
    # Secondary private quantities.
    _duration_by_phase: Dict[int, float] = field(init=False, repr=False)
    """Durations computed for phase number."""
    _width_by_phase: Dict[int, float] = field(init=False, repr=False)
    """Width goals computed for phase number."""

    def __post_init__(self):
        """Ensure correct primary types and compute the secondary quantities.
        """
        self.intermediate_phases = int(self.intermediate_phases)
        self.initial_duration = float(self.initial_duration)
        self.final_duration = float(self.final_duration)
        self.final_width = float(self.final_width)
        self._duration_by_phase = dict()
        multiplier = pow(
            self.final_duration / self.initial_duration,
            1.0 / self.intermediate_phases
        )
        duration = self.initial_duration
        for phase in range(self.intermediate_phases + 1):
            self._duration_by_phase[phase] = duration
            duration *= multiplier
        self._width_by_phase = dict()
        width = self.final_width
        for phase in range(self.intermediate_phases, -1, -1):
            self._width_by_phase[phase] = width
            # Rounding constant is needed to ensure halving works reliably.
            # One constant is not enough when uneven splits happen.
            width = multiply_relative_width(
                width, 2.0 * ROUNDING_CONSTANT * ROUNDING_CONSTANT
            )

    def duration(self, phase):
        """Return the trial duration for this phase.

        :param phase: Number of phase, 0 is the first intermediate one.
        :type phase: int
        :returns: Trial duration [s] for this phase.
        :rtype: float
        :raises IndexError: If the phase is outside the constructed data.
        """
        return self._duration_by_phase[phase]

    def width_goal(self, phase):
        """Return the target relative width for this phase.

        :param phase: Number of phase, 0 is the first intermediate one.
        :type phase: int
        :returns: Target relative width for this phase.
        :rtype: float
        :raises IndexError: If the phase is outside the constructed data.
        """
        return self._width_by_phase[phase]
