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

from dateutil.parser import parse

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

    def process_test_name(self):
        """Replace raw test name with short and long test name and set test_type.

        Perform in-place edits on the data dictionary.
        Remove raw suite_name and test_name, they are not part of info schema.
        Return early if the data is not for test case.
        Inserttest ID and long and short test name into the data.
        Besides suite_name and test_name, also test tags are read.

        Short test name is basically a suite tag, but with NIC driver prefix,
        if the NIC driver used is not the default one (drv_vfio_pci for VPP tests).

        Long test name has the following form:
        {nic_short_name}-{frame_size}-{threads_and_cores}-{suite_part}
        Lookup in test tags is needed to get the threads value.
        The threads_and_cores part may be empty, e.g. for TRex tests.

        Test ID has form {suite_name}.{test_name} where the two names come from
        Robot variables, converted to lower case and spaces replaces by undescores.

        Test type is set in an internal function.

        :raises RuntimeError: If the raw data does not contain expected values.
        """
        suite_part = self.raw_data.pop(u"suite_name").lower().replace(u" ", u"_")
        if u"test_name" not in self.raw_data:
            # There will be no test_id, provide suite_id instead.
            self.raw_data[u"suite_id"] = suite_part
            return
        test_part = self.raw_data.pop(u"test_name").lower().replace(u" ", u"_")
        self.raw_data[u"test_id"] = f"{suite_part}.{test_part}"
        tags = self.raw_data[u"tags"]
        # Test name does not contain thread count.
        subparts = test_part.split(u"c-", 1)
        if len(subparts) < 2 or subparts[0][-2:-1] != u"-":
            # Physical core count not detected, assume it is a TRex test.
            if u"--" not in test_part:
                raise RuntimeError(f"Cores not found for {subparts}")
            short_name = test_part.split(u"--", 1)[1]
        else:
            short_name = subparts[1]
            # Add threads to test_part.
            core_part = subparts[0][-1] + u"c"
            for tag in tags:
                tag = tag.lower()
                if len(tag) == 4 and core_part == tag[2:] and tag[1] == u"t":
                    test_part = test_part.replace(f"-{core_part}-", f"-{tag}-")
                    break
            else:
                raise RuntimeError(f"Threads not found for {test_part} tags {tags}")
        # For long name we need NIC model, which is only in suite name.
        last_suite_part = suite_part.split(u".")[-1]
        # Short name happens to be the suffix we want to ignore.
        prefix_part = last_suite_part.split(short_name)[0]
        # Also remove the trailing dash.
        prefix_part = prefix_part[:-1]
        # Throw away possible link prefix such as "1n1l-".
        nic_code = prefix_part.split(u"-", 1)[-1]
        nic_short = Constants.NIC_CODE_TO_SHORT_NAME[nic_code]
        long_name = f"{nic_short}-{test_part}"
        # Set test type.
        test_type = self.detect_test_type()
        self.raw_data[u"test_type"] = test_type
        # Remove trailing test type from names (if present).
        short_name = short_name.split(f"-{test_type}")[0]
        long_name = long_name.split(f"-{test_type}")[0]
        # Store names.
        self.raw_data[u"test_name_short"] = short_name
        self.raw_data[u"test_name_long"] = long_name

    def detect_test_type(self):
        """Return test_type, as inferred from robot test tags.

        :returns: The inferred test type value.
        :rtype: str
        :raises RuntimeError: If the test tags does not contain expected values.
        """
        tags = self.raw_data[u"tags"]
        # First 5 options are specific for VPP tests.
        if u"DEVICETEST" in tags:
            test_type = u"device"
        elif u"LDP_NGINX" in tags:
            test_type = u"vsap"
        elif u"HOSTSTACK" in tags:
            test_type = u"hoststack"
        elif u"GSO_TRUE" in tags or u"GSO_FALSE" in tags:
            test_type = u"gso"
        elif u"RECONF" in tags:
            test_type = u"reconf"
        # The remaining 3 options could also apply to DPDK and TRex tests.
        elif u"SOAK" in tags:
            test_type = u"soak"
        elif u"NDRPDR" in tags:
            test_type = u"ndrpdr"
        elif u"MRR" in tags:
            test_type = u"mrr"
        else:
            raise RuntimeError(f"Unable to infer test type from tags: {tags}")
        return test_type

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
        self.raw_data[u"hosts"] = BuiltIn().get_variable_value(u"\\${hosts}")
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
        self.raw_data[u"hosts"] = BuiltIn().get_variable_value(u"\\${hosts}")

    def finalize_suite_setup_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite setup.
        The write is done at next start (or at the end of global teardown).
        """
        end_time = datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")
        self.raw_data[u"hosts"] = BuiltIn().get_variable_value(u"\\${hosts}")
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
        self.raw_data[u"message"] = message
        if status is not None:
            self.raw_data[u"passed"] = (status == u"PASS")
            if self.raw_data[u"passed"]:
                # Also truncate success test messages.
                self.raw_data[u"message"] = u""
        start_float = parse(self.raw_data[u"start_time"]).timestamp()
        end_float = parse(self.raw_data[u"end_time"]).timestamp()
        self.raw_data[u"duration"] = end_float - start_float
        self.process_test_name()
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
