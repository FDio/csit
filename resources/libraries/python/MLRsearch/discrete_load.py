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

"""Module defining DiscreteLoad class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Union

from .load_rounding import LoadRounding
from .discrete_width import DiscreteWidth


@dataclass(order=True)
class DiscreteLoad:
    """Structure to store load value together with its rounded integer form.

    LoadRounding instance is needed to enable conversion between two forms.
    (BaseLoadRounding would suffice, but LoadRounding is more convenient.)
    Conversion methods and factories are added for convenience.

    In general, the int form is allowed to differ from conversion from int.

    Comparisons are supported, acting on the float load component.
    Additive operations are supported, acting on int form.
    Multiplication by a float constant is supported, acting on float form.

    As for all user defined classes by default, all instances are truthy.
    That is useful when dealing with Optional values, as None is falsy.
    """

    # For most debugs, rounding in repr just takes space.
    rounding: LoadRounding = field(compare=False, repr=False)
    """Rounding instance to use for conversion."""
    float_load: float = None
    """Float form of intended load [tps], usable for measurer."""
    int_load: int = field(compare=False, default=None)
    """Integer form, usable for exact computations."""

    def __post_init__(self) -> None:
        """Ensure types, compute missing information.

        At this point, it is allowed for float load to differ from
        conversion from int load. MLR should round explicitly later,
        based on its additional information.
        """
        if self.float_load is None and self.int_load is None:
            raise RuntimeError(u"Float or int value is needed.")
        if self.float_load is None:
            self.int_load = int(self.int_load)
            self.float_load = self.rounding.int2float(self.int_load)
        else:
            self.float_load = float(self.float_load)
            self.int_load = self.rounding.float2int(self.float_load)

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
            """Use rounding and float load to create discrete load.

            :param int_load: Intended load in float form [tps].
            :type int_load: float
            :returns: New discrete load instance matching the float load.
            :rtype: DiscreteLoad
            """
            return DiscreteLoad(rounding=rounding, float_load=float_load)
        return factory_float

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
            raise RuntimeError(f"Not width: {type(width)}")
        return DiscreteLoad(
            rounding=self.rounding, int_load=self.int_load + int(width)
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
        raise RuntimeError(f"Unsupported type {type(other)}")

    def _minus_width(self, width: DiscreteWidth) -> DiscreteLoad:
        """Return newly constructed instance, width subtracted from int load.

        Rounding instance (reference) is copied from self.

        :param width: Value to subtract from int load.
        :type width: DiscreteWidth
        :returns: New instance.
        :rtype: DiscreteLoad
        """
        return DiscreteLoad(
            rounding=self.rounding, int_load=self.int_load - int(width)
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
            rounding=self.rounding, int_width=self.int_load - int(other)
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
            rounding=self.rounding, float_load=self.float_load * coefficient
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
