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

"""Test variables for Honeycomb VxLAN GPE management test suite."""

# The first VxLAN GPE Interface used in tests.
vxlan_gpe_if1 = 'vxlan_gpe_tunnel0'
vxlan_gpe_base_settings = {
    'name': vxlan_gpe_if1,
    'description': 'for testing purposes',
    'enabled': True,
    'link-up-down-trap-enable': 'enabled'
}
vxlan_gpe_settings = {
    'local': '192.168.50.76',
    'remote': '192.168.50.71',
    'vni': 9,
    'next-protocol': 'ipv4',
    'encap-vrf-id': 0,
    'decap-vrf-id': 0
}

# The values of parameters of disabled VxLAN GPE interface.
vxlan_gpe_disabled_base_settings = {
    'name': vxlan_gpe_if1,
    'description': 'for testing purposes',
    'enabled': 'false'
}

# Wrong interface type.
vxlan_gpe_if2 = 'vxlan_gpe_tunnel1'
vxlan_gpe_wrong_type_base_settings = {
    'name': vxlan_gpe_if2,
    'type': 'iana-if-type:ethernetCsmacd',
    'description': 'for testing purposes',
    'enabled': True,
    'link-up-down-trap-enable': 'enabled'
}

# Wrong next-protocol value.
vxlan_gpe_if3 = 'vxlan_gpe_tunnel1'
vxlan_gpe_wrong_protocol_base_settings = {
    'name': vxlan_gpe_if3,
    'description': 'for testing purposes',
    'enabled': 'true',
    'link-up-down-trap-enable': 'enabled'
}
vxlan_gpe_wrong_protocol_settings = {
    'local': '192.168.50.77',
    'remote': '192.168.50.72',
    'vni': 9,
    'next-protocol': 'wrong_ipv4',
    'encap-vrf-id': 0,
    'decap-vrf-id': 0
}

# The first IPv6 VxLAN GPE interface.
vxlan_gpe_if5 = 'vxlan_gpe_tunnel0'
vxlan_gpe_base_ipv6_settings = {
    'name': vxlan_gpe_if5,
    'description': 'for testing purposes',
    'enabled': True,
    'link-up-down-trap-enable': 'enabled'
}
vxlan_gpe_ipv6_settings = {
    'local': '10:10:10:10:10:10:10:10',
    'remote': '10:10:10:10:10:10:10:11',
    'vni': 9,
    'next-protocol':'ipv4',
    'encap-vrf-id': 0,
    'decap-vrf-id': 0
}

# The second IPv6 VxLAN GPE interface.
vxlan_gpe_if6 = 'vxlan_gpe_tunnel1'
vxlan_gpe_base_ipv6_settings2 = {
    'name': vxlan_gpe_if6,
    'description': 'for testing purposes',
    'enabled': True,
    'link-up-down-trap-enable': 'enabled'
}
vxlan_gpe_ipv6_settings2 = {
    'local': '10:10:10:10:10:10:10:20',
    'remote': '10:10:10:10:10:10:10:21',
    'vni': 9,
    'next-protocol': 'ipv4',
    'encap-vrf-id': 0,
    'decap-vrf-id': 0
}
