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

"""Module for converting in-memory data into raw JSON output.

CSIT and VPP PAPI are using custom data types
that are not directly serializable into JSON.

Thus, before writing the raw outpt onto disk,
the data is recursively converted to equivalent serializable types,
in extreme cases replaced by string representation.

Validation is outside the scope of this module,
as it should use the JSON data read from disk.
"""

from collections.abc import Mapping, Iterable
from enum import IntFlag

from resources.libraries.python.model.json_io import dump_into


def _pre_serialize_recursive(data):
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
    # Recurse over, convert and sort mappings.
    if isinstance(data, Mapping):
        # Convert and sort alphabetically.
        ret = {
            str(key): _pre_serialize_recursive(data[key])
            for key in sorted(data.keys())
        }
        # If exists, move "data" field to the end.
        data_value = ret.pop(u"data", None)
        if data_value is not None:
            ret[u"data"] = data_value
        return ret
    # Recurse over and convert iterables.
    if isinstance(data, Iterable):
        return [_pre_serialize_recursive(item) for item in data]
    # Unknown structure, attempt str().
    return str(data)


def _pre_serialize_root(data):
    """Recursively convert to a more serializable form, tweak order.

    See _pre_serialize_recursive for most of changes this does.

    The logic here (outside the recursive function) only affects
    field ordering in the root mapping,
    to make it more human friendly.
    We are moving "version" to the top,
    followed by start time and end time.
    and various long fields (such as "log") to the bottom.

    Some edits are done in-place, do not trust the argument value after calling.

    :param data: Root data to make serializable, dictized when applicable.
    :type data: dict
    :returns: Order-tweaked version of the argument.
    :rtype: dict
    :raises KeyError: If the data does not contain required fields.
    :raises TypeError: If the argument is not a dict.
    :raises ValueError: If the argument does not support string conversion.
    """
    if not isinstance(data, dict):
        raise RuntimeError(f"Root data object needs to be a dict: {data!r}")
    data = _pre_serialize_recursive(data)
    log = data.pop(u"log")
    new_data = dict(version=data.pop(u"version"))
    new_data[u"start_time"] = data.pop(u"start_time")
    new_data[u"end_time"] = data.pop(u"end_time")
    new_data.update(data)
    new_data[u"log"] = log
    return new_data


def write_raw_output(raw_file_path, raw_data):
    """Prepare data for serialization and dump into a file.

    Ancestor directories are created if needed.

    :param to_raw_path: Local filesystem path, including the file name.
    :type to_raw_path: str
    """
    raw_data = _pre_serialize_root(raw_data)
    dump_into(raw_data, raw_file_path)
