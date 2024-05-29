# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Utility functions for handling VPP API enum values from Robot."""


from enum import Enum, IntEnum
from typing import Type, Union


# The return type is enum_class, but it is hard to explain that to pylint.
def get_enum_instance(
    enum_class: Type[Enum], value: Union[Enum, str, int, None]
) -> Enum:
    """Return an enum instance matching the string name.

    In Robot, it is not convenient to construct Enum instances,
    most values defined in Robot are strings.

    This helper function can be used in Python L1 keywords
    to convert string into the corresponding Enum instance.
    Aliases are also recognized.

    As a common shortcut, value is returned it it already is an instance.

    Another convenience: None or empty string is processed as "NONE".

    As an added benefit, support various Robot-like niceties,
    like lower case, or dash or space instead of underscore.
    Also strip the identifiers, this is mostly due to "3DES".
    Enum instance cannot start with a number, so "_3DES" + strip is needed.

    If the class is a subclass of IntEnum, int values
    and (string) values convertable to int are also accepted as input.

    :param enum_class: Class object instance of which should be returned.
    :param value: String or any other recognized form of an enum instance.
    :type enum_class: Type[Enum]
    :type value: Union[enum_class, str, int, None]
    :returns: The matching instance, if found.
    :rtype: enum_class
    :raises: ValueError if no matching instance is found.
    """
    if issubclass(enum_class, IntEnum):
        try:
            int_value = int(value)
            return enum_class(int_value)
        except (TypeError, ValueError):
            pass
    if isinstance(value, enum_class):
        return value
    if not value:
        value = "NONE"
    normalized_name = str(value).upper().replace("-", " ").replace("_", " ")
    members = enum_class.__members__  # Includes aliases, useful for NONE.
    for member_name in members:
        if normalized_name.strip() == member_name.replace("_", " ").strip():
            return members[member_name]
    msg = f"Enum class {enum_class} does not have value {normalized_name!r}"
    raise ValueError(msg)
