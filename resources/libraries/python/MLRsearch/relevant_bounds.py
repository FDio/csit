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
    """Container for the relevant lower and upper bound for some target.

    If there is no valid bound, None is used.

    Relevant upper bound is smallest load acting as an upper bound.
    Relevant lower bound acts as a lower bound, has to be strictly smaller
    than the relevant upper bound, and is largest among such loads.

    Nothing special in the fields, the added value is the factory,
    and the fact most of time a strategy wants to know both bounds.

    The short names "clo" and "chi" are used in logging and technical comments.
    """

    clo: Optional[LoadStats]
    """The relevant lower bound (trimmed) for the current target."""
    chi: Optional[LoadStats]
    """The relevant upper bound (trimmed) for the current target."""

    def __str__(self):
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        clo = int(self.clo) if self.clo else None
        chi = int(self.chi) if self.chi else None
        return f"clo={clo},chi={chi}"

    @staticmethod
    def from_database(
        database: MeasurementDatabase,
        target: TargetSpec,
    ) -> RelevantBounds:
        """Create instance by getting and processing bounds from database.

        Basically a call to database.get_relevant_bounds.

        :param database: Database of all available trial measurement results.
        :param target: The current target the bounds shall be relevant to.
        :type database: MeasurementDatabase
        :type target: TargetSpec
        :returns: New instance holding the values found in database.
        :rtype: RelevantBounds
        """
        clo, chi = database.get_relevant_bounds(target)
        ret = RelevantBounds(clo=clo, chi=chi)
        return ret
