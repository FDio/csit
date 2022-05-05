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

import datetime
import os.path

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.model.ExportResult import (
    export_dut_type_and_version, export_tg_type_and_version
)
from resources.libraries.python.model.mem2raw import write_raw_output
from resources.libraries.python.model.raw2info import convert_content_to_info
from resources.libraries.python.model.validate import (get_validators, validate)


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

        Functions which finalize content for given file are calling this,
        so make sure each test and non-empty suite setup or teardown
        is calling this as their last keyword.

        If no file path is set, do not write anything,
        as that is the failsafe behavior when caller from unexpected place.
        Aso do not write anything when EXPORT_JSON constant is false.

        Regardless of whether data was written, it is cleared.
        """
        if not Constants.EXPORT_JSON or not self.raw_file_path:
            self.raw_data = None
            self.raw_file_path = None
            return
        write_raw_output(self.raw_file_path, self.raw_data)
        # Raw data is going to be cleared (as a sign that raw export succeeded),
        # so this is the last chance to detect if it was for a test case.
        is_testcase = u"result" in self.raw_data
        self.raw_data = None
        # Validation for raw output goes here when ready.
        info_file_path = convert_content_to_info(self.raw_file_path)
        self.raw_file_path = None
        # If "result" is missing from info content,
        # it could be a bug in conversion from raw test case content,
        # so instead of that we use the flag detected earlier.
        if is_testcase:
            validate(info_file_path, self.validators[u"tc_info"])

    def warn_on_bad_export(self):
        """If bad state is detected, log a warning and clean up state."""
        if self.raw_file_path is not None or self.raw_data is not None:
            logger.warn(f"Previous export not clean, path {self.raw_file_path}")
            self.raw_data = None
            self.raw_file_path = None

    def start_suite_setup_export(self):
        """Set new file path, initialize data for the suite setup.

        This has to be called explicitly at start of suite setup,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.

        File path is set based on suite.
        """
        self.warn_on_bad_export()
        start_time = datetime.datetime.utcnow().strftime(
            u"%Y-%m-%dT%H:%M:%S.%fZ"
        )
        suite_name = BuiltIn().get_variable_value(u"\\${SUITE_NAME}")
        suite_id = suite_name.lower().replace(u" ", u"_")
        suite_path_part = os.path.join(*suite_id.split(u"."))
        output_dir = self.output_dir
        self.raw_file_path = os.path.join(
            output_dir, suite_path_part, u"setup.raw.json"
        )
        self.raw_data = dict()
        self.raw_data[u"version"] = Constants.MODEL_VERSION
        self.raw_data[u"start_time"] = start_time
        self.raw_data[u"suite_name"] = suite_name
        self.raw_data[u"suite_documentation"] = BuiltIn().get_variable_value(
            u"\\${SUITE_DOCUMENTATION}"
        )
        # "end_time" and "duration" is added on flush.
        self.raw_data[u"hosts"] = set()
        self.raw_data[u"log"] = list()

    def start_test_export(self):
        """Set new file path, initialize data to minimal tree for the test case.

        It is assumed Robot variables DUT_TYPE and DUT_VERSION
        are already set (in suite setup) to correct values.

        This function has to be called explicitly at the start of test setup,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.

        File path is set based on suite and test.
        """
        self.warn_on_bad_export()
        start_time = datetime.datetime.utcnow().strftime(
            u"%Y-%m-%dT%H:%M:%S.%fZ"
        )
        suite_name = BuiltIn().get_variable_value(u"\\${SUITE_NAME}")
        suite_id = suite_name.lower().replace(u" ", u"_")
        suite_path_part = os.path.join(*suite_id.split(u"."))
        test_name = BuiltIn().get_variable_value(u"\\${TEST_NAME}")
        self.raw_file_path = os.path.join(
            self.output_dir, suite_path_part,
            test_name.lower().replace(u" ", u"_") + u".raw.json"
        )
        self.raw_data = dict()
        self.raw_data[u"version"] = Constants.MODEL_VERSION
        self.raw_data[u"start_time"] = start_time
        self.raw_data[u"suite_name"] = suite_name
        self.raw_data[u"test_name"] = test_name
        test_doc = BuiltIn().get_variable_value(u"\\${TEST_DOCUMENTATION}", u"")
        self.raw_data[u"test_documentation"] = test_doc
        # "test_type" is added when converting to info.
        # "tags" is detected and added on flush.
        # "end_time" and "duration" is added on flush.
        # Robot status and message are added on flush.
        self.raw_data[u"result"] = dict(type=u"unknown")
        self.raw_data[u"hosts"] = set()
        self.raw_data[u"log"] = list()
        export_dut_type_and_version()
        export_tg_type_and_version()

    def start_suite_teardown_export(self):
        """Set new file path, initialize data for the suite teardown.

        This has to be called explicitly at start of suite teardown,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.

        File path is set based on suite.
        """
        self.warn_on_bad_export()
        start_time = datetime.datetime.utcnow().strftime(
            u"%Y-%m-%dT%H:%M:%S.%fZ"
        )
        suite_name = BuiltIn().get_variable_value(u"\\${SUITE_NAME}")
        suite_id = suite_name.lower().replace(u" ", u"_")
        suite_path_part = os.path.join(*suite_id.split(u"."))
        self.raw_file_path = os.path.join(
            self.output_dir, suite_path_part, u"teardown.raw.json"
        )
        self.raw_data = dict()
        self.raw_data[u"version"] = Constants.MODEL_VERSION
        self.raw_data[u"start_time"] = start_time
        self.raw_data[u"suite_name"] = suite_name
        # "end_time" and "duration" is added on flush.
        self.raw_data[u"hosts"] = set()
        self.raw_data[u"log"] = list()

    def finalize_suite_setup_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite setup.
        The write is done at next start (or at the end of global teardown).
        """
        end_time = datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")
        self.raw_data[u"end_time"] = end_time
        self.export_pending_data()

    def finalize_test_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be at the end of test teardown, as the implementation
        reads various Robot variables, some of them only available at teardown.

        The write is done at next start (or at the end of global teardown).
        """
        end_time = datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")
        message = BuiltIn().get_variable_value(u"\\${TEST_MESSAGE}")
        status = BuiltIn().get_variable_value(u"\\${TEST_STATUS}")
        test_tags = BuiltIn().get_variable_value(u"\\${TEST_TAGS}")
        self.raw_data[u"end_time"] = end_time
        self.raw_data[u"tags"] = list(test_tags)
        self.raw_data[u"status"] = status
        self.raw_data[u"message"] = message
        self.export_pending_data()

    def finalize_suite_teardown_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite teardown
        (but before the explicit write in the global suite teardown).
        The write is done at next start (or explicitly for global teardown).
        """
        end_time = datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")
        self.raw_data[u"end_time"] = end_time
        self.export_pending_data()
