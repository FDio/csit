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
        "policer_data": [
            {
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
            }
        ],
        "policer_data_compare": [
            {
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
            }
        ],
        "policer_data_2": [
            {
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
            }
        ],
        "policer_data_compare_2": [
            {
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
            }
        ],
        "policer_data_3": [
            {
                "name": "policy1",
                "cir": 1500,
                "cb": 500000,
                "rate-type": "kbps",
                "round-type": "closest",
                "type": "1r2c",
                "conform-action": {
                    "meter-action-type": "meter-action-transmit"
                },
                "exceed-action": {
                    "meter-action-type": "meter-action-drop"
                }
            }
        ],
        "policer_data_compare_3": [
            {
                "name": "policy1",
                "cir": 1500,
                "cb": 500000,
                "rate-type": "kbps",
                "round-type": "closest",
                "type": "1r2c",
                "conform-action": {
                    "meter-action-type": "policer:meter-action-transmit"
                },
                "exceed-action": {
                    "meter-action-type": "policer:meter-action-drop"
                }
            }
        ],
        "classifiers": {
            "classify-table": [
                {
                    "name": "table0",
                    "nbuckets": "2",
                    "memory_size": "1048576",
                    "miss_next": "permit",
                    "mask": "00:00:00:00:00:00:00:00:00:00:ff:ff:ff:ff:00:00"
                }
            ],
            "classify-session": [
                {
                    "policer_hit_next": "policy1",
                    "color_classfier": "exceed-color",
                    "match": "00:00:00:00:00:00:00:00:00:00:c0:a8:01:02:00:00"
                }
            ],
            "interface-policer:policer": {
                "ip4-table": "table0"
            }
        },
        "acl_tables": {
            # settings for policer tables
            "hc_acl_table": {
                "name": "acl_table_test",
                "nbuckets": 1,
                "memory_size": 1048576,
                "skip_n_vectors": 0,
                "miss_next": "permit",
                "mask": "00:00:00:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
            },
            "hc_acl_table2": {
                "name": "acl_table_test2",
                "nbuckets": 2,
                "memory_size": 1048576,
                "skip_n_vectors": 1,
                "next_table": "acl_table_test",
                "miss_next": "deny",
                "mask": "ff:ff:ff:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
            },
            # TODO: remove once memory_size is visible in oper data(HC2VPP-10)
            "hc_acl_table_oper": {
                "name": "acl_table_test",
                "nbuckets": 1,
                "skip_n_vectors": 0,
                "miss_next": "permit",
                "mask": "00:00:00:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
            },
            "hc_acl_table2_oper": {
                "name": "acl_table_test2",
                "nbuckets": 2,
                "skip_n_vectors": 1,
                "next_table": "acl_table_test",
                "miss_next": "deny",
                "mask": "ff:ff:ff:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
            },
            # representation of table settings in VAT
            "table_index": 0,
            "vat_acl_table": {
                "nbuckets": 1,
                "skip": 0,
                "match": 1,
                "nextnode": -1,
                "nexttbl": -1,
                "mask": "000000000000ffffffffffff00000000",
            },
            "table_index2": 1,
            "vat_acl_table2": {
                "nbuckets": 2,
                "skip": 1,
                "match": 1,
                "nextnode": 0,
                "nexttbl": 0,
                "mask": "ffffff000000ffffffffffff00000000",
            },
            # setting for acl sessions
            "hc_acl_session": {
                "match": "00:00:00:00:00:00:01:02:03:04:05:06:00:00:00:00",
                "hit_next": "permit",
                "opaque_index": "1",
                "advance": 1
            },
            "hc_acl_session2": {
                "match": "00:00:00:00:00:00:06:05:04:03:02:01:00:00:00:00",
                "hit_next": "deny",
                "opaque_index": "2",
                "advance": 1
            },
            # representation of session settings in VAT
            "session_index": 0,
            "vat_acl_session": {
                "match": "00000000000001020304050600000000",
                "advance": 1,
                "opaque": 1,
                "next_index": -1
            },
            "session_index2": 1,
            "vat_acl_session2": {
                "match": "00000000000006050403020100000000",
                "advance": 1,
                "opaque": 2,
                "next_index": 0
            }
        }
    }
    return policer_data

