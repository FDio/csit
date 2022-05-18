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

"""Module defining utility functions to enhande dataclass usage.

Two links for details on interaction between dataclasses and properties:
  https://florimond.dev/en/posts/2018/10/reconciling-dataclasses-and-properties-in-python/
  https://stackoverflow.com/a/61480946

Using this gist would be more convenient:
  https://gist.github.com/rnag/d14b05680094b871935a9a30d43d5c0d
but as it does not come with a license, we cannot.

This is to support the first way.
The situation with mutable defaults is even more complicated,
so the code is worth be moved into functions.
"""

from dataclasses import field, Field
from typing import Any, Iterable, List, Protocol






class IsDataclass(Protocol):
    """Typing hint for dataclass instances.

    https://stackoverflow.com/a/55240861
    """
    __dataclass_fields__: Dict


def scalar_default(default: Any) -> Field:
    """Generate Field for private fields with scalar default value.

    Nothing fancy here, just for completeness and shorter lines.

    :param default: Default value to use for this field.
    :type default: Any
    """
    return field(init=False, repr=False, default=default)


def list_default(default: Iterable[Any]) -> Field:
    """Generate Field for private fields with list default value.

    This has some logic to ensure mutations are not shared.

    :param default: Default value to use for this field.
    :type default: Iterable[Any[
    """
    # Iterate only once.
    default = list(default)
    # Copy on each factory invocation.
    return field(
        init=False, repr=False, default_factory=lambda: list(default)
    )



def or_scalar_default(
    dataclazz: IsDataclass, value: Any, field_name: str
) -> Any:
    """Value if not property else default of given declared field.

    The argument order is suitable for binding to a class,
    turning this function into its method.

    There is no easy way to avoid the need for the field name,
    as in typical case (field name starts with underscore
    but value is the property not startsin"""




def property_with_default(default: Any) -> property:
    """"""
    def closure(function: Callable[Any, Any]):
        """"""
        propertied = property(function)
        propertied.default = default
        return propertied
    return closure
