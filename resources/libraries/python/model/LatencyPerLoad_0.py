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


class LatencyPerLoad_0:
    """Hold latency results for one direction and load.
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

    def __init__(self, l_min, l_avg, l_max, hdrh):
        """Construct the instance by storing the values needed.

        Convert arguments so caller do not have to.

        TODO: Use the real implementation of HDRhistogram, not serialization.

        :param l_min: Minimal latency value [us].
        :param l_avg: Average latency value [us].
        :param l_max: Maximal latency value [us].
        :param hdrh: HDRHistogram serialized data.
        :type l_min: int
        :type l_avg: int
        :type l_max: int
        :type hdrh: str
        """
        self.l_min = int(l_min)
        self.l_avg = int(l_avg)
        self.l_max = int(l_max)
        self.hdrh = str(hdrh)

    # TODO: __str__, __repr__.

    def to_plain_string(self):
        """Return quoteless string with json representation according to model.

        Currently it is the usual min/avg/max/hdrh string.

        :returns: A string serialization of self.
        :rtype: str
        """
        return (
            f'{self.l_min}/'
            f'{self.l_avg}/'
            f'{self.l_max}/'
            f'{self.hdrh}'
        )

    def to_json_string(self):
        """Return string with json representation according to model.

        Strictly speaking it is not a full json, just a string in double quotes.

        :returns: JSON string, not pretty-formatted.
        :rtype: str
        """
        return u'"' + self.to_plain_string() + u'"'

    @classmethod
    def from_plain_string(cls, plain_string):
        """Return new instance with data from an unquoted string.

        TODO: Document possibly raised exceptions.

        :param plain_string: The usual min/avg/max/hdrh string.
        :type plain_string: str
        :returns: The new instance.
        :rtype: cls
        """
        l_min, l_avg, l_max, hdrh = plain_string.split(u"/", 3)
        return cls(
            l_min=l_min,
            l_avg=l_avg,
            l_max=l_max,
            hdrh=hdrh,
        )

    @classmethod
    def from_json_string(cls, json_string):
        """Return new instance with data from json string.

        Well, it is just a string in double quotes, not a full json.

        :param json_string: JSON generated with compatible to_json_string.
        :type json_string: str
        :returns: The new instance.
        :rtype: cls
        """
        return cls.from_plain_string(json_string[1:-1])
