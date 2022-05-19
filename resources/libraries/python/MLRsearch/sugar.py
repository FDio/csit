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
(meaning default factory is used).

First, this explains how property ends up passes as default constructor value:
https://florimond.dev/en/posts/2018/10/reconciling-dataclasses-and-properties-in-python/
TL;DR: By the time __init__ is generated, original class variable (type hint)
is replaced by property (method definition).

Second, there is a way to deal with that:
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
Then in setter, the property (method) contains the getter (unbound function),
so it can access the additional attribute to get the value.

This approach circumvents the precautions dataclasses take to prevent mishaps
when a single mutable object is shared between multiple instances.
So it is up to setters to create a copy of the default object.

If you see a "property" (without quotes) in the code, it means
the type of created property function.
If you see @property, it means the decorator that turns functions
into properties (the function becoming the getter of that property).
"""

from inspect import stack
from typing import Callable, TypeVar, Optional, Union


S = TypeVar(u"S")  # Type of "self" the functions below support.
V = TypeVar(u"V")  # Type of "value" the functions below support.


def _calling_scope_variable(name: str) -> V:
    """Get a variable from a higher scope.

    This feels dirty, but without this the syntaxtic sugar
    would not be sweet enough.

    The implementation is copied from https://stackoverflow.com/a/14694234
    with the difference of raising (instead of returning None) if not found.

    :param name: Name of the variable to access.
    :type name: str
    :returns: The value of the found variable.
    :rtype: V
    :raises RuntimeError: If the variable is not found in any calling scope.
    """
    frame = stack()[1][0]
    while name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            raise RuntimeError(f"Field {name} value not found.")
    return frame.f_locals[name]


def property_with_default(getter_function: Callable[[S], V]) -> property:
    """Create a property which "remembers" its default value.

    Use as a decorator, @property_with_default instead of @property.

    The default value is read from a class variable of the same name,
    which is assumed to be defined (or otherwise found in calling context).
    The getter function does need to have name defined.
    (It does if defined in the usual way getters are written.)

    The implementation adds an atribute "default_value" into the function
    before passing it to @property decorator.
    That means if the function already has a default_value attribute,
    its value is lost.

    :param getter_function: The future getter function of the created property.
    :type function: Callable[[S], V]
    :returns: The created property.
    :rtype: property
    """
    getter_function.default = _calling_scope_variable(getter_function.__name__)
    return property(function)


def or_from_property(value: Union[V, property]) -> V:
    """Return value given, or extracted from (getter of) property.

    Typical code in a setter: "value = or_from_property(value)".

    When called from (dataclass created) init, that line puts
    the intended default value into the variable
    (assuming @property_with_default(default_value) was used).

    When called externally, the value is preserved.
    Obviously, that only works when isinstance does not consider
    the value to be a property.

    :param value: External value to preserve (or property to extract from).
    :type value: Union[V, property]
    :returns: Given or default (read from property getter attribute) value.
    :rtype: V
    """
    return value.fget.default_value if isinstance(value, property) else value
