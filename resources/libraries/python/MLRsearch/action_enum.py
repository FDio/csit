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

"""Module defining ActionEnum class."""

from __future__ import annotations

from enum import IntEnum, auto


class ActionEnum(IntEnum):
    """FIXME"""

    NONE = auto()
    REFINE_MIN = auto()
    REFINE_MAX = auto()
    HALVE = auto()
    REFINE_LO = auto()
    REFINE_HI = auto()
    EXT_LO = auto()
    EXT_HI = auto()
    BISECT = auto()
    DONE = auto()
