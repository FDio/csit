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

"""Module supporting structure-unaware json in-memory data.
"""

import json
import os

from resources.libraries.python.Constants import MODEL_VERSION
from resources.libraries.python.robot_interaction import get_variable
from resources.libraries.python.time_measurement import datetime_utc_str as now


class export_json():
    """Class handling the json data setting and export.
    """

    ROBOT_LIBRARY_SCOPE = u"TEST"

    def __init__(self):
        """Declare data field, do not reset data yet.
        """
        self.data = None

    def reset_test_timer(self):
        """Reset the mutable state to minimal initial tree.

        This has to be called explicitly from test setup,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.
        """
        self.data = dict()
        self.data[u"version"] = MODEL_VERSION
        self.data[u"metadata"] = dict()
        metadata_node = self.data[u"metadata"]
        metadata_node[u"suite-id"] = get_variable(u"${SUITE_NAME}")
        metadata_node[u"suite-doc"] = get_variable(u"${SUITE_DOCUMENTATION}")
        # TODO: "testbed"
        # TODO: Set "sut-version" via a new keyword.
        self.data[u"test"] = dict()
        test_node = self.data[u"test"]
        # "test-id" is added on flush.
        # "test-type" is set by keyword setting results.
        # "test-tags" is detected and added on flush.
        test_doc = get_variable(u"${TEST_DOCUMENTATION}", u"")
        test_node[u"documentation"] = test_doc
        test_node[u"execution"] = dict()
        execution_node = test_node[u"execution"]
        execution_node[u"start_time"] = now()
        # End time is added on flush.
        # Test status is added on flush.
        # TODO: Is the rest of "execution" data even available from Robot?
        test_node[u"results"] = dict()
        # TODO: "resource"
        # TODO: "network"
        self.data[u"log"] = list()

    def flush_test(self):
        """Write serialized data to file based on test name.

        The implementation reads various Robot variables.
        """
        suite_name = get_variable(u"${SUITE_NAME}")
        suite_path_part = os.path.join(*suite_name.split(u"."))
        test_name = get_variable(u"${TEST_NAME}")
        self.data[u"test"][u"test-id"] = suite_name + u"." + test_name
        test_tags = get_variable(u"${TEST_TAGS}")
        self.data[u"test"][u"test_tags"] = [str(tag) for tag in test_tags]
        execution_node = self.data[u"test"][u"execution"]
        execution_node[u"end_time"] = now()
        execution_node[u"status"] = get_variable(u"${TEST_STATUS}")
        log_dir = get_variable(u"${OUTPUT_DIR}", ".")
        file_path = os.path.join(
            log_dir, suite_path_part, test_name + u".json.log"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, u"w") as file_out:
            json.dump(self.data, file_out, indent=1)
        # Not explicitly forgetting data here, so accidental double flush
        # does not lose information.
        # We rely on explicit "time reset" at start of test setup,
        # coupled with library import scope set to "test".
