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


class json_export():
    """Class handling the json data setting and export.
    """

    ROBOT_LIBRARY_SCOPE = u"TEST"

    MODEL_VERSION = u"0.1.0"

    def __init__(self, suite_name, log_dir):
        """Store values and reset data.

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
        self.data[u"version"] = MODEL_VERSION
        # TODO: "metadata"
        # TODO: "resource"
        # TODO: "network"
        self.data[u"log"] = list()
        self.data[u"test"] = dict()
        test = self.data[u"test"]
        # "test-id" to be added on flush.
        # "test-type" to be set explicitly later.
        # TODO: Detect and add "tags" on flush.
        # TODO: Detect and add "documentation".
        # TODO: Is the data for "execution" even available from Robot?
        test[u"telemetry"] = list()
        test[u"results"] = dict()
        results = test[u"results"]
        results[u"test"] = dict()
        # TODO: Detect and add [u"node"], probably on flush.

    def flush_test(self, test_name):
        """Write serialized data to file based on test name.

        :param test_name: Test case name as detected by Robot.
        :type test_name: str
        """
        file_path = os.path.join(
            self.log_dir, self.suite_path_part, test_name + u".json.log"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, u"w") as file_out:
            file_out.write(json.dumps(self.data))
