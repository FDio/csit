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

"""Module tracking json in-memory data and saving it to files.

Each test case, suite setup (hierarchical) and teardown has its own file pair.

Validation is performed for output files with available JSON schema.
Validation is performed in data deserialized from disk,
as serialization might have introduced subtle errors.
"""

import datetime
import os.path

from binascii import b2a_base64
from dateutil.parser import parse
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from zlib import compress

from resources.libraries.python.Constants import Constants
from resources.libraries.python.jumpavg import AvgStdevStats
from resources.libraries.python.model.ExportResult import (
    export_dut_type_and_version, export_tg_type_and_version
)
from resources.libraries.python.model.MemDump import write_output
from resources.libraries.python.model.validate import (
    get_validators, validate
)


class ExportJson():
    """Class handling the json data setting and export."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        """Declare required fields, cache output dir.

        Also memorize schema validator instances.
        """
        self.output_dir = BuiltIn().get_variable_value("\\${OUTPUT_DIR}", ".")
        self.file_path = None
        self.data = None
        self.validators = get_validators()

    def _detect_test_type(self):
        """Return test_type, as inferred from robot test tags.

        :returns: The inferred test type value.
        :rtype: str
        :raises RuntimeError: If the test tags does not contain expected values.
        """
        tags = self.data["tags"]
        # First 5 options are specific for VPP tests.
        if "DEVICETEST" in tags:
            test_type = "device"
        elif "LDP_NGINX" in tags:
            test_type = "hoststack"
        elif "HOSTSTACK" in tags:
            test_type = "hoststack"
        elif "GSO_TRUE" in tags or "GSO_FALSE" in tags:
            test_type = "mrr"
        elif "RECONF" in tags:
            test_type = "reconf"
        # The remaining 3 options could also apply to DPDK and TRex tests.
        elif "SOAK" in tags:
            test_type = "soak"
        elif "NDRPDR" in tags:
            test_type = "ndrpdr"
        elif "MRR" in tags:
            test_type = "mrr"
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
        if not Constants.EXPORT_JSON or not self.file_path:
            self.data = None
            self.file_path = None
            return
        new_file_path = write_output(self.file_path, self.data)
        # Data is going to be cleared (as a sign that export succeeded),
        # so this is the last chance to detect if it was for a test case.
        is_testcase = "result" in self.data
        self.data = None
        # Validation for output goes here when ready.
        self.file_path = None
        if is_testcase:
            validate(new_file_path, self.validators["tc_info"])

    def warn_on_bad_export(self):
        """If bad state is detected, log a warning and clean up state."""
        if self.file_path is not None or self.data is not None:
            logger.warn(f"Previous export not clean, path {self.file_path}")
            self.data = None
            self.file_path = None

    def start_suite_setup_export(self):
        """Set new file path, initialize data for the suite setup.

        This has to be called explicitly at start of suite setup,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.

        File path is set based on suite.
        """
        self.warn_on_bad_export()
        start_time = datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        suite_name = BuiltIn().get_variable_value("\\${SUITE_NAME}")
        suite_id = suite_name.lower().replace(" ", "_")
        suite_path_part = os.path.join(*suite_id.split("."))
        output_dir = self.output_dir
        self.file_path = os.path.join(
            output_dir, suite_path_part, "setup.info.json"
        )
        self.data = dict()
        self.data["version"] = Constants.MODEL_VERSION
        self.data["start_time"] = start_time
        self.data["suite_name"] = suite_name
        self.data["suite_documentation"] = BuiltIn().get_variable_value(
            "\\${SUITE_DOCUMENTATION}"
        )
        # "end_time" and "duration" are added on flush.
        self.data["hosts"] = set()
        self.data["telemetry"] = list()

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
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        suite_name = BuiltIn().get_variable_value("\\${SUITE_NAME}")
        suite_id = suite_name.lower().replace(" ", "_")
        suite_path_part = os.path.join(*suite_id.split("."))
        test_name = BuiltIn().get_variable_value("\\${TEST_NAME}")
        self.file_path = os.path.join(
            self.output_dir, suite_path_part,
            test_name.lower().replace(" ", "_") + ".info.json"
        )
        self.data = dict()
        self.data["version"] = Constants.MODEL_VERSION
        self.data["start_time"] = start_time
        self.data["suite_name"] = suite_name
        self.data["test_name"] = test_name
        test_doc = BuiltIn().get_variable_value("\\${TEST_DOCUMENTATION}", "")
        self.data["test_documentation"] = test_doc
        # "test_type" is added on flush.
        # "tags" is detected and added on flush.
        # "end_time" and "duration" is added on flush.
        # Robot status and message are added on flush.
        self.data["result"] = dict(type="unknown")
        self.data["hosts"] = BuiltIn().get_variable_value("\\${hosts}")
        self.data["telemetry"] = list()
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
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        suite_name = BuiltIn().get_variable_value("\\${SUITE_NAME}")
        suite_id = suite_name.lower().replace(" ", "_")
        suite_path_part = os.path.join(*suite_id.split("."))
        self.file_path = os.path.join(
            self.output_dir, suite_path_part, "teardown.info.json"
        )
        self.data = dict()
        self.data["version"] = Constants.MODEL_VERSION
        self.data["start_time"] = start_time
        self.data["suite_name"] = suite_name
        # "end_time" and "duration" is added on flush.
        self.data["hosts"] = BuiltIn().get_variable_value("\\${hosts}")
        self.data["telemetry"] = list()

    def finalize_suite_setup_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite setup.
        The write is done at next start (or at the end of global teardown).
        """
        end_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.data["hosts"] = BuiltIn().get_variable_value("\\${hosts}")
        self.data["end_time"] = end_time
        self.export_pending_data()

    def finalize_test_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be at the end of test teardown, as the implementation
        reads various Robot variables, some of them only available at teardown.

        The write is done at next start (or at the end of global teardown).
        """
        end_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        message = BuiltIn().get_variable_value("\\${TEST_MESSAGE}")
        test_tags = BuiltIn().get_variable_value("\\${TEST_TAGS}")
        self.data["end_time"] = end_time
        start_float = parse(self.data["start_time"]).timestamp()
        end_float = parse(self.data["end_time"]).timestamp()
        self.data["duration"] = end_float - start_float
        self.data["tags"] = list(test_tags)
        self.data["message"] = message
        self.process_passed()
        self.process_test_name()
        self.process_results()
        self.export_pending_data()

    def finalize_suite_teardown_export(self):
        """Add the missing fields to data. Do not write yet.

        Should be run at the end of suite teardown
        (but before the explicit write in the global suite teardown).
        The write is done at next start (or explicitly for global teardown).
        """
        end_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.data["end_time"] = end_time
        self.export_pending_data()

    def process_test_name(self):
        """Replace raw test name with short and long test name and set
        test_type.

        Perform in-place edits on the data dictionary.
        Remove raw suite_name and test_name, they are not published.
        Return early if the data is not for test case.
        Insert test ID and long and short test name into the data.
        Besides suite_name and test_name, also test tags are read.

        Short test name is basically a suite tag, but with NIC driver prefix,
        if the NIC driver used is not the default one (drv_vfio_pci for VPP
        tests).

        Long test name has the following form:
        {nic_short_name}-{frame_size}-{threads_and_cores}-{suite_part}
        Lookup in test tags is needed to get the threads value.
        The threads_and_cores part may be empty, e.g. for TRex tests.

        Test ID has form {suite_name}.{test_name} where the two names come from
        Robot variables, converted to lower case and spaces replaces by
        undescores.

        Test type is set in an internal function.

        :raises RuntimeError: If the data does not contain expected values.
        """
        suite_part = self.data.pop("suite_name").lower().replace(" ", "_")
        if "test_name" not in self.data:
            # There will be no test_id, provide suite_id instead.
            self.data["suite_id"] = suite_part
            return
        test_part = self.data.pop("test_name").lower().replace(" ", "_")
        self.data["test_id"] = f"{suite_part}.{test_part}"
        tags = self.data["tags"]
        # Test name does not contain thread count.
        subparts = test_part.split("-")
        if any("tg" in s for s in subparts) and subparts[1] == "":
            # Physical core count not detected, assume it is a TRex test.
            if "--" not in test_part:
                raise RuntimeError(f"Invalid TG test name for: {subparts}")
            short_name = test_part.split("--", 1)[1]
        else:
            short_name = "-".join(subparts[2:])
            # Add threads to test_part.
            core_part = subparts[1]
            tag = list(filter(lambda t: subparts[1].upper() in t, tags))[0]
            test_part = test_part.replace(f"-{core_part}-", f"-{tag.lower()}-")
        # For long name we need NIC model, which is only in suite name.
        last_suite_part = suite_part.split(".")[-1]
        # Short name happens to be the suffix we want to ignore.
        prefix_part = last_suite_part.split(short_name)[0]
        # Also remove the trailing dash.
        prefix_part = prefix_part[:-1]
        # Throw away possible link prefix such as "1n1l-".
        nic_code = prefix_part.split("-", 1)[-1]
        nic_short = Constants.NIC_CODE_TO_SHORT_NAME[nic_code]
        long_name = f"{nic_short}-{test_part}"
        # Set test type.
        test_type = self._detect_test_type()
        self.data["test_type"] = test_type
        # Remove trailing test type from names (if present).
        short_name = short_name.split(f"-{test_type}")[0]
        long_name = long_name.split(f"-{test_type}")[0]
        # Store names.
        self.data["test_name_short"] = short_name
        self.data["test_name_long"] = long_name

    def process_passed(self):
        """Process the test status information as boolean.

        Boolean is used to make post processing more efficient.
        In case the test status is PASS, we will truncate the test message.
        """
        status = BuiltIn().get_variable_value("\\${TEST_STATUS}")
        if status is not None:
            self.data["passed"] = (status == "PASS")
            if self.data["passed"]:
                # Also truncate success test messages.
                self.data["message"] = ""

    def process_results(self):
        """Process measured results.

        Results are used to avoid future post processing, making it more
        efficient to consume.
        """
        if self.data["telemetry"]:
            telemetry_encode = "\n".join(self.data["telemetry"]).encode()
            telemetry_compress = compress(telemetry_encode, level=9)
            telemetry_base64 = b2a_base64(telemetry_compress, newline=False)
            self.data["telemetry"] = [telemetry_base64.decode()]
        if "result" not in self.data:
            return
        result_node = self.data["result"]
        result_type = result_node["type"]
        if result_type == "unknown":
            # Device or something else not supported.
            return

        # Compute avg and stdev for mrr (rate and bandwidth).
        if result_type == "mrr":
            for node_name in ("rate", "bandwidth"):
                node = result_node["receive_rate"].get(node_name, None)
                if node is not None:
                    stats = AvgStdevStats.for_runs(node["values"])
                    node["avg"] = stats.avg
                    node["stdev"] = stats.stdev
            return

        # Multiple processing steps for ndrpdr.
        if result_type != "ndrpdr":
            return
        # Filter out invalid latencies.
        for which_key in ("latency_forward", "latency_reverse"):
            if which_key not in result_node:
                # Probably just an unidir test.
                continue
            for load in ("pdr_0", "pdr_10", "pdr_50", "pdr_90"):
                if result_node[which_key][load]["max"] <= 0:
                    # One invalid number is enough to remove all loads.
                    break
            else:
                # No break means all numbers are ok, nothing to do here.
                continue
            # Break happened, something is invalid, remove all loads.
            result_node.pop(which_key)
        return
