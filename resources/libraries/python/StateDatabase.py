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

    # Class cache for reuse between instances.
    data = dict()

    def __init__(self, suite_name):
        """FIXME.
        """
        data = self.__class__.data
        self.suite_data = data.get(suite_name, dict())
        data[suite_name] = self.suite_data

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

    def database_dump(self, filename):
        """FIXME.
        """
        with open(filename, u"w") as file_out:
            file_out.write(json.dumps(self.__class__.data))
