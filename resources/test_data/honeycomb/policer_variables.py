# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""Test variables for Policer test suite."""


def get_variables():
    """Create and return a dictionary of test variables for the specified
    test case.

    :returns: Dictionary of test variables - settings for Honeycomb's Policer.
    :rtype: dict
    """
    policer_data = {
        "policer_data": {
            "name": "policy1",
            "cir": 450,
            "cb": 50000,
            "rate-type": "kbps",
            "round-type": "closest",
            "type": "1r2c",
            "conform-action": {
                "meter-action-type": "meter-action-transmit"
            },
            "exceed-action": {
                "meter-action-type": "meter-action-drop"
            }
        },
        "policer_data_oper": {
            "name": "policy1",
            "cir": 450,
            "cb": 50000,
            "rate-type": "kbps",
            "round-type": "closest",
            "type": "1r2c",
            "conform-action": {
                "meter-action-type": "policer:meter-action-transmit"
            },
            "exceed-action": {
                "meter-action-type": "policer:meter-action-drop"
            }
        },
        "policer_data_2": {
            "name": "policy1",
            "cir": 900,
            "cb": 50000,
            "rate-type": "kbps",
            "round-type": "closest",
            "type": "1r2c",
            "conform-action": {
                "meter-action-type": "meter-action-transmit"
            },
            "exceed-action": {
                "meter-action-type": "meter-action-drop"
            }
        },
        "policer_data_oper_2": {
            "name": "policy1",
            "cir": 900,
            "cb": 50000,
            "rate-type": "kbps",
            "round-type": "closest",
            "type": "1r2c",
            "conform-action": {
                "meter-action-type": "policer:meter-action-transmit"
            },
            "exceed-action": {
                "meter-action-type": "policer:meter-action-drop"
            }
        },
        "policer_data_3": {
            "name": "policy1",
            "cir": 100,
            "eir": 150,
            "cb": 200,
            "eb": 300,
            "rate-type": "pps",
            "round-type": "closest",
            "type": "2r3c-2698",
            "conform-action": {
                "meter-action-type": "meter-action-transmit"
            },
            "exceed-action": {
                "meter-action-type": "meter-action-mark-dscp",
                "dscp": "AF22"
            },
            "violate-action": {
                "meter-action-type": "meter-action-drop"
            },
            "color-aware": True
            },
        "policer_data_oper_3": {
            "name": "policy1",
            "cir": 100,
            "eir": 150,
            "cb": 200,
            "eb": 300,
            "rate-type": "pps",
            "round-type": "closest",
            "type": "2r3c-2698",
            "conform-action": {
                "meter-action-type": "policer:meter-action-transmit"
            },
            "exceed-action": {
                "meter-action-type": "policer:meter-action-mark-dscp",
                "dscp": "AF22"
            },
            "violate-action": {
                "meter-action-type": "policer:meter-action-drop"
            },
            "color-aware": True
        },

        "acl_tables": {
            # settings for policer tables
            "hc_acl_table": {
                "name": "table0",
                "nbuckets": 2,
                "memory_size": 1048576,
                "skip_n_vectors": 12,
                "miss_next": "permit",
                "mask": "00:00:00:00:00:00:00:00:00:00:00:00:ff:ff:ff:ff"
            },
            # setting for acl sessions
            "hc_acl_session": {
                "match": "00:00:00:00:00:00:00:00:00:00:00:00:C0:A8:7A:01",
                "policer_hit_next": "policy1",
                "color_classfier": "exceed-color",
            },
            "hc_acl_session2": {
                "match": "00:00:00:00:00:00:00:00:00:00:00:00:C0:A8:7A:02",
                "policer_hit_next": "policy1",
                "color_classfier": "exceed-color",
            },
        },
    }
    return policer_data
