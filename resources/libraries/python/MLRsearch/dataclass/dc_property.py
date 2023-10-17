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

"""Module defining DataclassProperty class.

The main issue that needs support is dataclasses with properties
(including setters) and with (immutable) default values.

First, this explains how property ends up passed as default constructor value:
https://florimond.dev/en/posts/2018/10/
/reconciling-dataclasses-and-properties-in-python/
TL;DR: By the time __init__ is generated, original class variable (type hint)
is replaced by property (method definition).

Second, there are ways to deal with that:
https://stackoverflow.com/a/61480946
TL;DR: It relies on the underscored field being replaced by the value.

But that does not work for field which use default_factory (or no default)
(the underscored class field is deleted instead).
So another way is needed to cover those cases,
ideally without the need to define both original and underscored field.

This implementation relies on a fact that decorators are executed
when the class fields do yet exist, and decorated function
does know its name, so the decorator can get the value stored in
the class field, and store it as an additional attribute of the getter function.
Then for setter, the property contains the getter (as an unbound function),
so it can access the additional attribute to get the value.

This approach circumvents the precautions dataclasses take to prevent mishaps
when a single mutable object is shared between multiple instances.
So it is up to setters to create an appropriate copy of the default object
if the default value is mutable.

The default value cannot be MISSING nor Field nor DataclassProperty,
otherwise the intended logic breaks.
"""

from __future__ import annotations

from dataclasses import Field, MISSING
from functools import wraps
from inspect import stack
from typing import Callable, Optional, TypeVar, Union


Self = TypeVar("Self")
"""Type for the dataclass instances being created using properties."""
Value = TypeVar("Value")
"""Type for the value the property (getter, setter) handles."""


def _calling_scope_variable(name: str) -> Value:
    """Get a variable from a higher scope.

    This feels dirty, but without this the syntactic sugar
    would not be sweet enough.

    The implementation is copied from https://stackoverflow.com/a/14694234
    with the difference of raising RuntimeError (instead of returning None)
    if no variable of that name is found in any of the scopes.

    :param name: Name of the variable to access.
    :type name: str
    :returns: The value of the found variable.
    :rtype: Value
    :raises RuntimeError: If the variable is not found in any calling scope.
    """
    frame = stack()[1][0]
    while name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            raise RuntimeError(f"Field {name} value not found.")
    return frame.f_locals[name]


class DataclassProperty(property):
    """Subclass of property, handles default values for dataclass fields.

    If a dataclass field does not specify a default value (nor default_factory),
    this is not needed, and in fact it will not work (so use built-in property).

    This implementation seemlessly finds and inserts the default value
    (can be mutable) into a new attribute of the getter function.
    Before calling a setter function in init (recognized by type),
    the default value is retrieved and passed transparently to the setter.
    It is the responsibilty of the setter to appropriately clone the value,
    in order to prevent multiple instances sharing the same mutable value.
    """

    def __init__(
        self,
        fget: Optional[Callable[[], Value]] = None,
        fset: Optional[Callable[[Self, Value], None]] = None,
        fdel: Optional[Callable[[], None]] = None,
        doc: Optional[str] = None,
    ):
        """Find and store the default value, construct the property.

        See this for how the superclass property works:
        https://docs.python.org/3/howto/descriptor.html#properties

        :param fget: Getter (unbound) function to use, if any.
        :param fset: Setter (unbound) function to use, if any.
        :param fdel: Deleter (unbound) function to use, if any.
        :param doc: Docstring to display when examining the property.
        :type fget: Optional[Callable[[Self], Value]]
        :type fset: Optional[Callable[[Self, Value], None]]
        :type fdel: Optional[Callable[[Self], None]]
        :type doc: Optional[str]
        """
        variable_found = _calling_scope_variable(fget.__name__)
        if not isinstance(variable_found, DataclassProperty):
            if isinstance(variable_found, Field):
                if variable_found.default is not MISSING:
                    fget.default_value = variable_found.default
                # Else do not store any default value.
            else:
                fget.default_value = variable_found
        # Else this is the second time init is called (when setting setter),
        # in which case the default is already stored into fget.
        super().__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)

    def setter(
        self,
        fset: Optional[Callable[[Self, Value], None]],
    ) -> DataclassProperty:
        """Return new instance with a wrapped setter function set.

        If the argument is None, call superclass method.

        The wrapped function recognizes when it is called in init
        (by the fact the value argument is of type DataclassProperty)
        and in that case it extracts the stored default and passes that
        to the user-defined setter function.

        :param fset: Setter function to wrap and apply.
        :type fset: Optional[Callable[[Self, Value], None]]
        :returns: New property instance with correct setter function set.
        :rtype: DataclassProperty
        """
        if fset is None:
            return super().setter(fset)

        @wraps(fset)
        def wrapped(sel_: Self, val: Union[Value, DataclassProperty]) -> None:
            """Extract default from getter if needed, call the user setter.

            The sel_ parameter is listed explicitly, to signify
            this is an unbound function, not a bounded method yet.

            :param sel_: Instance of dataclass (not of DataclassProperty)
                to set the value on.
            :param val: Set this value, or the default value stored there.
            :type sel_: Self
            :type val: Union[Value, DataclassProperty]
            """
            if isinstance(val, DataclassProperty):
                val = val.fget.default_value
            fset(sel_, val)

        return super().setter(wrapped)
