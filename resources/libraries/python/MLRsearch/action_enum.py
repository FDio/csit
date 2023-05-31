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

"""Module defining ActionEnum class."""

from enum import IntEnum, auto


class ActionEnum(IntEnum):
    """States for finite state machine for a load selector of a single target.

    The full state also contains flags and bounds.
    """

    WAIT = auto()
    """Waiting for preceding target to become done."""
    HALVE = auto()
    """Add more trials in between preceding target bounds."""
    REFINE_MIN = auto()
    """Add more trials at min load."""
    REFINE_MAX = auto()
    """Add more trials at max load."""
    REFINE_LO = auto()
    """Add more trials to preceding target lower bound."""
    REFINE_HI = auto()
    """Add more trials to preceding target upper bound."""
    EXT_LO = auto()
    """Add more trials at a load below current upper bound."""
    EXT_HI = auto()
    """Add more trials at a load above current lower bound."""
    BISECT = auto()
    """Add more trials in between current bounds."""
    DONE = auto()
    """No more trials needed by this load selector."""
