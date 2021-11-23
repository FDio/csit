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

"""Module tracking json in-memory data and saving it to files.

The current implementation tracks data for raw output,
and info output is created from raw output on disk (see raw2info module).
Raw file contains all log items but no derived quantities,
info file contains only important log items but also derived quantities.
The overlap between two files is big.

Each test case, suite setup (hierarchical) and teardown has its own file pair.

Validation is performed for output files with available JSON schema.
Validation is performed in data deserialized from disk,
as serialization might have introduced subtle errors.
"""

from collections.abc import Mapping, Iterable
from enum import IntFlag
import json
import os

import jsonschema
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.model.raw2info import process_content_to_info
from resources.libraries.python.model.util import normalize
from resources.libraries.python.time_measurement import timestamp_or_now


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


def _get_validator(schema_path):
    """Contruct validator with format checking enabled.

    Load json schema from disk.
    Perform validation against meta-schema before returning.

    :param schema_path: Local filesystem path to .json file storing the schema.
    :type schema_path: str
    :returns: Instantiated validator class instance.
    :rtype: jsonschema.validators.Validator
    """
    with open(schema_path, u"rt", encoding="utf-8") as file_in:
        schema = json.load(file_in)
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)
    fmt_checker = jsonschema.FormatChecker()
    validator = validator_class(schema, format_checker=fmt_checker)
    return validator


class export_json():
    """Class handling the json data setting and export."""

    ROBOT_LIBRARY_SCOPE = u"GLOBAL"

    def __init__(self):
        """Declare required fields, cache output dir.

        Also memorize schema validator instances.
        """
        self.output_dir = BuiltIn().get_variable_value(u"\\${OUTPUT_DIR}", ".")
        self.raw_file_path = None
        self.raw_data = None
        # Robot is always started when CWD is CSIT_DIR.
        schema_dir = os.getcwd() + u"/docs/model/current/UTI_output_files/"
        schema_path = schema_dir + u"test_case.info.schema.json"
        self.info_test_schema_validator = _get_validator(schema_path)

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
        if not Constants.EXPORT_JSON or not self.raw_file_path:
            return
        raw_data = _pre_serialize_root(self.raw_data)
        os.makedirs(os.path.dirname(self.raw_file_path), exist_ok=True)
        with open(self.raw_file_path, u"wt", encoding="utf-8") as file_out:
            json.dump(raw_data, file_out, indent=1)
        self.raw_data = None
        # Validation for raw outpt goes here when ready.
        info_file_path = process_content_to_info(self.raw_file_path)
        self.raw_file_path = None
        # TODO: Move validation code into a separate function?
        if u"results" not in raw_data:
            # Suite setups and teardown currently do not have schema.
            return
        with open(info_file_path, u"rt", encoding="utf-8") as file_in:
            instance = json.load(file_in)
        error = jsonschema.exceptions.best_match(
            self.info_test_schema_validator.iter_errors(instance)
        )
        if error is not None:
            raise error

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
        suite_name = BuiltIn().get_variable_value(u"\\${SUITE_NAME}")
        suite_path_part = os.path.join(*normalize(suite_name).split(u"."))
        output_dir = self.output_dir
        self.raw_file_path = os.path.join(
            output_dir, u"output_raw", suite_path_part, u"setup.raw.json"
        )
        data = dict()
        data[u"version"] = Constants.MODEL_VERSION
        # TODO: Add example to model document.
        data[u"suite_name"] = suite_name
        data[u"suite_documentation"] = BuiltIn().get_variable_value(
            u"\\${SUITE_DOCUMENTATION}"
        )
        data[u"start_time"] = start_time
        # "end_time" and "duration" is added on flush.
        data[u"log"] = list()
        self.raw_data = data

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
        suite_name = BuiltIn().get_variable_value(u"\\${SUITE_NAME}")
        suite_path_part = os.path.join(*normalize(suite_name).split(u"."))
        test_name = BuiltIn().get_variable_value(u"\\${TEST_NAME}")
        self.raw_file_path = os.path.join(
            self.output_dir, u"output_raw", suite_path_part,
            normalize(test_name) + u".raw.json"
        )
        data = dict()
        data[u"version"] = Constants.MODEL_VERSION
        # TODO: "ci".
        # TODO: "job".
        # TODO: "build_number".
        # TODO: "testbed".
        data[u"suite_name"] = suite_name
        # "sut_version" is set by a separate keyword.
        data[u"test_name"] = test_name
        # "test_type" is set by keyword setting results.
        test_doc = BuiltIn().get_variable_value(u"\\${TEST_DOCUMENTATION}", u"")
        data[u"test_documentation"] = test_doc
        # "tags" is detected and added on flush.
        data[u"start_time"] = start_time
        # "end_time" and "duration" is added on flush.
        # "status" is added on flush.
        # "message" is added on flush.
        data[u"results"] = dict()
        # TODO: "resource"
        # TODO: "network"
        data[u"log"] = list()
        self.raw_data = data

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
        suite_name = BuiltIn().get_variable_value(u"\\${SUITE_NAME}")
        suite_path_part = os.path.join(*normalize(suite_name).split(u"."))
        self.raw_file_path = os.path.join(
            self.output_dir, u"output_raw", suite_path_part,
            u"teardown.raw.json"
        )
        data = dict()
        data[u"version"] = Constants.MODEL_VERSION
        data[u"start_time"] = start_time
        # "end_time" and "duration" is added on flush.
        data[u"log"] = list()
        data[u"suite_name"] = suite_name
        self.raw_data = data

    def finalize_suite_setup_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite setup.
        The write is done at next start (or at the end of global teardown).
        """
        end_time = timestamp_or_now()
        self.raw_data[u"end_time"] = end_time

    def finalize_test_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be at the end of test teardown, as the implementation
        reads various Robot variables, some of them only available at teardown.

        The write is done at next start (or at the end of global teardown).
        """
        end_time = timestamp_or_now()
        test_tags = BuiltIn().get_variable_value(u"\\${TEST_TAGS}")
        self.raw_data[u"tags"] = [str(tag) for tag in test_tags]
        self.raw_data[u"end_time"] = end_time
        self.raw_data[u"status"] = BuiltIn().get_variable_value(
            u"\\${TEST_STATUS}"
        )
        self.raw_data[u"message"] = BuiltIn().get_variable_value(
            u"\\${TEST_MESSAGE}"
        )

    def finalize_suite_teardown_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite teardown
        (but before the explicit write in the global suite teardown).
        The write is done at next start (or explicitly for global teardown).
        """
        end_time = timestamp_or_now()
        self.raw_data[u"end_time"] = end_time
