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


class NdrpdrResult_0:
    """Hold rate and latency results of Ndrpdr test.
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

    def __init__(
            self,
            pdr_interval,
            ndr_interval,
            forward_latency,
            reverse_latency=None,
        ):
        """Construct the instance by storing the values needed.

        The reverse latency can be missing (e.g. unidirectional test).

        :param pdr_interval: Bounds for PDR.
        :param ndr_interval: Bunds for NDR.
        :param forward_latency: Latency for the primary traffic direction.
        :param reverse_latency: Latency for the secondary traffic direction.
        :type pdr_interval: DropRateInterval_0
        :type ndr_interval: DropRateInterval_0
        :type forward_latency: LatencyPerDirection_0
        :type reverse_latency: LatencyPerDirection_0
        """
        self.pdr_interval = pdr_interval
        self.ndr_interval = ndr_interval
        self.forward_latency = forward_latency
        self.reverse_latency = reverse_latency

    # TODO: __repr__.

    def to_json_dict(self):
        """Return dict suitable for JSON serialization.

        :returns: Minimalistic object as if deserialized from JSON string.
        :rtype: dict
        """
        ret_dict = {
            "ndr": self.ndr_interval.to_json_dict(),
            "pdr": self.pdr_interval.to_json_dict(),
            "hdrh": {
                "forward": self.forward_latency.to_json_dict(),
            }
        }
        if self.reverse_latency is not None:
            ret_dict[u"hdrh"][u"reverse"] = self.reverse_latency.to_json_dict()
        return ret_dict

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
        reverse = json_dict[u"hdrh"].get(u"reverse", None)
        if reverse is not None:
            reverse = LatencyPerDirection.from_json_dict(reverse)
        return cls(
            ndr_interval=DropRateInterval.from_json_dict(json_dict[u"ndr"]),
            pdr_interval=DropRateInterval.from_json_dict(json_dict[u"pdr"]),
            forward_latency=LatencyPerDirection.from_json_dict(
                json_dict[u"hdrh"][u"forward"]
            ),
            reverse_latency=reverse,
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
