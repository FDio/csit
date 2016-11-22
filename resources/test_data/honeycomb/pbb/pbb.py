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
cfg_pbb_sub_if_1 = {
    "pbb-rewrite": {
        "source-address": "aa:aa:aa:aa:aa:ab",
        "destination-address": "bb:bb:bb:bb:bb:bc",
        "b-vlan-tag-vlan-id": "2223",
        "outer-tag": "16",
        "i-tag-isid": "12",
        "interface-operation": "translate-2-1"
    }
}

# Modify pbb sub interface
# Configuration data
cfg_pbb_sub_if_1_mod = {
    "pbb-rewrite": {
        "source-address": "aa:aa:aa:aa:aa:ac",
        "destination-address": "bb:bb:bb:bb:bb:bd",
        "b-vlan-tag-vlan-id": "2224",
        "outer-tag": "17",
        "i-tag-isid": "13",
        "interface-operation": "push-2"
    }
}

# Wrong configuration data
# Wrong source-address
cfg_pbb_sub_if_ID = '5'
cfg_pbb_sub_if_wrong_src_addr = {
    "pbb-rewrite": {
        "source-address": "aa:aa:aa:aa:aa:ag",
        "destination-address": "bb:bb:bb:bb:bb:ce",
        "b-vlan-tag-vlan-id": "2226",
        "outer-tag": "19",
        "i-tag-isid": "15",
        "interface-operation": "pop-2"
    }
}

# Wrong destination-address
cfg_pbb_sub_if_wrong_dst_addr = {
    "pbb-rewrite": {
        "source-address": "aa:aa:aa:aa:aa:ae",
        "destination-address": "bb:bb:bb:bb:bb:cg",
        "b-vlan-tag-vlan-id": "2226",
        "outer-tag": "19",
        "i-tag-isid": "15",
        "interface-operation": "pop-2"
    }
}

# Wrong b-vlan-tag-vlan-id
cfg_pbb_sub_if_wrong_vlan_tag = {
    "pbb-rewrite": {
        "source-address": "aa:aa:aa:aa:aa:ae",
        "destination-address": "bb:bb:bb:bb:bb:ce",
        "b-vlan-tag-vlan-id": "123456789",
        "outer-tag": "19",
        "i-tag-isid": "15",
        "interface-operation": "pop-2"
    }
}

# Wrong i-tag-isid
cfg_pbb_sub_if_wrong_i_tag = {
    "pbb-rewrite": {
        "source-address": "aa:aa:aa:aa:aa:ae",
        "destination-address": "bb:bb:bb:bb:bb:ce",
        "b-vlan-tag-vlan-id": "2226",
        "outer-tag": "19",
        "i-tag-isid": "167772152345",
        "interface-operation": "pop-2"
    }
}

# b-vlan-tag-vlan-id is missing
cfg_pbb_sub_if_no_vlan_tag = {
    "pbb-rewrite": {
        "source-address": "aa:aa:aa:aa:aa:ae",
        "destination-address": "bb:bb:bb:bb:bb:ce",
        "outer-tag": "19",
        "i-tag-isid": "15",
        "interface-operation": "pop-2"
    }
}
