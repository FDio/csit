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


from enum import Enum
from typing import Type


# The return type is enum_type, but it is hard to explain that to pylint.
def get_enum_instance(enum_class: Type[Enum], value_name: str) -> Enum:
    """Return an enum instance matching the string name.

    In Robot, it is not convenient to construct Enum instances,
    most values defined in Robot are strings.

    This helper function can be used by Python L1 keywords
    to "convert" string into an Enum instance.

    As an added benefit, ignore common mistakes
    like lowercase or dash instead of underscore.

    As a common shortcut, value_name is returned it it already is an instance.

    Another convenience: None is processed as "NONE".

    :param enum_class: Class object instance of which should be returned.
    :param value_name: String matching the intended instance.
    :type enum_class: Type[Enum]
    :type value_name: Union[str, enum_class]
    :returns: The matching instance, if found.
    :rtype: enum_class
    :raises: ValueError if the instance is not found.
    """
    if isinstance(value_name, enum_class):
        return value_name
    if not value_name:
        value_name = "NONE"
    normalized_name = str(value_name).upper().replace("-", "_")
    members = enum_class.__members__  # Includes aliases, useful for NONE.
    if normalized_name not in members:
        msg = f"Enum class {enum_class} does not have value {normalized_name!r}"
        raise ValueError(msg)
    return members[normalized_name]
