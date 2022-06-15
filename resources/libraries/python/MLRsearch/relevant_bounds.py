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

"""Module defining RelevantBounds class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .comparable_measurement_result import ComparableMeasurementResult
from .measurement_database import MeasurementDatabase


@dataclass
class RelevantBounds:
    """Structure of several bounds relevant for specific ratio and phase.

    Nothing special in the fields, the added value is the factory.
    """

    clo1: Optional[ComparableMeasurementResult]
    """Tightest valid lower bound at current duration or longer."""
    chi1: Optional[ComparableMeasurementResult]
    """Tightest valid upper bound at current duration or longer."""
    plo1: Optional[ComparableMeasurementResult]
    """Tightest valid lower bound at previous duration or longer."""
    phi1: Optional[ComparableMeasurementResult]
    """Tightest valid upper bound at previous duration or longer."""
    clo2: Optional[ComparableMeasurementResult]
    """Second tightest lower bound at current duration or longer."""
    chi2: Optional[ComparableMeasurementResult]
    """Second tightest upper bound at current duration or longer."""

    @staticmethod
    def from_database(
        database: MeasurementDatabase,
        ratio_goal: float,
        current_duration: float,
        previous_duration: float,
    ) -> RelevantBounds:
        """Create instance by getting and processing bounds from database.

        If bounds for previous duration are already reported
        for current duration, they are set to None.
        If the phase is the first one, previous_duration should be None.

        :param database: Database of all available trial measurement results.
        :param ratio_goal: Loss ratio the bounds should be tight around.
        :param current_duration: Trial duration [s] for the current phase.
        :param previous_duration: Trial duration [s] for the previous phase.
        :type database: MeasurementDatabase
        :type ratio_goal: float
        :type current_duration: float
        :type previous_duration: Optional[float]
        :returns: New instance holding the processed values.
        :rtype: RelevantBounds
        """
        bounds = database.get_valid_bounds(ratio_goal, current_duration)
        plo1, phi1, clo1, chi1, clo2, chi2 = None, None, *bounds
        if previous_duration is not None:
            bounds = database.get_valid_bounds(ratio_goal, previous_duration)
            plo1, phi1, _, _ = bounds
            if plo1 and plo1 in [clo1, clo2]:
                # Possible as plo1 can have current duration.
                plo1 = None
            if phi1 and phi1 in [chi1, chi2]:
                phi1 = None
        return RelevantBounds(
            clo1=clo1, chi1=chi1, clo2=clo2, chi2=chi2, plo1=plo1, phi1=phi1
        )
