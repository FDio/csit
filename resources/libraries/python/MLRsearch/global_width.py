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

"""Module defining GlobalWidth class."""


from __future__ import annotations

from dataclasses import dataclass

from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth


@dataclass
class GlobalWidth:
    """Primarily used to synchronize external search steps across selectors.

    The full name is global current width, but that is too long for identifiers.

    While each selector tracks its "local" (per goal) width using expander,
    it is important we do not interleave upper external search for two goals.
    That is why all selector instances refer to a singleton instance of this.

    In general, this value remains constant when main loop iterates over
    selectors and when selector iterates over strategies.
    After winner is measured, this width is set to winner width value
    and for some strategies that width is expanded when external search says so.

    The two methods are not really worth creating a new class,
    but the main reason is having a name for type hints
    that distinguish this from various other "width" and "current" values.
    """

    width: DiscreteWidth
    """Minimum width to apply at next external search step."""
    # TODO: Add a setter, so it is easier to add debug logging.

    @staticmethod
    def from_loads(load0: DiscreteLoad, load1: DiscreteLoad) -> GlobalWidth:
        """Initialize the value based on two loads from initial trials.

        :param load0: Lower (or equal) load from the two most recent trials.
        :param load1: Higher (or equal) load from the two most recent trials.
        :type load0: DiscreteLoad
        :type load1: DiscreteLoad
        :returns: Newly created instance with computed width.
        :rtype: GlobalWidth
        """
        return GlobalWidth(load1 - load0)

    def or_larger(self, width: DiscreteWidth) -> DiscreteWidth:
        """Return width from argument or self, whichever is larger.

        :param width: A selector (strategy) asks if this width is large enough.
        :type width: DiscreteWidth
        :returns: Argument or current width.
        :rtype: DiscreteWidth
        """
        return width if width > self.width else self.width
