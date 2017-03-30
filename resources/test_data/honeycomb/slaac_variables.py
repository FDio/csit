# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Test variables for SLAAC test suite."""


def get_variables():
    """Create and return a dictionary of test variables for the specified
    test case.

    :returns: Dictionary of test variables - settings for Honeycomb's SLAAC.
    :rtype: dict
    """
    slaac_data = {
        "address": "10::10",
        "prefix": 64,
        "slaac_data": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "15",
            "max-rtr-adv-interval": "100",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "3",
            "vpp-routing-ra:initial-interval": "5"
        },
        "slaac_data_01": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "3",
            "max-rtr-adv-interval": "4",
            "default-lifetime": "8",
            "vpp-routing-ra:suppress-link-layer": "True",
            "vpp-routing-ra:initial-count": "1",
            "vpp-routing-ra:initial-interval": "1"
        },
        "slaac_data_02": {
            "send-advertisements": "False",
            "min-rtr-adv-interval": "3",
            "max-rtr-adv-interval": "4",
            "default-lifetime": "5",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "1",
            "vpp-routing-ra:initial-interval": "1"
        },
        "slaac_data_03": {
            "send-advertisements": "False",
            "min-rtr-adv-interval": "1350",
            "max-rtr-adv-interval": "1800",
            "default-lifetime": "9000",
            "vpp-routing-ra:suppress-link-layer": "True",
            "vpp-routing-ra:initial-count": "3",
            "vpp-routing-ra:initial-interval": "16"
        },
    }
    return slaac_data
