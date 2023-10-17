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

from .trimmed_stat import TrimmedStat


@dataclass
class RelevantBounds:
    """Container for the pair of relevant bounds for a target.

    If there is no valid bound, None is used.

    Relevant upper bound is smallest load acting as an upper bound.
    Relevant lower bound acts as a lower bound, has to be strictly smaller
    than the relevant upper bound, and is largest among such loads.

    The short names "clo" and "chi" are also commonly used
    in logging and technical comments.

    Trimming could be done here, but it needs to known the target explicitly,
    so it is done in MeasurementDatabase instead.
    """

    clo: Optional[TrimmedStat]
    """The relevant lower bound (trimmed) for the current target."""
    chi: Optional[TrimmedStat]
    """The relevant upper bound (trimmed) for the current target."""

    # TODO: Check types in post init?

    def __str__(self) -> str:
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        clo = int(self.clo) if self.clo else None
        chi = int(self.chi) if self.chi else None
        return f"clo={clo},chi={chi}"
