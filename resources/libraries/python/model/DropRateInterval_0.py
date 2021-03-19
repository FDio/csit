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


class DropRateInterval_0:
    """Hold results specific to NDR or PDR.
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

    def __init__(self, lower_bound, upper_bound, unit_string):
        """Construct the instance by storing the values needed.

        Convert arguments so caller do not have to.

        TODO: Use an enum class for units (instead of unit string).

        TODO: Compute bandwidth from pps.

        :param lower_bound: Lower bound load value, in units.
        :param upper_bound: Upper bound load value, in units.
        :param unit_string: Units, usually "pps" or "cps".
        :type lower_bound: float
        :type upper_bound: float
        :type units_string: str
        """
        self.lower_bound = float(lower_bound)
        self.upper_bound = float(upper_bound)
        self.unit_string = str(unit_string)

    # TODO: __str__, __repr__.

    def to_json_dict(self):
        """Return dict suitable for JSON serialization.

        :returns: Minimalistic object as if deserialized from JSON string.
        :rtype: dict
        """
        return {
            "unit": self.unit_string,
            "value": {
                "lower": self.lower_bound,
                "upper": self.upper_bound,
            }
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
            lower_bound=json_dict[u"value"][u"lower"],
            upper_bound=json_dict[u"value"][u"upper"],
            unit_string=json_dict[u"unit"],
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
