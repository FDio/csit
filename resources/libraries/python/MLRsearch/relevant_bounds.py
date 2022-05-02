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

from dataclasses import dataclass
from typing import Optional

from .receive_rate_measurement import ReceiveRateMeasurement


@dataclass
class RelevantBounds:
    """Structure of several bounds relevant for specific ratio and phase."""

    clo1: Optional[ReceiveRateMeasurement]
    """Tightest valid lower bound at current duration or longer."""
    chi1: Optional[ReceiveRateMeasurement]
    """Tightest valid upper bound at current duration or longer."""
    plo1: Optional[ReceiveRateMeasurement]
    """Tightest valid lower bound at previous duration or longer."""
    phi1: Optional[ReceiveRateMeasurement]
    """Tightest valid upper bound at previous duration or longer."""
    clo2: Optional[ReceiveRateMeasurement]
    """Second tightest lower bound at current duration or longer."""
    chi2: Optional[ReceiveRateMeasurement]
    """Second tightest upper bound at current duration or longer."""

    @classmethod
    def from_database(
        cls, database, ratio_goal, current_duration, previous_duration
    ):
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
        :rtype: cls
        :raises RuntimeError: If internal inconsistency is detected.
        """
        bounds = database.get_valid_bounds(ratio_goal, current_duration)
        plo1, phi1, clo1, chi1, clo2, chi2 = None, None, *bounds
        if previous_duration is not None:
            bounds = database.get_valid_bounds(ratio_goal, previous_duration)
            plo1, phi1, _, _ = bounds
            if plo1 is not None and plo1 in [clo1, clo2]:
                # Possible as plo1 can have current duration.
                plo1 = None
            if phi1 is not None and phi1 in [chi1, chi2]:
                phi1 = None
        return cls(
            clo1=clo1, chi1=chi1, clo2=clo2, chi2=chi2, plo1=plo1, phi1=phi1
        )
