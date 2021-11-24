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

import os.path

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.model.mem2raw import write_raw_output
from resources.libraries.python.model.raw2info import convert_content_to_info
from resources.libraries.python.model.util import normalize
from resources.libraries.python.model.validate import (get_validators, validate)
from resources.libraries.python.time_measurement import timestamp_or_now


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
        self.validators = get_validators()

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
        is_testcase = u"results" in self.raw_data
        write_raw_output(self.raw_file_path, self.raw_data)
        self.raw_data = None
        # Validation for raw outpt goes here when ready.
        info_file_path = convert_content_to_info(self.raw_file_path)
        self.raw_file_path = None
        if not is_testcase:
            # Suite setups and teardown currently do not have schema.
            return
        validate(info_file_path, self.validators[u"tc_info_output"])

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
            output_dir, suite_path_part, u"setup.output.raw.json"
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
            self.output_dir, suite_path_part,
            normalize(test_name) + u".output.raw.json"
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
            self.output_dir, suite_path_part, u"teardown.output.raw.json"
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
