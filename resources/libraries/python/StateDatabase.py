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

"""Library for tracking and accessing runtime state dring test.
"""

import json


class StateDatabase:
    """FIXME.
    """

    def __init__(self, suite_name, log_dir):
        """FIXME.
        """
        self.suite_name = suite_name
        self.log_dir = log_dir
        self.suite_data = dict()

    def database_update(self, test_name, key, value):
        """FIXME.
        """
        test_data = self.suite_data.get(test_name, dict())
        test_data[key] = value
        self.suite_data[test_name] = test_data

    def database_get(self, test_name, key, default_value=None):
        """FIXME.
        """
        return self.suite_data[test_name].get(key, default_value)

    def database_flush_test(self, test_name):
        """FIXME.
        """
        file_name = self.log_dir + u"/" + self.suite_name + u"." + test_name + u".json.log"
        test_data = self.suite_data.pop(test_name, dict())
        with open(file_name, u"w") as file_out:
            file_out.write(json.dumps(test_data))

    def __del__(self):
        """FIXME.
        """
        file_name = self.log_dir + u"/" + self.suite_name + u".json.log"
        with open(file_name, u"w") as file_out:
            file_out.write(json.dumps(self.suite_data))
