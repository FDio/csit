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

    def __init__(self, instance_key):
        """FIXME.
        """
        data = self.__class__.data
        self.instance_data = data.get(instance_key, dict())
        data[instance_key] = self.instance_data

    def update(self, sub_key, value):
        """FIXME.
        """
        self.instance_data[sub_key] = value

    def get(self, sub_key, default_value=None):
        """FIXME.
        """
        return self.instance_data.get(sub_key, default_value)

    def dump(self, filename):
        """FIXME.
        """
        with open(filename, u"w") as file_out:
            file_out.write(json.dumps(self.__class__.data))
