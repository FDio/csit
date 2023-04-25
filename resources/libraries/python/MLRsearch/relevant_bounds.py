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

    clo1: Optional[LoadStats]
    """Tightest valid lower bound at current duration or longer."""
    chi1: Optional[LoadStats]
    """Tightest valid upper bound at current duration or longer."""
    plo1: Optional[LoadStats]
    """Tightest valid lower bound (below chi1) at any duration.
    Can be lower than clo1 due to phi1. Can be identical to clo1."""
    phi1: Optional[LoadStats]
    """Tightest valid upper bound (above clo1) at any duration.
    Lower than chi1, or even than clo1. Can be identical to chi1."""
    spec: TargetSpec
    """FIXME"""
    pspec: TargetSpec
    """FIXME"""

    def s4(self, bound, spec):
        """FIXME"""
        if not bound:
            return "None"
        return bound.s4(spec)

    def __str__(self):
        """FIXME"""
        return f"clo1={self.s4(self.clo1,self.spec)} chi1={self.s4(self.chi1,self.spec)} plo1={self.s4(self.plo1,self.pspec)} phi1={self.s4(self.phi1,self.pspec)}"

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
        clo1, chi1 = database.get_valid_bounds(current_target)
        plo1, phi1 = None, None
        pspec = current_target.coarser
        if pspec:
            plo1, phi1 = database.get_valid_bounds(pspec)
        # FIXME: None if duplicate?
        ret = RelevantBounds(
            clo1=clo1, chi1=chi1, plo1=plo1, phi1=phi1, spec=current_target, pspec=pspec
        )
        return ret
