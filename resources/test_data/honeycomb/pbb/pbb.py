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

"""Test variables for provider backbone bridge test suite."""

# pylint: disable=invalid-name

# Add pbb sub interface
# Configuration data
cfg_pbb_sub_if_1_ID = '1'
cfg_pbb_sub_if_1 = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_1_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:aa:ab",
                "destination-address": "bb:bb:bb:bb:bb:bc",
                "b-vlan-tag-vlan-id": "2223",
                "i-tag-isid": "12"
            },
        }
    ]
}

# Expected operational data:
oper_pbb_sub_if_1 = {
    'admin-status': 'up',
    'ietf-ip:ipv4': {},
    'oper-status': 'up',
    'sub-interfaces:sub-interfaces': {},
    'type': 'iana-if-type:ethernetCsmacd',
    'v3po:ethernet': {
        'duplex': 'full',
        'mtu': 9216
    }
}

# Modify pbb sub interface
# Configuration data
cfg_pbb_sub_if_1_ID = '2'
cfg_pbb_sub_if_1_mod = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_1_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:aa:de",
                "destination-address": "bb:bb:bb:bb:bb:ed",
                "b-vlan-tag-vlan-id": "2223",
                "i-tag-isid": "12"
            },
        }
    ]
}

# Expected operational data:
oper_pbb_sub_if_1_mod = {
    'admin-status': 'up',
    'ietf-ip:ipv4': {},
    'oper-status': 'up',
    'sub-interfaces:sub-interfaces': {},
    'type': 'iana-if-type:ethernetCsmacd',
    'v3po:ethernet': {
        'duplex': 'full',
        'mtu': 9216
    }
}

# Configuration data
cfg_pbb_sub_if_2_ID = '3'
cfg_pbb_sub_if_2 = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_2_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:aa:cc",
                "destination-address": "bb:bb:bb:bb:bb:dd",
                "b-vlan-tag-vlan-id": "10",
                "i-tag-isid": "20"
            },
        }
    ]
}

# Expected operational data:
oper_pbb_sub_if_2 = {
    'admin-status': 'up',
    'ietf-ip:ipv4': {},
    'oper-status': 'up',
    'sub-interfaces:sub-interfaces': {},
    'type': 'iana-if-type:ethernetCsmacd',
    'v3po:ethernet': {
        'duplex': 'full',
        'mtu': 9216
    }
}

# Configuration data
cfg_pbb_sub_if_3_ID = '4'
cfg_pbb_sub_if_3 = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_3_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:cc:aa",
                "destination-address": "bb:bb:bb:bb:dd:bb",
                "b-vlan-tag-vlan-id": "30",
                "i-tag-isid": "40"
            },
        }
    ]
}

# Expected operational data:
oper_pbb_sub_if_3 = {
    'admin-status': 'up',
    'ietf-ip:ipv4': {},
    'oper-status': 'up',
    'sub-interfaces:sub-interfaces': {},
    'type': 'iana-if-type:ethernetCsmacd',
    'v3po:ethernet': {
        'duplex': 'full',
        'mtu': 9216
    }
}

# Wrong configuration data
# Wrong source-address
cfg_pbb_sub_if_ID = '5'
cfg_pbb_sub_if_wrong_src_addr = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "ab:cd:ef:gh:ij",
                "destination-address": "bb:bb:bb:bb:bb:bc",
                "b-vlan-tag-vlan-id": "2223",
                "i-tag-isid": "12"
            },
        }
    ]
}

# Wrong destination-address
cfg_pbb_sub_if_wrong_dst_addr = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:aa:ab",
                "destination-address": "ab:cd:ef:gh:ij",
                "b-vlan-tag-vlan-id": "2223",
                "i-tag-isid": "12"
            },
        }
    ]
}

# Wrong b-vlan-tag-vlan-id
cfg_pbb_sub_if_wrong_vlan_tag = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:aa:ab",
                "destination-address": "bb:bb:bb:bb:bb:bc",
                "b-vlan-tag-vlan-id": "123456789",
                "i-tag-isid": "12"
            },
        }
    ]
}

# Wrong i-tag-isid
cfg_pbb_sub_if_wrong_i_tag = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:aa:ab",
                "destination-address": "bb:bb:bb:bb:bb:bc",
                "b-vlan-tag-vlan-id": "2223",
                "i-tag-isid": "167772152345"
            },
        }
    ]
}

# b-vlan-tag-vlan-id is missing
cfg_pbb_sub_if_no_vlan_tag = {
    "sub-interface": [
        {
            "identifier": cfg_pbb_sub_if_ID,
            "vlan-type": "dot1ah-types:802dot1ah",
            "enabled": "true",
            "admin-status": "up",
            "oper-status": "up",
            "pbb": {
                "source-address": "aa:aa:aa:aa:aa:ab",
                "destination-address": "bb:bb:bb:bb:bb:bc",
                "i-tag-isid": "12"
            },
        }
    ]
}
