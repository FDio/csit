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
    slaac_data = {
        "address": "10::10",
        "prefix": 64,
        "slaac_data": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "100",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_04": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "5",
            "max-rtr-adv-interval": "100",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_05": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "100",
            "default-lifetime": "121",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_06": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "100",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "True",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_07": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "100",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "1",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_08": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "100",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "2"
        },
        "slaac_data_09": {
            "send-advertisements": "False",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "300",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "True",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_10": {
            "send-advertisements": "False",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "500",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_11": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "600",
            "default-lifetime": "601",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_12": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "60",
            "default-lifetime": "61",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_13": {
            "send-advertisements": "False",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "60",
            "default-lifetime": "61",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_14": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "60",
            "default-lifetime": "61",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_15": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "60",
            "default-lifetime": "61",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_16": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "40",
            "default-lifetime": "41",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_17": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "30",
            "default-lifetime": "31",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
        "slaac_data_18": {
            "send-advertisements": "True",
            "min-rtr-adv-interval": "20",
            "max-rtr-adv-interval": "28",
            "default-lifetime": "29",
            "vpp-routing-ra:suppress-link-layer": "False",
            "vpp-routing-ra:initial-count": "2",
            "vpp-routing-ra:initial-interval": "15"
        },
    }
    return slaac_data
