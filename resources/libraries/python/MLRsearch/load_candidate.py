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

"""Module defining LoadCandidate class."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from .discrete_load import DiscreteLoad


@total_ordering
@dataclass(frozen=True)
class LoadCandidate:
    """Class describing next trial inputs, as nominated by a load selector.

    When two instances are compared, the lesser has higher priority
    for chosing which trial is actually performed next.
    """

    load: Optional[DiscreteLoad] = None
    """Measure at this intended load. None if no trial nominated by selector."""
    duration: float = None
    """Trial (if any) duration as chosen by the selector."""

    def __str__(self) -> str:
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return f"d={self.duration},l={self.load}"

    def __eq__(self, other: LoadCandidate) -> bool:
        """Return whether the two instances describe the same trial inputs.

        :param other: The other instance to compare to.
        :type other: LoadCandidate
        :returns: True if the instances are equivalent.
        :rtype: bool
        """
        if self.load != other.load:
            return False
        return self.duration == other.duration

    def __lt__(self, other: LoadCandidate) -> bool:
        """Return whether self should be measured before other.

        In the decreasing order of importance:
        Lack of measurement is never preferred.
        Lower offered load is preferred.
        Longer trial duration is preferred.

        :param other: The other instance to compare to.
        :type other: LoadCandidate
        :returns: True if self should be measured sooner.
        :rtype: bool
        """
        if not self.load:
            return False
        if not other.load:
            return True
        if self.load < other.load:
            return True
        if self.load > other.load:
            return False
        return self.duration > other.duration

    def __bool__(self) -> bool:
        """Does this candidate choose to perform any trial measurement?

        :returns: True if yes, it does choose to perform.
        :rtype: bool
        """
        return self.load is not None
