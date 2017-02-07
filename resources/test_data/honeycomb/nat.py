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

"""Test variables for NAT test suite."""

from resources.libraries.python.topology import Topology


def get_variables(node, interface):
    """Create and return a dictionary of test variables.

    :param node: Honeycomb node.
    :param interface: Name, link name or sw_if_index of an interface.
    :type node: dict
    :type interface: str or int

    :returns: Dictionary of test variables - settings for Honeycomb's
    NAT node and expected operational data.
    :rtype: dict
    """
    sw_if_index = Topology.convert_interface_reference(
        node, interface, "sw_if_index")

    variables = {
        "nat_empty": {
            'nat-instances': {
                'nat-instance': [{
                    'id': 0}]
            }
        },
        "entry1": {
            "mapping-entry": [{
                "index": 1,
                "type": "static",
                "internal-src-address": "192.168.0.1",
                "external-src-address": "192.168.1.1"
            }]
        },
        "entry2": {
            "mapping-entry": [{
                "index": 2,
                "type": "static",
                "internal-src-address": "192.168.0.2",
                "external-src-address": "192.168.1.2"
            }]
        },
        "entry1_2_oper": {
            "mapping-entry": [
                {
                    "index": 1,
                    "type": "static",
                    "internal-src-address": "192.168.0.1",
                    "external-src-address": "192.168.1.1"
                },
                {
                    "index": 2,
                    "type": "static",
                    "internal-src-address": "192.168.0.2",
                    "external-src-address": "192.168.1.2"
                }
            ]
        },
        "entry1_vat": [{
            "local_address": "192.168.0.1",
            "remote_address": "192.168.1.1",
            "vrf": "0"
        }],
        "entry1_2_vat": [
            {
                "local_address": "192.168.0.1",
                "remote_address": "192.168.1.1",
                "vrf": "0",
                "protocol": "17"
            }, {
                "local_address": "192.168.0.2",
                "remote_address": "192.168.1.2",
                "vrf": "0",
                "protocol": "17"
            }
        ],
        "nat_interface_vat_in": [
            {"sw_if_index": str(sw_if_index),
             "direction": "in"}
        ],
        "nat_interface_vat_out": [
            {"sw_if_index": str(sw_if_index),
             "direction": "out"}
        ]
    }

    return variables
