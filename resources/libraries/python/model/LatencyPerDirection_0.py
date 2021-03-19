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

"""Module holding an eponymous class."""

import json

from resources.libraries.python.model.LatencyPerLoad_0 impor LatencyPerLoad_0


class LatencyPerDirection_0:
    """Hold latency results for one direction, multiple loads.
    """

    # We use semantic versioning.
    # Backward incompatible edit bump major version,
    # backward compatible but forward incompatible edit bumps minor version,
    # fully compatible edit bumps patch version.
    # Backward compatible means newer version of this class
    # creates json (to_json) readable with older version of PAL (from_json).

    # Major version number is in the class name.
    version_minor = 0
    version_patch = 0

    # TODO: Document global model version compatible with this?

    def __init__(self, l_90, l_50, l_10, l_0):
        """Construct the instance by storing the values needed.

        :param l_90: Latency result for 90% PDR load.
        :param l_50: Latency result for 50% PDR load.
        :param l_10: Latency result for 10% PDR load.
        :param l_0: Latency result for 0% PDR load.
        :type l_90: LatencyPerLoad_0
        :type l_50: LatencyPerLoad_0
        :type l_10: LatencyPerLoad_0
        :type l_0: LatencyPerLoad_0
        """
        self.l_90 = l_90
        self.l_50 = l_50
        self.l_10 = l_10
        self.l_0 = l_0

    # TODO: __str__, __repr__.

    def to_json_dict(self):
        """Return dict suitable for JSON serialization.

        :returns: Minimalistic object as if deserialized from JSON string.
        :rtype: dict
        """
        return {
            "pdr-90": self.l_90.to_plain_string(),
            "pdr-50": self.l_50.to_plain_string(),
            "pdr-10": self.l_10.to_plain_string(),
            "pdr-0": self.l_0.to_plain_string(),
        }

    def to_json_string(self):
        """Return string with json representation according to model.

        :returns: JSON string, not pretty-formatted.
        :rtype: str
        """
        return json.dumps(self.to_json_dict())

    @classmethod
    def from_json_dict(cls, json_dict):
        """Return new instance with data from parsed json dictionary.

        TODO: Document possibly raised exceptions.

        :param json_dict: JSON object generated with compatible to_json_dict.
        :type json_dict: dict
        :returns: The new instance.
        :rtype: cls
        """
        return cls(
            l_90=LatencyPerLoad_0.from_json_dict(json_dict[u"pdr-90"]),
            l_50=LatencyPerLoad_0.from_json_dict(json_dict[u"pdr-50"]),
            l_10=LatencyPerLoad_0.from_json_dict(json_dict[u"pdr-10"]),
            l_0=LatencyPerLoad_0.from_json_dict(json_dict[u"pdr-0"]),
        )

    @classmethod
    def from_json_string(cls, json_string):
        """Return new instance with data from json string.

        TODO: Document possibly raised exceptions.

        :param json_string: JSON generated with compatible to_json_string.
        :type json_string: str
        :returns: The new instance.
        :rtype: cls
        """
        json_dict = json.loads(json_string)
        return cls.from_json_dict(json_dict)
