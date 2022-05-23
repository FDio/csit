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

"""Module defining SelectionInfo class."""

from dataclasses import dataclass
from typing import Optional

from .discrete_load import DiscreteLoad


@dataclass
class SelectionInfo:
    """Structure for output (and one input) of load selection method.

    Contains default values, so that calling code can be shorter.
    The default value is always the falsy one, as that is pythonic.
    """

    load: Optional[DiscreteLoad] = None
    """Selected load. None means no measurements needed at the phase."""
    halve: bool = False
    """Whether the subsequent load selections can attempt the halving."""
    remeasure: bool = False
    """Whether the subsequent load selection can attempt re-measurement."""
    handle: bool = False
    """Whether the load should be handled with respext to load limits."""
