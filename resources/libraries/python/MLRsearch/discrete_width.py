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

"""Module defining DiscreteWidth class."""

from __future__ import annotations

from dataclasses import dataclass, field

from .load_rounding import LoadRounding


# TODO: Make properly frozen.
@dataclass(order=True)
class DiscreteWidth:
    """Structure to store float width together with its rounded integer form.

    The width does not have to be positive, i.e. the computed integer width
    does not have to be larger than zero.

    LoadRounding instance is needed to enable conversion between two forms.

    Conversion and arithmetic methods are added for convenience.
    Division and non-integer multiplication are intentionally not supported,
    as MLRsearch should not seek unround widths when round ones are available.

    The instance is effectively immutable, but not hashable as it refers
    to the rounding instance, which is implemented as mutable
    (although the mutations are not visible).
    """

    # For most debugs, rounding in repr just takes space.
    rounding: LoadRounding = field(repr=False, compare=False)
    """Rounding instance to use for conversion."""
    float_width: float = None
    """Relative width of float intended load.
    This is treated as a constructor argument, and does not need to match
    the int width. Int width is computed to be no wider than this."""
    int_width: int = field(compare=False, default=None)
    """Integer form, difference of integer loads.
    This is the primary quantity used by most computations."""

    def __post_init__(self) -> None:
        """Ensure types, compute missing information.

        At this point, it is allowed for float width to be slightly larger
        than the implied int width.

        If both forms are specified, the float form is taken as primary
        (thus the integer form is recomputed to match).

        :raises RuntimeError: If both init arguments are None.
        """
        if self.float_width is None and self.int_width is None:
            raise RuntimeError("Float or int value is needed.")
        if self.float_width is None:
            self.int_width = int(self.int_width)
            min_load = self.rounding.int2float(0)
            increased_load = self.rounding.int2float(self.int_width)
            self.float_width = (increased_load - min_load) / increased_load
            return
        self.float_width = float(self.float_width)
        min_load = self.rounding.int2float(0)
        increased_load = min_load / (1.0 - self.float_width)
        int_load = self.rounding.float2int(increased_load)
        verify_load = self.rounding.int2float(int_load)
        if verify_load > increased_load:
            int_load -= 1
        self.int_width = int_load

    def __str__(self) -> str:
        """Convert into a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return f"int_width={int(self)}"

    def __int__(self) -> int:
        """Return the integer form.

        :returns: The int field value.
        :rtype: int
        """
        return self.int_width

    def __float__(self) -> float:
        """Return the float form.

        :returns: The float field value.
        :rtype: float
        """
        return self.float_width

    def __hash__(self) -> int:
        """Return a hash based on the float value.

        With this, the instance can be used as if it was immutable and hashable,
        e.g. it can be a key in a dict.

        :returns: Hash value for this instance.
        :rtype: int
        """
        return hash(float(self))

    def rounded_down(self) -> DiscreteWidth:
        """Create and return new instance with float form matching int.

        :returns: New instance with same int form and float form rounded down.
        :rtype: DiscreteWidth
        """
        return DiscreteWidth(rounding=self.rounding, int_width=int(self))

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
            raise RuntimeError(f"Not width: {width!r}")
        return DiscreteWidth(
            rounding=self.rounding,
            int_width=self.int_width + int(width),
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
            rounding=self.rounding,
            int_width=self.int_width - int(width),
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
            rounding=self.rounding,
            int_width=self.int_width * coefficient,
        )

    def half_rounded_down(self) -> DiscreteWidth:
        """Contruct new instance of half the integer width.

        If the current integer width is odd, round the half width down.

        :returns: New instance with half int width.
        :rtype: DiscreteWidth
        :raises RuntimeError: If the resulting integerl width is not positive.
        """
        return DiscreteWidth(
            rounding=self.rounding,
            int_width=self.int_width // 2,
        )
