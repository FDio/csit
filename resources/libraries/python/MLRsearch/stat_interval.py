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

"""Module defining DiscreteInterval class."""

from dataclasses import dataclass

from .discrete_interval import DiscreteInterval
from .trimmed_stat import TrimmedStat


# TODO: Can this be frozen?
@dataclass
class StatInterval(DiscreteInterval):
    """Interval class useful for reporting final results."""

    def __post_init__(self):
        """Check the two loads are type TrimmedStat.

        :raises RuntimeError: If a field has an unexpected type.
        """
        super().__post_init__()
        if not isinstance(self.lower_bound, TrimmedStat):
            raise RuntimeError(f"Lower bound not trimmed: {self.lower_bound!r}")
        if not isinstance(self.upper_bound, TrimmedStat):
            raise RuntimeError(f"Upper bound not trimmed: {self.lower_bound!r}")

    def __str__(self) -> str:
        """Convert to a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return (
            f"(lower_bound={float(self.lower_bound)}"
            f",upper_bound={float(self.upper_bound)})"
        )
