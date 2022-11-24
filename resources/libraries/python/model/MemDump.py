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

"""Module for converting in-memory data into JSON output.

CSIT and VPP PAPI are using custom data types that are not directly serializable
into JSON.

Thus, before writing the output onto disk, the data is recursively converted to
equivalent serializable types, in extreme cases replaced by string
representation.

Validation is outside the scope of this module, as it should use the JSON data
read from disk.
"""

import json
import os

from collections.abc import Iterable, Mapping, Set
from enum import IntFlag
from dateutil.parser import parse


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

    We also convert iterables to list (sorted if the iterable was a set),
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
        if u"data" in ret:
            data_value = ret.pop(u"data")
            ret[u"data"] = data_value
        # If exists, move "type" field at the start.
        if u"type" in ret:
            type_value = ret.pop(u"type")
            ret_old = ret
            ret = dict(type=type_value)
            ret.update(ret_old)
        return ret
    # Recurse over and convert iterables.
    if isinstance(data, Iterable):
        list_data = [_pre_serialize_recursive(item) for item in data]
        # Additionally, sets are exported as sorted.
        if isinstance(data, Set):
            list_data = sorted(list_data)
        return list_data
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
    and various long fields to the bottom.

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
    new_data = dict(version=data.pop(u"version"))
    new_data[u"start_time"] = data.pop(u"start_time")
    new_data[u"end_time"] = data.pop(u"end_time")
    new_data.update(data)
    return new_data


def _merge_into_suite_info_file(teardown_path):
    """Move setup and teardown data into a singe file, remove old files.

    The caller has to confirm the argument is correct, e.g. ending in
    "/teardown.info.json".

    :param teardown_path: Local filesystem path to teardown file.
    :type teardown_path: str
    :returns: Local filesystem path to newly created suite file.
    :rtype: str
    """
    # Manual right replace: https://stackoverflow.com/a/9943875
    setup_path = u"setup".join(teardown_path.rsplit(u"teardown", 1))
    with open(teardown_path, u"rt", encoding="utf-8") as file_in:
        teardown_data = json.load(file_in)
    # Transforming setup data into suite data.
    with open(setup_path, u"rt", encoding="utf-8") as file_in:
        suite_data = json.load(file_in)

    end_time = teardown_data[u"end_time"]
    suite_data[u"end_time"] = end_time
    start_float = parse(suite_data[u"start_time"]).timestamp()
    end_float = parse(suite_data[u"end_time"]).timestamp()
    suite_data[u"duration"] = end_float - start_float
    setup_telemetry = suite_data.pop(u"telemetry")
    suite_data[u"setup_telemetry"] = setup_telemetry
    suite_data[u"teardown_telemetry"] = teardown_data[u"telemetry"]

    suite_path = u"suite".join(teardown_path.rsplit(u"teardown", 1))
    with open(suite_path, u"wt", encoding="utf-8") as file_out:
        json.dump(suite_data, file_out, indent=1)
    # We moved everything useful from temporary setup/teardown info files.
    os.remove(setup_path)
    os.remove(teardown_path)

    return suite_path


def write_output(file_path, data):
    """Prepare data for serialization and dump into a file.

    Ancestor directories are created if needed.

    :param file_path: Local filesystem path, including the file name.
    :param data: Root data to make serializable, dictized when applicable.
    :type file_path: str
    :type data: dict
    """
    data = _pre_serialize_root(data)

    # Lets move Telemetry to the end.
    telemetry = data.pop(u"telemetry")
    data[u"telemetry"] = telemetry

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, u"wt", encoding="utf-8") as file_out:
        json.dump(data, file_out, indent=1)

    if file_path.endswith(u"/teardown.info.json"):
        file_path = _merge_into_suite_info_file(file_path)

    return file_path
