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

import datetime
import json
import os


class export_json():
    """Class handling the json data setting and export.
    """

    ROBOT_LIBRARY_SCOPE = u"TEST"

    # TODO: Where to store model version? Constants.py?
    MODEL_VERSION = u"0.1.0"
    # TODO: Version of the whole model, or just the UTI part?

    def __init__(self, suite_name, log_dir):
        """Store values and reset data.

        Suite name is used to create tree structure for json file placement.

        :param suite_name: Name of suite as detected by Robot.
        :param log_dir: Root directory for json file placement.
        :type suite_name: str
        :type log_dir: str
        """
        self.suite_name = str(suite_name)
        self.suite_path_part = os.path.join(*suite_name.split(u"."))
        self.log_dir = str(log_dir)
        self.data = None
        self.reset()

    def get_subdata(self, path):
        """Return reference to inner tree node.

        TODO: Define class for path or path item?

        :param path: Node names (for dict nodes) or indices (for list nodes).
        :type path: Sequence[Union[str, int]]
        :returns: Reference to (mutable) inner tree node.
        :rtype: Union[dict, list]
        """
        cursor = self.data
        for item in path:
            cursor = cursor[item]
        return cursor

    def reset(self):
        """Reset the mutable state to minimal initial tree."""
        self.data = dict()
        self.data[u"version"] = self.MODEL_VERSION
        self.data[u"metadata"] = dict()
        metadata_node = self.data[u"metadata"]
        metadata_node[u"suite-id"] = self.suite_name
        # TODO: "suite-doc"
        # TODO: "testbed"
        # TODO: Set "sut-version" via a new keyword.
        # TODO: "resource"
        # TODO: "network"
        self.data[u"log"] = list()
        self.data[u"test"] = dict()
        test_node = self.data[u"test"]
        # "test-id" is added on flush.
        # "test-type" to be set explicitly later.
        # TODO: Detect and add "tags" on flush.
        # TODO: Detect and add "documentation".
        test_node[u"execution"] = dict()
        execution_node = test_node[u"execution"]
        execution_node[u"start_time"] = str(datetime.datetime.utcnow())
        # Stop time is added on flush.
        # Test status is added on flush.
        # TODO: Is the rest of "execution" data even available from Robot?
        test_node[u"results"] = dict()

    def flush_test(self, test_name, test_status):
        """Write serialized data to file based on test name.

        :param test_name: Test case name as detected by Robot.
        :param test_status: PASS or FAIL.
        :type test_name: str
        :type test_status: str
        """
        self.data[u"test"][u"test-id"] = self.suite_name + u"." + test_name
        execution_node = self.data[u"test"][u"execution"]
        execution_node[u"stop_time"] = str(datetime.datetime.utcnow())
        execution_node[u"status"] = str(test_status)
        file_path = os.path.join(
            self.log_dir, self.suite_path_part, test_name + u".json.log"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, u"w") as file_out:
            json.dump(self.data, file_out, indent=1)
        # Not explicitly forgetting data, so accidental double flush
        # does not lose information.
        # We rely on library import scope to start next test case
        # with data reset.
