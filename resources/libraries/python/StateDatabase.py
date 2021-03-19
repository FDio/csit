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
import os


class StateDatabase:
    """FIXME.
    """

    def __init__(self, suite_name, log_dir):
        """FIXME.
        """
        self.suite_name = suite_name
        self.suite_path_part = os.path.join(*suite_name.split(u"."))
        self.log_dir = log_dir
        self.suite_data = dict()

    def database_update(self, test_name, key, value):
        """FIXME.
        """
        try:
            # Is it a deserialized implementation?
            value = value.to_json_string()
        except: AttributeError:
            # Assume it is already deserialized.
            pass
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
        test_data = self.suite_data.pop(test_name, dict())
        file_path = os.path.join(
            self.log_dir, self.suite_path_part, test_name + u".json.log"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, u"w") as file_out:
            file_out.write(json.dumps(test_data))
