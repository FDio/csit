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

"""Module defining DurationAndWidthScaling class."""

from dataclasses import dataclass, field
from typing import Dict

from .criterion import Criterion
from .discrete_width import DiscreteWidth
from .load_rounding import LoadRounding


@dataclass
class DurationAndWidthScaling:
    """Encapsulate values that depend on MLRsearch phase.

    Phase 0 is the first intermediate phase, the duration is also used
    for the initial phase.
    If there are 2 intermediate phases, the final phase is phase 2,
    so 3 phases overall.

    No default values, contructor call has to specify everything.

    The caller may need multiple instances if different ratios
    require different final width goal integers.

    It is possible to have zero intermediate phases,
    in that case initial duration is ignored (as the only phase is final).
    """

    criterion: Criterion
    rounding: LoadRounding
    # Secondary private quantities.
    _duration_by_phase: Dict[int, float] = field(init=False, repr=False)
    """Durations computed for phase number."""
    _width_by_phase: Dict[int, DiscreteWidth] = field(init=False, repr=False)
    """Width goal (discrete form) computed for phase number."""

    def __post_init__(self) -> None:
        """Ensure correct primary types and compute the secondary quantities.

        :raises RuntimeError: If an unsupported argument value is detected.
        """
        final_width = DiscreteWidth(
            rounding=self.rounding,
            float_width=self.criterion.relative_width,
        )
        self._width_by_phase = dict()
        width = final_width
        for phase in range(self.criterion.intermediate_phases, -1, -1):
            self._width_by_phase[phase] = width
            width *= 2
        self._duration_by_phase = dict()
        if not self.criterion.intermediate_phases:
            # Avoid possible division by zero.
            self._duration_by_phase[0] = self.criterion.trials_duration
            return
        multiplier = pow(
            self.criterion.trials_duration,  # initial duration is 1.0 s.
            -1.0 / self.criterion.intermediate_phases,
        )
        duration = self.criterion.trials_duration
        for phase in range(self.criterion.intermediate_phases, -1, -1):
            self._duration_by_phase[phase] = duration
            duration *= multiplier

    def duration(self, phase: int) -> int:
        """Return the trial duration for this phase.

        :param phase: Number of phase, 0 is the first intermediate one.
        :type phase: int
        :returns: Trial duration [s] for this phase.
        :rtype: float
        :raises IndexError: If the phase is outside the constructed data.
        """
        return self._duration_by_phase[phase]

    def width_goal(self, phase: int) -> DiscreteWidth:
        """Return the target relative width (discrete form) for this phase.

        :param phase: Number of phase, 0 is the first intermediate one.
        :type phase: int
        :returns: Target relative width for this phase, in discrete form.
        :rtype: DiscreteWidth
        :raises IndexError: If the phase is outside the constructed data.
        """
        return self._width_by_phase[phase]
