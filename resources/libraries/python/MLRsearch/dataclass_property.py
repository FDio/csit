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

"""Module defining some utility functions to serve as a syntactic sugar.

The main issue that needs support is dataclasses with properties
(including setters) and with default values, including mutable ones
(meaning default_factory would ordinarilty be used).

First, this explains how property ends up passes as default constructor value:
https://florimond.dev/en/posts/2018/10/reconciling-dataclasses-and-properties-in-python/
TL;DR: By the time __init__ is generated, original class variable (type hint)
is replaced by property (method definition).

Second, there are ways to deal with that:
https://stackoverflow.com/a/61480946
TL;DR: It relies on the underscored field being replaced by the value.

But that does not work for field which use default_factory
(the underscored class field is deleted instead).

So another way is needed to store a mutable default value,
so setter can use it when called with property instead of value.

This implementation relies on a fact that decorators are executed
when the class field do exist, and decorated function
does know its name, so the decorator can get the value stored in
class field, and store it as an additional attribute for the function.
Then for setter, the property contains the getter (as an unbound function),
so it can access the additional attribute to get the value.

This approach circumvents the precautions dataclasses take to prevent mishaps
when a single mutable object is shared between multiple instances.
So it is up to setters to create an appropriate copy of the default object.
"""

from __future__ import annotations

from functools import wraps
from inspect import stack
from typing import Callable, TypeVar, Union


Self = TypeVar(u"Self")
"""Type for the dataclass instances being created using properties."""
Value = TypeVar(u"Value")
"""Type for the value the property (getter, setter) handles."""
Setter = Callable[[Self, Value], None]
"""Short for the setter type."""

def _calling_scope_variable(name: str) -> Value:
    """Get a variable from a higher scope.

    This feels dirty, but without this the syntaxtic sugar
    would not be sweet enough.

    The implementation is copied from https://stackoverflow.com/a/14694234
    with the difference of raising (instead of returning None) if not found.

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


class dataclass_property(property):
    """Subclass of property, handles default values for dataclass fields.

    If a dataclass field does not specify a default value (nor default_factory),
    this is not needed, and in fact it will not work (so use builtin property).

    Read this to understand why properties are tricky in dataclasses:
    https://florimond.dev/en/posts/2018/10/reconciling-dataclasses-and-properties-in-pyt

    Read this for other approaches that work for defaults
    (but not for default_factory):
    https://stackoverflow.com/a/61480946

    This implementation transparently finds and inserts the default value
    (can be mutable) into a new attribute of the getter function.
    Before calling a setter function in init (recognized by type),
    the default value is retrieved and passed transparently to the setter.
    It is the responsibilty of the setter to duplicate the value,
    in order to prevent multiple instances sharing the same mutable value.
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        """Find and store the default value, construct the property.

        See this for how the the superclass property works:
        https://docs.python.org/3/howto/descriptor.html#properties
        """
        # TODO: Add type hints and argument descriptions.
        default_value = _calling_scope_variable(fget.__name__)
        if not isinstance(default_value, dataclass_property):
            fget.default_value = _calling_scope_variable(fget.__name__)
        # Else this is the second time init is call (when setting setter),
        # in which case the default is already stored into fget.
        super().__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)

    def setter(self: dataclass_property, fset: Setter) -> dataclass_property:
        """Set a setter after wrapping it.

        The wrapping layer recongnizes when setter is called in init
        (by the fact the value argument is of type property)
        and in that case extract the stored default and pass that
        to the user-defined setter.
        """
        @wraps(fset)
        def wrapped(sel_: Self, val: Union[Value, dataclass_property]) -> None:
            """Extract default from getter if needed, call the user setter."""
            if isinstance(val, dataclass_property):
                val = val.fget.default_value
            fset(sel_, val)
        return super().setter(wrapped)
