# Copyright (c) 2023 Cisco and/or its affiliates.
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
    """Container for 4 tightest bound relevant to a selector.

    Two for the current target, two for the preceding target.
    If there is no bound for a field, use None.

    Nothing special in the fields, the added value is the factory.
    """

    clo: Optional[LoadStats]
    """The tightest lower bound (trimmed) for the current target."""
    chi: Optional[LoadStats]
    """The tightest upper bound (trimmed) for the current target."""
    plo: Optional[LoadStats]
    """The tightest lower bound (trimmed) for the preceding target.
    Can be lower than clo due to phi. Can be identical to clo."""
    phi: Optional[LoadStats]
    """The tightest upper bound (trimmed) for the preceding target.
    Lower than chi, or even than clo. Can be identical to chi."""

    def __str__(self):
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return (
            f"clo=({self.clo}),chi=({self.chi})"
            f",plo=({self.plo}),phi=({self.phi})"
        )

    @staticmethod
    def from_database(
        database: MeasurementDatabase,
        target: TargetSpec,
    ) -> RelevantBounds:
        """Create instance by getting and processing bounds from database.

        Basically just two calls to database.get_valid_bounds.

        :param database: Database of all available trial measurement results.
        :param target: The current target the bounds shall be relevant to.
        :type database: MeasurementDatabase
        :type target: TargetSpec
        :returns: New instance holding the values found in database.
        :rtype: RelevantBounds
        """
        clo, chi = database.get_valid_bounds(target)
        plo, phi = None, None
        if preceding := target.preceding:
            plo, phi = database.get_valid_bounds(preceding)
        ret = RelevantBounds(clo=clo, chi=chi, plo=plo, phi=phi)
        return ret
