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

"""Module defining Candidate class."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth
from .selector import Selector


@total_ordering
@dataclass(frozen=True)
class Candidate:
    """Class describing next trial inputs, as nominated by a selector.

    When two instances are compared, the lesser has higher priority
    for chosing which trial is actually performed next.

    The reference to the nominating selector is included for convenience.

    Truthiness is derived from None-ness of load.
    """

    load: Optional[DiscreteLoad] = None
    """Measure at this intended load. None if no trial nominated by selector."""
    duration: float = None
    """Trial duration as chosen by the selector."""
    width: Optional[DiscreteWidth] = None
    """Set current with to this when this candidate becomes the winner."""
    selector: Selector = None
    """Reference to the selector instance which nominated this candidate."""

    def __str__(self) -> str:
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return f"d={self.duration},l={self.load}"

    def __eq__(self, other: Candidate) -> bool:
        """Return whether the two instances describe the same trial inputs.

        :param other: The other instance to compare to.
        :type other: Candidate
        :returns: True if the instances are equivalent.
        :rtype: bool
        """
        raise RuntimeError("Candidate equality comparison shall not be needed.")

    def __lt__(self, other: Candidate) -> bool:
        """Return whether self should be measured before other.

        In the decreasing order of importance:
        Non-None load is preferred
        Self is less than other when both loads are None.
        Lower offered load is preferred.
        Longer trial duration is preferred.
        Non-none width is preferred.
        Larger width is preferred.
        Self is preferred.

        :param other: The other instance to compare to.
        :type other: Candidate
        :returns: True if self should be measured sooner.
        :rtype: bool
        """
        if not self.load:
            if other.load:
                return False
            return True
        if not other.load:
            return True
        if self.load < other.load:
            return True
        if self.load > other.load:
            return False
        if self.duration > other.duration:
            return True
        if self.duration < other.duration:
            return False
        if not self.width:
            if other.width:
                return False
            return True
        if not other.width:
            return True
        return self.width >= other.width

    def __bool__(self) -> bool:
        """Does this candidate choose to perform any trial measurement?

        :returns: True if yes, it does choose to perform.
        :rtype: bool
        """
        return bool(self.load)

    @staticmethod
    def nominated_by(selector: Selector) -> Candidate:
        """Call enter() on selector, wrap into Candidate instance and return it.

        :param selector: Selector to call.
        :type selector: Selector
        :returns: Newly created Candidate instance with nominated trial inputs.
        :rtype: Candidate
        """
        load, duration, width = selector.nominate()
        return Candidate(
            load=load,
            duration=duration,
            width=width,
            selector=selector,
        )

    def done(self) -> bool:
        """Return whether the selector wants to keep measuring the same load.

        :returns: Yes if the same load should be measured again.
        :rtype: bool
        """
        return self.selector.done(self.load)
