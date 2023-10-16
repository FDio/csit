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

"""Module defining secondary_field function.

Just a shrothand for frequently repeated expression.

The main point is that this dataclass field is not used in init.
Maybe it is a derived value of a frozen dataclass.
Maybe it is a cache to help avoiding repeated computation.
Maybe it is a temporary value stored in one method and read in another method.
In any case, the caller does not need to know it is here,
so it is excluded from repr, hashing, ordering and similar.
"""

from dataclasses import Field, field


def secondary_field() -> Field:
    """Return newly created Field with non-default arguments

    In practice, it seems to be fine to reuse the resulting Field instance
    when defining multiple dataclass fields,
    but we keep this as a function to improve readability.

    :returns: A new Field instance useful for secondary fields.
    :rtype: Field
    """
    return field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )
