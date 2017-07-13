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

from copy import deepcopy

locator_set = "loc01"

remote_bd_subtable = {
    "virtual-network-identifier": 3,
    "bridge-domain-subtable": {
        "bridge-domain-ref": "bd_lisp",
        "remote-mappings": {
            "remote-mapping": [{
                "id": "remote_map_l2",
                "eid": {
                    "virtual-network-id": 3,
                    "address-type": "ietf-lisp-address-types:mac-afi",
                    "mac": "aa:aa:aa:aa:aa:ab",
                },
                "rlocs": {
                    "locator": [{
                        "address": "192.168.0.3",
                        "priority": 1,
                        "weight": 1
                    }]
                },
            }]
        },
    }
}

remote_vrf_subtable = {
    "virtual-network-identifier": 4,
    "vrf-subtable": {
        "table-id": 1,
        "remote-mappings": {
            "remote-mapping": [{
                "id": "remote_map_vrf",
                "eid": {
                    "virtual-network-id": 4,
                    "address-type": "ietf-lisp-address-types:ipv4-afi",
                    "ipv4": "192.168.0.2"
                },
                "rlocs": {
                    "locator": [{
                        "address": "192.168.0.3",
                        "priority": 1,
                        "weight": 1
                    }]
                },

            }]
        },
    }
}

local_bd_subtable = {
    "virtual-network-identifier": 5,
    "bridge-domain-subtable": {
        "bridge-domain-ref": "bd2_lisp",
        "local-mappings": {
            "local-mapping": [{
                "id": "local_map_l2",
                "eid": {
                    "address-type": "ietf-lisp-address-types:mac-afi",
                    "virtual-network-id": 5,
                    "mac": "ba:aa:aa:aa:aa:aa"
                },
                "locator-set": locator_set
            }]
        },
    }
}

local_vrf_subtable = {
    "virtual-network-identifier": 6,
    "vrf-subtable": {
        "table-id": 2,
        "local-mappings": {
            "local-mapping": [{
                "id": "local_map_vrf",
                "eid": {
                    "virtual-network-id": 6,
                    "address-type": "ietf-lisp-address-types:ipv4-afi",
                    "ipv4": "192.168.1.1"
                },
                "locator-set": locator_set
            }]
        },
    }
}

lisp_settings_enable = {
    "lisp": {
        "enable": True
    }
}

prepare_vrf_adjacency = {
    "virtual-network-identifier": 7,
    "vrf-subtable": {
        "table-id": 3,
        "local-mappings": {
            "local-mapping": [{
                "id": "local_map_vrf",
                "eid": {
                    "virtual-network-id": 7,
                    "address-type": "ietf-lisp-address-types:ipv4-afi",
                    "ipv4": "192.168.1.1"
                },
                "locator-set": locator_set
            }]
        },
        "remote-mappings": {
            "remote-mapping": [{
                "id": "remote_map_vrf",
                "eid": {
                    "virtual-network-id": 7,
                    "address-type": "ietf-lisp-address-types:ipv4-afi",
                    "ipv4": "192.168.0.2"
                },
                "rlocs": {
                    "locator": [{
                        "address": "192.168.0.3",
                        "priority": 1,
                        "weight": 1
                    }]
                },

            }]
        },
    }
}

vrf_adjacency = {
                    "adjacency": [{
                        "id": "adj01",
                        "local-eid": {
                            "virtual-network-id": 7,
                            "address-type": "ietf-lisp-address-types:ipv4-afi",
                            "ipv4": "192.168.1.1"
                        },
                        "remote-eid": {
                            "virtual-network-id": 7,
                            "address-type": "ietf-lisp-address-types:ipv4-afi",
                            "ipv4": "192.168.0.2"
                        },
                    }]
                }

adj_subtable = deepcopy(prepare_vrf_adjacency)
adj_subtable["vrf-subtable"]["remote-mappings"]\
    ["remote-mapping"][0]["adjacencies"] = deepcopy(vrf_adjacency)


def create_settings_dict(subtable):
    settings = {
        "eid-table": {
            "vni-table": [subtable]
        }
    }

    return settings

lisp_settings_remote_bd = create_settings_dict(remote_bd_subtable)
lisp_settings_remote_vrf = create_settings_dict(remote_vrf_subtable)
lisp_settings_local_bd = create_settings_dict(local_bd_subtable)
lisp_settings_local_vrf = create_settings_dict(local_vrf_subtable)
lisp_settings_both_vrf = create_settings_dict(prepare_vrf_adjacency)

vat_remote_bd = {
    "is_local": 0,
    "vni": remote_bd_subtable["virtual-network-identifier"],
    "eid": remote_bd_subtable["bridge-domain-subtable"]["remote-mappings"][
        "remote-mapping"][0]["eid"]["mac"],
}

vat_remote_vrf = {
    "is_local": 0,
    "vni": remote_vrf_subtable["virtual-network-identifier"],
    "eid": remote_vrf_subtable["vrf-subtable"]["remote-mappings"][
        "remote-mapping"][0]["eid"]["ipv4"]+"/32",
}

vat_local_bd = {
    "is_local": 1,
    "vni": local_bd_subtable["virtual-network-identifier"],
    "eid": local_bd_subtable["bridge-domain-subtable"]["local-mappings"][
        "local-mapping"][0]["eid"]["mac"]
}

vat_local_vrf = {
    "is_local": 1,
    "vni": local_vrf_subtable["virtual-network-identifier"],
    "eid": local_vrf_subtable["vrf-subtable"]["local-mappings"][
        "local-mapping"][0]["eid"]["ipv4"]+"/32"
}

# variables for traffic test
dut_to_tg_if1_ip4 = "192.168.0.1"
dut_to_tg_if2_ip4 = "192.168.1.1"
tg_to_dut_if2_ip4 = "192.168.1.2"
src_ip4 = "192.168.0.2"
dst_ip4 = "192.168.2.2"
prefix_len4 = 24

local_eid4 = "192.168.0.0/24"
remote_eid4 = "192.168.2.0/24"
src_rloc4 = dut_to_tg_if2_ip4
dst_rloc4 = tg_to_dut_if2_ip4

lisp_traffic_table_ip4 = {
    "virtual-network-identifier": 0,
    "vrf-subtable": {
        "table-id": 1,
        "local-mappings": {
            "local-mapping": [{
                "id": "local_map_vrf",
                "eid": {
                    "virtual-network-id": 0,
                    "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
                    "ipv4-prefix": local_eid4
                },
                "locator-set": locator_set
            }]
        },
        "remote-mappings": {
            "remote-mapping": [{
                "id": "remote_map_vrf",
                "eid": {
                    "virtual-network-id": 0,
                    "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
                    "ipv4-prefix": remote_eid4
                },
                "rlocs": {
                    "locator": [{
                        "address": tg_to_dut_if2_ip4,
                        "priority": 1,
                        "weight": 1
                    }]
                },
                "adjacencies": {
                    "adjacency": [{
                        "id": "adj01",
                        "local-eid": {
                            "virtual-network-id": 0,
                            "address-type":
                                "ietf-lisp-address-types:ipv4-prefix-afi",
                            "ipv4-prefix": local_eid4
                        },
                        "remote-eid": {
                            "virtual-network-id": 0,
                            "address-type":
                                "ietf-lisp-address-types:ipv4-prefix-afi",
                            "ipv4-prefix": remote_eid4
                        },
                    }]
                }
            }]
        },
    }
}

dut_to_tg_if1_ip6 = "10::1"
dut_to_tg_if2_ip6 = "11::1"
tg_to_dut_if2_ip6 = "11::2"
src_ip6 = "10::2"
dst_ip6 = "12::2"
prefix_len6 = 64

local_eid6 = "10::/64"
remote_eid6 = "12::/64"
src_rloc6 = dut_to_tg_if2_ip6
dst_rloc6 = tg_to_dut_if2_ip6

lisp_traffic_table_ip6 = {
    "virtual-network-identifier": 0,
    "vrf-subtable": {
        "table-id": 1,
        "local-mappings": {
            "local-mapping": [{
                "id": "local_map_vrf",
                "eid": {
                    "virtual-network-id": 0,
                    "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
                    "ipv6-prefix": local_eid6
                },
                "locator-set": locator_set
            }]
        },
        "remote-mappings": {
            "remote-mapping": [{
                "id": "remote_map_vrf",
                "eid": {
                    "virtual-network-id": 0,
                    "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
                    "ipv6-prefix": remote_eid6
                },
                "rlocs": {
                    "locator": [{
                        "address": tg_to_dut_if2_ip6,
                        "priority": 1,
                        "weight": 1
                    }]
                },
                "adjacencies": {
                    "adjacency": [{
                        "id": "adj01",
                        "local-eid": {
                            "virtual-network-id": 0,
                            "address-type":
                                "ietf-lisp-address-types:ipv6-prefix-afi",
                            "ipv6-prefix": local_eid6
                        },
                        "remote-eid": {
                            "virtual-network-id": 0,
                            "address-type":
                                "ietf-lisp-address-types:ipv6-prefix-afi",
                            "ipv6-prefix": remote_eid6
                        },
                    }]
                }
            }]
        },
    }
}

lisp_traffic_ip4 = create_settings_dict(lisp_traffic_table_ip4)
lisp_traffic_ip6 = create_settings_dict(lisp_traffic_table_ip6)
