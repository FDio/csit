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

"""
__init__ file for Python package "strategy".
"""

from .base import StrategyBase
from .bisect import BisectStrategy
from .extend_hi import ExtendHiStrategy
from .extend_lo import ExtendLoStrategy
from .halve import HalveStrategy
from .refine_hi import RefineHiStrategy
from .refine_lo import RefineLoStrategy


STRATEGY_CLASSES = (
    HalveStrategy,
    RefineLoStrategy,
    RefineHiStrategy,
    ExtendLoStrategy,
    ExtendHiStrategy,
    BisectStrategy,
)
"""Tuple of strategy constructors in order of priority."""
