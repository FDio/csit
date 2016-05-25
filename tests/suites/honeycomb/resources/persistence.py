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
    # Vlan subinterface basic settings
    sub_interface_id = 10
    sub_interface_name = interface + '.' + str(sub_interface_id)

    variables = {
        # VxLan settings
        'vx_interface': 'vx_tunnel_test',
        'vxlan_settings': {'src': '192.168.0.2',
                           'dst': '192.168.0.3',
                           "vni": 88,
                           'encap-vrf-id': 0},
        # bridge domain settings
        'bd_name': 'bd_persist',
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
        'sub_interface_id': sub_interface_id,
        'sub_interface_name': sub_interface_name,
        'sub_interface_base_settings': {'name': sub_interface_name,
                                        'type': 'v3po:sub-interface'
                                        },
        'sub_interface_settings': {
            'super-interface': interface,
            'identifier': sub_interface_id,
            'vlan-type': '802dot1ad',
            'number-of-tags': 2,
            'outer-id': 22,
            'inner-id': 33,
            'match-any-outer-id': False,
            'match-any-inner-id': False,
            'exact-match': True,
            'default-subif': True
        }
    }
    return variables
