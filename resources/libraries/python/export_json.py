# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""FIXME."""

from collections.abc import Mapping, Iterable
from copy import deepcopy
from enum import IntFlag
import json

from resources.libraries.python.ip_types import (
    UnionAddress, Address, AddressWithPrefix,
)

def pre_serialize_recursive(data):
    """Recursively sort and convert to a more serializable form.

    VPP PAPI code can give data with its own MACAddres type,
    or various other enum and flag types.
    The default json.JSONEncoder method raises TypeError on that.
    First point of this function is to apply str() or repr()
    to leaf values that need it.

    Also, PAPI responses are namedtuples, which confuses
    the json.JSONEncoder method (so it does not recurse).
    Dictization (see PapiExecutor) helps somewhat, but it turns namedtuple
    into a UserDict, which also confuses json.JSONEncoder.
    Therefore, we recursively convert any Mapping into an ordinary dict.

    We also convert iterables to list,
    and prevent numbers from getting converted to strings.

    As we are doing such low level operations,
    we also convert mapping keys to strings
    and sort the mapping items by keys alphabetically,
    except "data" field moved to the end.

    :param data: Object to make serializable, dictized when applicable.
    :type data: object
    :returns: Serializable equivalent of the argument.
    :rtype: object
    :raises ValueError: If the argument does not support string conversion.
    """
    # Recursion ends at scalar values, first handle irregular ones.
    if isinstance(data, IntFlag):
        return repr(data)
    if isinstance(data, bytes):
        return data.hex()
    # The regular ones are good to go.
    if isinstance(data, (str, int, float, bool)):
        return data
    # For VAT2, do not consider ip_types as dicts.
    if isinstance(data, (UnionAddress, Address, AddressWithPrefix)):
        return str(data)
    # Recurse over, convert and sort mappings.
    if isinstance(data, Mapping):
        # Convert and sort alphabetically.
        ret = {
            str(key): pre_serialize_recursive(data[key])
            for key in sorted(data)
        }
        # If exists, move "data" field to the end.
        data_value = ret.pop(u"data", None)
        if data_value is not None:
            ret[u"data"] = data_value
        return ret
    # Recurse over and convert other iterables.
    if isinstance(data, Iterable):
        return [pre_serialize_recursive(item) for item in data]
    # Unknown structure, attempt str().
    return str(data)
