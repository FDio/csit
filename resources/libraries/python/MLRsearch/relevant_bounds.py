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

from .load_stats import LoadStats
from .measurement_database import MeasurementDatabase
from .target_spec import TargetSpec


@dataclass
class RelevantBounds:
    """Structure of several bounds relevant for specific ratio and phase.

    Nothing special in the fields, the added value is the factory.
    """

    clo: Optional[LoadStats]
    """Tightest valid lower bound at current duration or longer."""
    chi: Optional[LoadStats]
    """Tightest valid upper bound at current duration or longer."""
    plo: Optional[LoadStats]
    """Tightest valid lower bound (below chi) at any duration.
    Can be lower than clo due to phi. Can be identical to clo."""
    phi: Optional[LoadStats]
    """Tightest valid upper bound (above clo) at any duration.
    Lower than chi, or even than clo. Can be identical to chi."""
    spec: TargetSpec
    """FIXME"""
    pspec: TargetSpec
    """FIXME"""

    def __str__(self):
        """FIXME"""
        return f"clo=({self.clo}),chi=({self.chi}),plo=({self.plo}),phi=({self.phi})"

    @staticmethod
    def from_database(
        database: MeasurementDatabase,
        current_target: TargetSpec,
    ) -> RelevantBounds:
        """Create instance by getting and processing bounds from database.

        If bounds for coarser duration are already reported
        for current duration, they are set to None.
        If the phase is the first one, coarser_target should be None.

        FIXME
        :param database: Database of all available trial measurement results.
        :param ratio_goal: Loss ratio the bounds should be tight around.
        :param current_duration: Trial duration [s] for the current phase.
        :param coarser_duration: Trial duration [s] for the coarser phase.
        :type database: MeasurementDatabase
        :type ratio_goal: float
        :type current_duration: float
        :type coarser_duration: Optional[float]
        :returns: New instance holding the processed values.
        :rtype: RelevantBounds
        """
        clo, chi = database.get_valid_bounds(current_target)
        plo, phi = None, None
        if pspec := current_target.coarser:
            plo, phi = database.get_valid_bounds(pspec)
            # FIXME: None if duplicate?
        ret = RelevantBounds(
            clo=clo, chi=chi, plo=plo, phi=phi, spec=current_target, pspec=pspec
        )
        return ret
