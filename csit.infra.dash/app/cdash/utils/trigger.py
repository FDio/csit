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


"""A module implementing the processing of a trigger.
"""

from json import loads, JSONDecodeError


class Trigger:
    """
    """
    def __init__(self, trigger) -> None:
        """
        """
        self._id = trigger[0]["prop_id"].split(".")
        self._param = self._id[1]
        try:
            self._id = loads(self._id[0])
        except (JSONDecodeError, TypeError):
            # It is a string
            self._id = {"type": self._id[0], "index": None}
        self._val = trigger[0]["value"]

    def __str__(self) -> str:
        return (
            f"\nTrigger:\n"
            f"  ID:        {self._id}\n"
            f"  Type:      {self._id['type']}\n"
            f"  Index:     {self._id['index']}\n"
            f"  Parameter: {self._param}\n"
            f"  Value:     {self._val}\n"
        )

    @property
    def id(self) -> dict:
        return self._id
    
    @property
    def type(self) -> str:
        return self._id["type"]

    @property
    def idx(self) -> any:
        return self._id["index"]
    
    @property
    def parameter(self) -> str:
        return self._param

    @property
    def value(self) -> any:
        return self._val
