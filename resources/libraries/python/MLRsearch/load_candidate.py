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

"""Module defining LoadCandidate class."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from .discrete_load import DiscreteLoad


@total_ordering
@dataclass(frozen=True)
class LoadCandidate:
    """FIXME"""

    load: Optional[DiscreteLoad] = None
    """FIXME"""
    duration: float = None
    """FIXME"""

    def __str__(self) -> str:
        """FIXME"""
        return f"d={self.duration},l={self.load}"

    def __eq__(self, other: LoadCandidate) -> bool:
        """FIXME"""
        if self.load != other.load:
            return False
        return self.duration == other.duration

    def __lt__(self, other: LoadCandidate) -> bool:
        """FIXME"""
        if not self.load:
            return False
        if not other.load:
            return True
        if self.load < other.load:
            return True
        if self.load > other.load:
            return False
        return self.duration < other.duration

    def __bool__(self) -> bool:
        """FIXME"""
        return self.load is not None
