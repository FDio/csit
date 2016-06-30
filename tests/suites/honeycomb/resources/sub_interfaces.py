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

"""Test variables for Honeycomb sub-interface test suite."""

# Sub-interface 1 and its settings:
sub_if_1_settings = {
    "identifier": "1",
    "vlan-type": "802dot1q",
    "enabled": "false"
}

sub_if_1_tags = [
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
]

sub_if_1_match = "vlan-tagged-exact-match"

# Expected operational data: sub-interface.
sub_if_1_oper = {
    "identifier": 1,
    "oper-status": "down",
    "admin-status": "down",
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
}

# Bridge domain name.
bd_name = 'test-sub-bd'

# Bridge domain settings used while creating a test bridge domain.
bd_settings = {
    'flood': True,
    'forward': True,
    'learn': True,
    'unknown-unicast-flood': True,
    'arp-termination': True
}

# Bridge domain configuration used while adding the sub-interface to the bridge
# domain.
sub_bd_settings = {
    'bridge-domain': bd_name,
    'split-horizon-group': 1,
    'bridged-virtual-interface': False
}

# Configuration data: Enable tag-rewrite push.
tag_rewrite_push = {
    "vlan-type": "vpp-vlan:802dot1q",
    "push-tags": [
        {
            "index": 0,
            "dot1q-tag": {
                "tag-type": "dot1q-types:s-vlan",
                "vlan-id":123
            }
        },
        {
            "index": 1,
            "dot1q-tag": {
                "tag-type": "dot1q-types:c-vlan",
                "vlan-id": 456
            }
        }
    ]
}

# Expected operational data: tag-rewrite push.
tag_rewrite_push_oper = {
    "vlan-type": "vpp-vlan:802dot1q",
    "push-tags": [
        {
            "index": 1,
            "dot1q-tag": {
                "tag-type": "dot1q-types:c-vlan",
                "vlan-id": 456
            }
        },
        {
            "index": 0,
            "dot1q-tag": {
                "tag-type": "dot1q-types:s-vlan",
                "vlan-id": 123
            }
        }
    ]
}

# Expected VAT data: tag-rewrite push.
tag_rewrite_push_VAT = {
    'sub_default': 0,
    'sub_dot1ad': 0,
    'sub_exact_match': 0,
    'sub_inner_vlan_id': 0,
    'sub_inner_vlan_id_any': 1,
    'sub_number_of_tags': 2,
    'sub_outer_vlan_id': 100,
    'sub_outer_vlan_id_any': 0,
    'vtr_op': 2,
    'vtr_push_dot1q': 1,
    'vtr_tag1': 123,
    'vtr_tag2': 456
}

# Configuration data: Enable tag-rewrite pop 1.
tag_rewrite_pop_1 = {
    "pop-tags": "1"
}

# Expected operational data: tag-rewrite pop 1.
tag_rewrite_pop_1_oper = {
    "vlan-type": "vpp-vlan:802dot1ad",
    "pop-tags": 1
}

# Expected VAT data: tag-rewrite pop 1.
tag_rewrite_pop_1_VAT = {
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

# Configuration data: Enable tag-rewrite translate 1-2.
tag_rewrite_translate_1_2 = {
    "vlan-type": "vpp-vlan:802dot1q",
    "pop-tags": "1",
    "push-tags": [
        {
            "index": 0,
            "dot1q-tag": {
                "tag-type": "dot1q-types:s-vlan",
                "vlan-id": 111
            }
        },
        {
            "index": 1,
            "dot1q-tag": {
                "tag-type": "dot1q-types:c-vlan",
                "vlan-id": 222
            }
        }
    ]
}

# Expected operational data: tag-rewrite translate 1-2.
tag_rewrite_translate_1_2_oper = {
    "vlan-type": "vpp-vlan:802dot1q",
    "pop-tags": 1,
    "push-tags": [
        {
            "index": 1,
            "dot1q-tag": {
                "tag-type": "dot1q-types:c-vlan",
                "vlan-id": 222
            }
        },
        {
            "index": 0,
            "dot1q-tag": {
                "tag-type": "dot1q-types:s-vlan",
                "vlan-id": 111
            }
        }
    ]
}

# Expected VAT data: tag-rewrite translate 1-2.
tag_rewrite_translate_1_2_VAT = {
    'sub_default': 0,
    'sub_dot1ad': 0,
    'sub_exact_match': 0,
    'sub_inner_vlan_id': 0,
    'sub_inner_vlan_id_any': 1,
    'sub_number_of_tags': 2,
    'sub_outer_vlan_id': 100,
    'sub_outer_vlan_id_any': 0,
    'vtr_op': 6,
    'vtr_push_dot1q': 1,
    'vtr_tag1': 111,
    'vtr_tag2': 222
}

# Configuration data: Disable tag-rewrite.
tag_rewrite_disabled = {}

# Expected VAT data: Disable tag-rewrite.
tag_rewrite_disabled_VAT = {
    'sub_default': 0,
    'sub_dot1ad': 0,
    'sub_exact_match': 0,
    'sub_inner_vlan_id': 0,
    'sub_inner_vlan_id_any': 1,
    'sub_number_of_tags': 2,
    'sub_outer_vlan_id': 100,
    'sub_outer_vlan_id_any': 0,
    'vtr_op': 0,
    'vtr_push_dot1q': 0,
    'vtr_tag1': 0,
    'vtr_tag2': 0
}

# Configuration data:
# Wrong vlan-type for enable tag-rewrite translate 1-2.
tag_rewrite_translate_1_2_wrong = {
    "vlan-type": "vpp-vlan:WRONG",
    "pop-tags": "1",
    "push-tags": [
        {
            "index": 0,
            "dot1q-tag": {
                "tag-type": "dot1q-types:s-vlan",
                "vlan-id": 111
            }
        },
        {
            "index": 1,
            "dot1q-tag": {
                "tag-type": "dot1q-types:c-vlan",
                "vlan-id": 222
            }
        }
    ]
}

# IP addresses configured on sub-interface during tests
ipv4 = {
    "address": "192.168.0.4",
    "netmask": "255.255.255.0",
    "prefix-length": 24}
ipv4_2 = {
    "address": "192.168.0.5",
    "netmask": "255.255.0.0",
    "prefix-length": 16}
