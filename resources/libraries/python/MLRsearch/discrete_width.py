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

"""Module defining DiscreteWidth class."""

from __future__ import annotations

from dataclasses import dataclass, field

from .base_load_rounding import BaseLoadRounding


@dataclass(order=True)
class DiscreteWidth:
    """Structure to store float width together with its rounded integer form.

    The Base part means this class does not support arithmetic operations
    between width (and load) values. This is done to avoid circular type hints.

    BaseLoadRounding instance is needed to enable conversion between two forms.
    In practice, LoadRounding instances will be used by callers,
    but LoadRounding definition depends on DiscreteWidth,
    hence two rounding classes to avoid circular type hints.

    Conversion and arithmetic methods are added for convenience.
    Division and non-integer multiplication are intentionally not supported,
    as MLRsearch should not seek unround widths when round ones are available.
    """

    # For most debugs, rounding in repr just takes space.
    rounding: BaseLoadRounding = field(compare=False, repr=False)
    """Rounding instance to use for conversion."""
    int_width: int = field(default=None, compare=False)
    """Integer form, difference of integer loads.
    This is the primary quantity used by most computations."""
    float_width: float = None
    """Relative width of float intended load.
    This is treated as a constructor argument, and does not need to match
    the int width. Int width is computed to be no wider than this."""

    def __post_init__(self) -> None:
        """Ensure types, compute missing information.

        At this point, it is allowed for float width to be slightly larger
        than the implied int width.

        :raises RuntimeError: Is int width is not positive.
        """
        if self.float_width is None and self.int_width is None:
            raise RuntimeError(u"Float or int value is needed.")
        if self.int_width is None:
            self.float_width = float(self.float_width)
            min_load = self.rounding.int2float(0)
            increased_load = min_load / (1.0 - self.float_width)
            int_load = self.rounding.float2int(increased_load)
            verify_load = self.rounding.int2float(int_load)
            if verify_load > increased_load:
                int_load -= 1
            self.int_width = int_load
            if self.int_width <= 0:
                raise RuntimeError(f"Got non-positive iwidth: {self.int_width}")
        if self.float_width is None:
            self.int_width = int(self.int_width)
            if self.int_width <= 0:
                raise RuntimeError(f"Got non-positive iwidth: {self.int_width}")
            min_load = self.rounding.int2float(0)
            increased_load = self.rounding.int2float(self.int_width)
            self.float_width = (increased_load - min_load) / increased_load
        # TODO: Verify float is not too far from int.

    def __int__(self) -> int:
        """Return the int value.

        :returns: The int field value.
        :rtype: int
        """
        return self.int_width

    def __float__(self) -> float:
        """Return the float value.

        :returns: The float field value.
        :rtype: float
        """
        return self.float_width

    def __add__(self, width: DiscreteWidth) -> DiscreteWidth:
        """Return newly constructed instance with int widths added.

        Rounding instance (reference) is copied from self.

        Argument type is checked, to avoid caller adding something unsupported.

        :param width: Value to add to int width.
        :type width: DiscreteWidth
        :returns: New instance.
        :rtype: DiscreteWidth
        :raises RuntimeError: When argument has unexpected type.
        """
        if not isinstance(width, DiscreteWidth):
            raise RuntimeError(f"Not width: {type(width)}")
        return DiscreteWidth(
            rounding=self.rounding, int_width=self.int_width + int(width)
        )

    def __sub__(self, width: DiscreteWidth) -> DiscreteWidth:
        """Return newly constructed instance with int widths subtracted.

        Rounding instance (reference) is copied from self.

        Argument type is checked, to avoid caller adding something unsupported.
        Non-positive results are disallowed by constructor.

        :param width: Value to subtract to int width.
        :type width: DiscreteWidth
        :returns: New instance.
        :rtype: DiscreteWidth
        :raises RuntimeError: When argument has unexpected type.
        """
        if not isinstance(width, DiscreteWidth):
            raise RuntimeError(f"Not width: {type(width)}")
        return DiscreteWidth(
            rounding=self.rounding, int_width=self.int_width - int(width)
        )

    def __mul__(self, coefficient: int) -> DiscreteWidth:
        """Construct new instance with int value multiplied.

        Rounding instance (reference) is copied from self.

        :param coefficient: Constant to multiply int width with.
        :type coefficient: int
        :returns: New instance with multiplied int width.
        :rtype: DiscreteWidth
        :raises RuntimeError: If argument value does not meet requirements.
        """
        if not isinstance(coefficient, int):
            raise RuntimeError(f"Coefficient not int: {coefficient!r}")
        if coefficient < 1:
            raise RuntimeError(f"Coefficient not positive: {coefficient!r}")
        return DiscreteWidth(
            rounding=self.rounding, int_width=self.int_width * coefficient
        )
