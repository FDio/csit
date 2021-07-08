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

"""Module tracking json in-memory data and saving it to files."""

from collections.abc import Mapping, Iterable
from enum import IntFlag
import json
import os

from resources.libraries.python.Constants import Constants
from resources.libraries.python.robot_interaction import get_variable
from resources.libraries.python.time_measurement import timestamp_or_now


def _pre_serialize_recursive(data):
    """Return a copy, recursively sorted and converted to a serializable form.

    VPP PAPI code can give data with its own MACAddres type,
    or various other enum and flag types.
    The default json.JSONEncoder method raises TypeError on that.
    First point of this function is to apply str() or repr()
    to leaf values that need it.

    Also, PAPI responses are namedtuples, which confuses
    the json.JSONEncoder method (so it does not recurse).
    Dictization (see PapiExecutor) helps somewhat, but it turns namedtuple
    into a UserDict, which also confuses json.JSONEncoder.
    Therefore, we recursively convert any Mapping (including ProtectedDict)
    into an ordinary dict.

    We also convert iterables (including ProtectedList) to list,
    and prevent numbers from getting converted to strings.

    As we are doing such low level operations,
    we also convert mapping keys to strings
    and sort the mapping items by keys alphabetically,
    except "data" field moved to the end.

    :param data: Object to make serializable, dictized when applicable.
    :type data: object
    :returns: Serializable equivalent copy of the argument.
    :rtype: object
    :raises ValueError: If the argument does not support string conversion.
    """
    # Recursion ends at scalar values, first handle irregular ones.
    if isinstance(data, IntFlag):
        return repr(data)
    if isinstance(data, bytes):
        return data.hex()
    # The regular ones are good to go.
    # TODO: Will the list of types always be equal to ProtectedLeaf?
    if isinstance(data, (str, int, float, bool, type(None))):
        return data
    # Recurse over, convert and sort mappings.
    if isinstance(data, Mapping):
        # Convert and sort alphabetically.
        ret = {
            str(key): _pre_serialize_recursive(data[key])
            for key in sorted(data)
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
    log = data.pop(u"log")
    new_data = {u"version": data.pop(u"version")}
    new_data.update(_pre_serialize_recursive(data))
    new_data[u"log"] = _pre_serialize_recursive(log)
    return new_data


class export_json:
    """Class handling the json data setting and export."""

    ROBOT_LIBRARY_SCOPE = u"GLOBAL"

    def __init__(self):
        """Declare required fields, cache output dir."""
        self.output_dir = get_variable(u"\\${OUTPUT_DIR}", ".")
        self.file_path = None
        self.data = None

    def export_pending_data(self):
        """Write the accumulated data to disk.

        Create missing directories.
        Reset both file path and data to avoid writing multiple times.

        Functions which set file path are calling this.
        Call explicitly at the end of the global suite teardown,
        even after finalizing export forthat teardown.

        If no file path is set, return silently,
        as that is the expected behavior when starting global suite setup.
        """
        if not self.file_path:
            return
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        data = _pre_serialize_root(self.data)
        with open(self.file_path, u"w") as file_out:
            json.dump(data, file_out, indent=1)
        self.data = None
        self.file_path = None

    def start_suite_setup_export(self):
        """Set new file path, initialize data for the suite setup.

        Write data from previous test/suite.

        This has to be called explicitly at start of suite setup,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.

        File path is set based on suite.
        """
        self.export_pending_data()
        start_time = timestamp_or_now()
        suite_name = get_variable(u"\\${SUITE_NAME}")
        suite_path_part = os.path.join(*suite_name.split(u"."))
        self.file_path = os.path.join(
            self.output_dir, suite_path_part, u"setup.json.log"
        )
        data = dict()
        data[u"version"] = Constants.MODEL_VERSION
        # TODO: Add example to model document.
        data[u"suite_id"] = get_variable(u"\\${SUITE_NAME}")
        data[u"suite_doc"] = get_variable(u"\\${SUITE_DOCUMENTATION}")
        data[u"start_time"] = start_time
        # "end_time" is added on flush.
        data[u"log"] = list()
        self.data = data

    def start_test_export(self):
        """Set new file path, initialize data to minimal tree for the test case.

        Write data from previous test/suite.

        This has to be called explicitly at the start of test setup,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.

        File path is set based on suite and test.
        """
        self.export_pending_data()
        start_time = timestamp_or_now()
        suite_name = get_variable(u"\\${SUITE_NAME}")
        suite_path_part = os.path.join(*suite_name.split(u"."))
        test_name = get_variable(u"\\${TEST_NAME}")
        self.file_path = os.path.join(
            self.output_dir, suite_path_part, test_name + u".json.log"
        )
        data = dict()
        data[u"version"] = Constants.MODEL_VERSION
        # TODO: "ci".
        # TODO: "job".
        # TODO: "build_number".
        # TODO: "testbed".
        data[u"suite_id"] = get_variable(u"\\${SUITE_NAME}")
        data[u"suite_doc"] = get_variable(u"\\${SUITE_DOCUMENTATION}")
        # "sut_version" is set by a separate keyword.
        data[u"test_id"] = suite_name + u"." + test_name
        # "test_type" is set by keyword setting results.
        data[u"test_doc"] = get_variable(u"\\${TEST_DOCUMENTATION}", u"")
        # "tags" is detected and added on flush.
        data[u"start_time"] = start_time
        # "end_time" is added on flush.
        # "status" is added on flush.
        # "message" is added on flush.
        data[u"results"] = dict()
        # TODO: "resource"
        # TODO: "network"
        data[u"log"] = list()
        self.data = data

    def start_suite_teardown_export(self):
        """Set new file path, initialize data for the suite teardown.

        Write data from previous test/suite.

        This has to be called explicitly at start of suite teardown,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.

        File path is set based on suite.
        """
        self.export_pending_data()
        start_time = timestamp_or_now()
        suite_name = get_variable(u"\\${SUITE_NAME}")
        suite_path_part = os.path.join(*suite_name.split(u"."))
        self.file_path = os.path.join(
            self.output_dir, suite_path_part, u"teardown.json.log"
        )
        data = dict()
        data[u"version"] = Constants.MODEL_VERSION
        # TODO: Add example to model document.
        #data[u"suite_id"] = get_variable(u"\\${SUITE_NAME}")
        #data[u"suite_doc"] = get_variable(u"\\${SUITE_DOCUMENTATION}")
        data[u"start_time"] = start_time
        # "end_time" is added on flush.
        data[u"log"] = list()
        self.data = data

    def finalize_suite_setup_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite setup.
        The write is done at next start (or at the end of global teardown).
        """
        end_time = timestamp_or_now()
        data = self.data
        data[u"end_time"] = end_time

    def finalize_test_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be at the end of test teardown, as the implementation
        reads various Robot variables, some of them only available at teardown.

        The write is done at next start (or at the end of global teardown).
        """
        end_time = timestamp_or_now()
        data = self.data
        test_tags = get_variable(u"\\${TEST_TAGS}")
        data[u"tags"] = [str(tag) for tag in test_tags]
        data[u"end_time"] = end_time
        data[u"status"] = get_variable(u"\\${TEST_STATUS}")
        data[u"message"] = get_variable(u"\\${TEST_MESSAGE}")

    def finalize_suite_teardown_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite teardown
        (but before the explicit write in the global suite teardown).
        The write is done at next start (or explicitly for global teardown).
        """
        end_time = timestamp_or_now()
        data = self.data
        data[u"end_time"] = end_time
