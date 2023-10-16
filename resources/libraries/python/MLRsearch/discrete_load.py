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

"""Module defining DiscreteLoad class."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import total_ordering
from typing import Callable, Optional, Union

from .load_rounding import LoadRounding
from .discrete_width import DiscreteWidth


@total_ordering
@dataclass
class DiscreteLoad:
    """Structure to store load value together with its rounded integer form.

    LoadRounding instance is needed to enable conversion between two forms.
    Conversion methods and factories are added for convenience.

    In general, the float form is allowed to differ from conversion from int.

    Comparisons are supported, acting on the float load component.
    Additive operations are supported, acting on int form.
    Multiplication by a float constant is supported, acting on float form.

    As for all user defined classes by default, all instances are truthy.
    That is useful when dealing with Optional values, as None is falsy.

    This dataclass is effectively frozen, but cannot be marked as such
    as that would prevent LoadStats from being its subclass.
    """

    # For most debugs, rounding in repr just takes space.
    rounding: LoadRounding = field(repr=False, compare=False)
    """Rounding instance to use for conversion."""
    float_load: float = None
    """Float form of intended load [tps], usable for measurer."""
    int_load: int = field(compare=False, default=None)
    """Integer form, usable for exact computations."""

    def __post_init__(self) -> None:
        """Ensure types, compute missing information.

        At this point, it is allowed for float load to differ from
        conversion from int load. MLRsearch should round explicitly later,
        based on its additional information.

        :raises RuntimeError: If both init arguments are None.
        """
        if self.float_load is None and self.int_load is None:
            raise RuntimeError("Float or int value is needed.")
        if self.float_load is None:
            self.int_load = int(self.int_load)
            self.float_load = self.rounding.int2float(self.int_load)
        else:
            self.float_load = float(self.float_load)
            self.int_load = self.rounding.float2int(self.float_load)

    def __str__(self) -> str:
        """Convert to a short human-readable string.

        :returns: The short string.
        :rtype: str
        """
        return f"int_load={int(self)}"

    # Explicit comparison operators.
    # Those generated with dataclass order=True do not allow subclass instances.

    def __eq__(self, other: Optional[DiscreteLoad]) -> bool:
        """Return whether the other instance has the same float form.

        None is effectively considered to be an unequal instance.

        :param other: Other instance to compare to, or None.
        :type other: Optional[DiscreteLoad]
        :returns: True only if float forms are exactly equal.
        :rtype: bool
        """
        if other is None:
            return False
        return float(self) == float(other)

    def __lt__(self, other: DiscreteLoad) -> bool:
        """Return whether self has smaller float form than the other instance.

        None is not supported, as MLRsearch does not need that
        (so when None appears we want to raise).

        :param other: Other instance to compare to.
        :type other: DiscreteLoad
        :returns: True only if float forms of self is strictly smaller.
        :rtype: bool
        """
        return float(self) < float(other)

    def __hash__(self) -> int:
        """Return a hash based on the float value.

        With this, the instance can be used as if it was immutable and hashable,
        e.g. it can be a key in a dict.

        :returns: Hash value for this instance.
        :rtype: int
        """
        return hash(float(self))

    @property
    def is_round(self) -> bool:
        """Return whether float load matches converted int load.

        :returns: False if float load is not rounded.
        :rtype: bool
        """
        expected = self.rounding.int2float(self.int_load)
        return expected == self.float_load

    def __int__(self) -> int:
        """Return the int value.

        :returns: The int field value.
        :rtype: int
        """
        return self.int_load

    def __float__(self) -> float:
        """Return the float value.

        :returns: The float field value [tps].
        :rtype: float
        """
        return self.float_load

    @staticmethod
    def int_conver(rounding: LoadRounding) -> Callable[[int], DiscreteLoad]:
        """Return a factory that turns an int load into a discrete load.

        :param rounding: Rounding instance needed.
        :type rounding: LoadRounding
        :returns: Factory to use when converting from int.
        :rtype: Callable[[int], DiscreteLoad]
        """

        def factory_int(int_load: int) -> DiscreteLoad:
            """Use rounding and int load to create discrete load.

            :param int_load: Intended load in integer form.
            :type int_load: int
            :returns: New discrete load instance matching the int load.
            :rtype: DiscreteLoad
            """
            return DiscreteLoad(rounding=rounding, int_load=int_load)

        return factory_int

    @staticmethod
    def float_conver(rounding: LoadRounding) -> Callable[[float], DiscreteLoad]:
        """Return a factory that turns a float load into a discrete load.

        :param rounding: Rounding instance needed.
        :type rounding: LoadRounding
        :returns: Factory to use when converting from float.
        :rtype: Callable[[float], DiscreteLoad]
        """

        def factory_float(float_load: float) -> DiscreteLoad:
            """Use rounding instance and float load to create discrete load.

            The float form is not rounded yet.

            :param int_load: Intended load in float form [tps].
            :type int_load: float
            :returns: New discrete load instance matching the float load.
            :rtype: DiscreteLoad
            """
            return DiscreteLoad(rounding=rounding, float_load=float_load)

        return factory_float

    def rounded_down(self) -> DiscreteLoad:
        """Create and return new instance with float form matching int.

        :returns: New instance with same int form and float form rounded down.
        :rtype: DiscreteLoad
        """
        return DiscreteLoad(rounding=self.rounding, int_load=int(self))

    def hashable(self) -> DiscreteLoad:
        """Return new equivalent instance.

        This is mainly useful for conversion from unhashable subclasses,
        such as LoadStats.
        Rounding instance (reference) is copied from self.

        :returns: New instance with values based on float form of self.
        :rtype: DiscreteLoad
        """
        return DiscreteLoad(rounding=self.rounding, float_load=float(self))

    def __add__(self, width: DiscreteWidth) -> DiscreteLoad:
        """Return newly constructed instance with width added to int load.

        Rounding instance (reference) is copied from self.

        Argument type is checked, to avoid caller adding two loads by mistake
        (or adding int to load and similar).

        :param width: Value to add to int load.
        :type width: DiscreteWidth
        :returns: New instance.
        :rtype: DiscreteLoad
        :raises RuntimeError: When argument has unexpected type.
        """
        if not isinstance(width, DiscreteWidth):
            raise RuntimeError(f"Not width: {width!r}")
        return DiscreteLoad(
            rounding=self.rounding,
            int_load=self.int_load + int(width),
        )

    def __sub__(
        self, other: Union[DiscreteWidth, DiscreteLoad]
    ) -> Union[DiscreteLoad, DiscreteWidth]:
        """Return result based on the argument type.

        Load minus load is width, load minus width is load.
        This allows the same operator to support both operations.

        Rounding instance (reference) is copied from self.

        :param other: Value to subtract from int load.
        :type other: Union[DiscreteWidth, DiscreteLoad]
        :returns: Resulting width or load.
        :rtype: Union[DiscreteLoad, DiscreteWidth]
        :raises RuntimeError: If the argument type is not supported.
        """
        if isinstance(other, DiscreteWidth):
            return self._minus_width(other)
        if isinstance(other, DiscreteLoad):
            return self._minus_load(other)
        raise RuntimeError(f"Unsupported type {other!r}")

    def _minus_width(self, width: DiscreteWidth) -> DiscreteLoad:
        """Return newly constructed instance, width subtracted from int load.

        Rounding instance (reference) is copied from self.

        :param width: Value to subtract from int load.
        :type width: DiscreteWidth
        :returns: New instance.
        :rtype: DiscreteLoad
        """
        return DiscreteLoad(
            rounding=self.rounding,
            int_load=self.int_load - int(width),
        )

    def _minus_load(self, other: DiscreteLoad) -> DiscreteWidth:
        """Return newly constructed width instance, difference of int loads.

        Rounding instance (reference) is copied from self.

        :param other: Value to subtract from int load.
        :type other: DiscreteLoad
        :returns: New instance.
        :rtype: DiscreteWidth
        """
        return DiscreteWidth(
            rounding=self.rounding,
            int_width=self.int_load - int(other),
        )

    def __mul__(self, coefficient: float) -> DiscreteLoad:
        """Return newly constructed instance, float load multiplied by argument.

        Rounding instance (reference) is copied from self.

        :param coefficient: Value to multiply float load with.
        :type coefficient: float
        :returns: New instance.
        :rtype: DiscreteLoad
        :raises RuntimeError: If argument is unsupported.
        """
        if not isinstance(coefficient, float):
            raise RuntimeError(f"Not float: {coefficient!r}")
        if coefficient <= 0.0:
            raise RuntimeError(f"Not positive: {coefficient!r}")
        return DiscreteLoad(
            rounding=self.rounding,
            float_load=self.float_load * coefficient,
        )

    def __truediv__(self, coefficient: float) -> DiscreteLoad:
        """Call multiplication with inverse argument.

        :param coefficient: Value to divide float load with.
        :type coefficient: float
        :returns: New instance.
        :rtype: DiscreteLoad
        :raises RuntimeError: If argument is unsupported.
        """
        return self * (1.0 / coefficient)
