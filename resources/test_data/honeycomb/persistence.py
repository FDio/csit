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

"""Test variables for Honeycomb persistence test suite."""


def get_variables(interface):
    """Creates and returns dictionary of test variables.

    :param interface: name of super-interface for the tested sub-interface
    :type interface: str
    :return: dictionary of test variables
    :rtype: dict
    """
    # basic settings
    bd_name = 'bd_persist'
    sub_if_id = 1
    sub_if_name = interface + '.' + str(sub_if_id)

    variables = {
        # VxLan settings
        'vx_interface': 'vx_tunnel_test',
        'vxlan_settings': {'src': '192.168.0.2',
                           'dst': '192.168.0.3',
                           "vni": 88,
                           'encap-vrf-id': 0},
        # bridge domain settings
        'bd_name': bd_name,
        'bd_settings': {'flood': True,
                        'forward': True,
                        'learn': True,
                        'unknown-unicast-flood': True,
                        'arp-termination': True
                        },
        # tap interface settings
        'tap_interface': 'tap_test',
        'tap_settings': {'tap-name': 'tap_test',
                         'mac': '08:00:27:c0:5d:37',
                         'device-instance': 1
                         },
        # vhost-user interface settings
        'vhost_interface': 'test_vhost',
        'vhost_user_server': {'socket': 'soc1',
                              'role': 'server'
                              },
        # Vlan subinterface settings
        'sub_if_id': sub_if_id,
        'sub_if_name': sub_if_name,
        'sub_if_1_settings': {
            "identifier": sub_if_id,
            "vlan-type": "802dot1q",
            "enabled": "false"
            },
        'sub_if_1_tags': [
            {
                "index": "0",
                "dot1q-tag": {
                    "tag-type": "dot1q-types:s-vlan",
                    "vlan-id": "100"
                }
            },
            {
                "index": "1",
                "dot1q-tag": {
                    "tag-type": "dot1q-types:c-vlan",
                    "vlan-id": "any"
                }
            }
            ],
        'sub_if_1_match': "vlan-tagged-exact-match",
        'sub_if_1_oper': {
            "identifier": sub_if_id,
            "oper-status": "up",
            "admin-status": "up",
            "tags": {
                "tag": [
                    {
                        "index": 1,
                        "dot1q-tag": {
                            "tag-type": "dot1q-types:c-vlan",
                            "vlan-id": "any"
                        }
                    },
                    {
                        "index": 0,
                        "dot1q-tag": {
                            "tag-type": "dot1q-types:s-vlan",
                            "vlan-id": "100"
                        }
                    }
                ]
            },
            "match": {
                "vlan-tagged": {
                    "match-exact-tags": False
                }
            }
        },
        'sub_bd_settings': {
            'bridge-domain': bd_name,
            'split-horizon-group': '1',
            'bridged-virtual-interface': 'False'
        },
        'tag_rewrite_pop_1': {
            "pop-tags": "1"
        },

        'tag_rewrite_pop_1_oper': {
            "vlan-type": "vpp-vlan:802dot1ad",
            "pop-tags": 1
        },

        'tag_rewrite_pop_1_VAT': {
            'sub_default': 0,
            'sub_dot1ad': 0,
            'sub_exact_match': 0,
            'sub_inner_vlan_id': 0,
            'sub_inner_vlan_id_any': 1,
            'sub_number_of_tags': 2,
            'sub_outer_vlan_id': 100,
            'sub_outer_vlan_id_any': 0,
            'vtr_op': 3,
            'vtr_push_dot1q': 0,
            'vtr_tag1': 0,
            'vtr_tag2': 0
        }
    }
    return variables
