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

"""Test variables for LISP test suite."""

nsh_entry1 = {
    "nsh-entry": [{
        "name": "entry1",
        "version": 0,
        "length": 6,
        "md-type": "md-type1",
        "next-protocol": "ethernet",
        "nsp": 184,
        "nsi": 255,
        "c1": 1,
        "c2": 2,
        "c3": 3,
        "c4": 4
    }]
}

nsh_entry1_oper = {
    "nsh-entry": [{
        "name": "entry1",
        "version": 0,
        "length": 6,
        "md-type": "vpp-nsh:md-type1",
        "next-protocol": "vpp-nsh:ethernet",
        "nsp": 184,
        "nsi": 255,
        "c1": 1,
        "c2": 2,
        "c3": 3,
        "c4": 4
    }]
}

nsh_entry2 = {
    "nsh-entry": [{
        "name": "entry2",
        "version": 0,
        "length": 5,
        "md-type": "md-type1",
        "next-protocol": "ethernet",
        "nsp": 183,
        "nsi": 254,
        "c1": 2,
        "c2": 3,
        "c3": 4,
        "c4": 5
    }]
}

nsh_entry2_oper = {
    "nsh-entry": [{
        "name": "entry2",
        "version": 0,
        "length": 5,
        "md-type": "vpp-nsh:md-type1",
        "next-protocol": "vpp-nsh:ethernet",
        "nsp": 183,
        "nsi": 254,
        "c1": 2,
        "c2": 3,
        "c3": 4,
        "c4": 5
    }]
}

# Settings for VxLAN GPE interfaces, needed to configure NSH maps
vxlan_gpe_if1 = 'vxlan_gpe_test1'
vxlan_gpe_base_settings1 = {
    'name': vxlan_gpe_if1,
    'description': 'for testing NSH',
    'enabled': True,
    'link-up-down-trap-enable': 'enabled'
}
vxlan_gpe_settings1 = {
    'local': '192.168.0.1',
    'remote': '192.168.0.2',
    'vni': 5,
    'next-protocol': 'ethernet',
    'encap-vrf-id': 0,
    'decap-vrf-id': 0
}

vxlan_gpe_if2 = 'vxlan_gpe_test2'
vxlan_gpe_base_settings2 = {
    'name': vxlan_gpe_if2,
    'description': 'for testing NSH',
    'enabled': True,
    'link-up-down-trap-enable': 'enabled'
}
vxlan_gpe_settings2 = {
    'local': '192.168.1.1',
    'remote': '192.168.1.2',
    'vni': 6,
    'next-protocol': 'ethernet',
    'encap-vrf-id': 0,
    'decap-vrf-id': 0
}


nsh_map1 = {
    "nsh-map": [{
        "name": "map1",
        "nsp": 184,
        "nsi": 255,
        "mapped-nsp": 183,
        "mapped-nsi": 254,
        "nsh-action": "push",
        "encap-type": "vxlan-gpe",
        "encap-if-name": vxlan_gpe_if1
    }]
}

nsh_map1_oper = {
    "nsh-map": [{
        "name": "map1",
        "nsp": 184,
        "nsi": 255,
        "mapped-nsp": 183,
        "mapped-nsi": 254,
        "nsh-action": "vpp-nsh:push",
        "encap-type": "vpp-nsh:vxlan-gpe",
        "encap-if-name": vxlan_gpe_if1
    }]
}

nsh_map1_edit = {
    "nsh-map": [{
        "name": "map1_edit",
        "nsp": 184,
        "nsi": 255,
        "mapped-nsp": 184,
        "mapped-nsi": 253,
        "nsh-action": "push",
        "encap-type": "vxlan-gpe",
        "encap-if-name": vxlan_gpe_if1
    }]
}

nsh_map1_edit_oper = {
    "nsh-map": [{
        "name": "map1_edit",
        "nsp": 184,
        "nsi": 255,
        "mapped-nsp": 184,
        "mapped-nsi": 253,
        "nsh-action": "vpp-nsh:push",
        "encap-type": "vpp-nsh:vxlan-gpe",
        "encap-if-name": vxlan_gpe_if1
    }]
}

nsh_map2 = {
    "nsh-map": [{
        "name": "map2",
        "nsp": 183,
        "nsi": 254,
        "mapped-nsp": 182,
        "mapped-nsi": 253,
        "nsh-action": "vpp-nsh:push",
        "encap-type": "vpp-nsh:vxlan-gpe",
        "encap-if-name": vxlan_gpe_if2
    }]
}

nsh_map2_oper = {
    "nsh-map": [{
        "name": "map2",
        "nsp": 183,
        "nsi": 254,
        "mapped-nsp": 182,
        "mapped-nsi": 253,
        "nsh-action": "vpp-nsh:push",
        "encap-type": "vpp-nsh:vxlan-gpe",
        "encap-if-name": vxlan_gpe_if2
    }]
}
