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

"""Test data for Honeycomb routing test."""

from resources.libraries.python.topology import Topology


def get_variables(node, ip_version, out_interface):

    out_interface = Topology.convert_interface_reference(
        node, out_interface, "name")

    ip_version = ip_version.lower()
    variables = {}

    # base network settings
    ipv4_base = {
        "dut_to_tg_if1_ip": "16.0.0.1",
        "dut_to_tg_if2_ip": "16.0.1.1",
        "src_ip": "16.0.0.2",
        "dst_ip": "16.0.2.1",
        "dst_net": "16.0.2.0",
        "prefix_len": 24,
        "next_hop": "16.0.1.2",
        "next_hop1": "16.0.1.3",
        "next_hop2": "16.0.1.4",
        "next_hop_mac1": "00:11:22:33:44:55",
        "next_hop_mac2": "11:22:33:44:55:66"
    }

    ipv6_base = {
        "dut_to_tg_if1_ip": "10::1",
        "dut_to_tg_if2_ip": "11::1",
        "src_ip": "10::2",
        "dst_ip": "12::1",
        "dst_net": "12::",
        "prefix_len": 64,
        "next_hop": "11::2",
        "next_hop1": "11::3",
        "next_hop2": "11::4",
        "next_hop_mac1": "00:11:22:33:44:55",
        "next_hop_mac2": "11:22:33:44:55:66"
    }

    if ip_version == "ipv4":
        variables.update(ipv4_base)
    elif ip_version == "ipv6":
        variables.update(ipv6_base)
    else:
        raise ValueError("IP version must be either IPv4 or IPv6.")

    # route configuration used in tests
    tables_cfg = {
        "table1": {
            "description": "single hop ipv4",
            "destination-prefix":
                "{0}/{1}".format(ipv4_base["dst_net"], ipv4_base["prefix_len"]),
            "next-hop": {
                "next-hop-address" : ipv4_base["next_hop"],
                "outgoing-interface": out_interface
            },
            "vpp-ipv4-unicast-routing:vpp-ipv4-route": {}
        },
        "table2": {
            "description": "multi hop ipv4",
            "destination-prefix":
                "{0}/{1}".format(ipv4_base["dst_net"], ipv4_base["prefix_len"]),
            "next-hop":{
                "next-hop-list": {
                    "next-hop": [
                        {
                            "index": 1,
                            "next-hop-address": ipv4_base["next_hop1"],
                            "outgoing-interface": out_interface,
                            "weight": "1"
                        },
                        {
                            "index": 2,
                            "next-hop-address": ipv4_base["next_hop2"],
                            "outgoing-interface": out_interface,
                            "weight": "1"
                        }
                    ]
                }
            }
        },
        "table3": {
            "description": "blackhole ipv4",
            "destination-prefix":
                "{0}/{1}".format(ipv4_base["dst_net"], ipv4_base["prefix_len"]),
            "next-hop": {
                "special-next-hop-enum": "blackhole"
            }
        },
        "table4": {
            "description": "single hop ipv6",
            "destination-prefix":
                "{0}/{1}".format(ipv6_base["dst_net"], ipv6_base["prefix_len"]),
            "next-hop": {
                "next-hop-address": ipv6_base["next_hop"],
                "outgoing-interface": out_interface
            },
            "vpp-ipv6-unicast-routing:vpp-ipv6-route": {}
        },
        "table5": {
            "description": "multi hop ipv6",
            "destination-prefix":
                "{0}/{1}".format(ipv6_base["dst_net"], ipv6_base["prefix_len"]),
            "next-hop":{
                "next-hop-list": {
                    "next-hop": [
                        {
                            "index": 1,
                            "next-hop-address": ipv6_base["next_hop1"],
                            "outgoing-interface": out_interface,
                            "weight": "1"
                        },
                        {
                            "index": 2,
                            "next-hop-address": ipv6_base["next_hop2"],
                            "outgoing-interface": out_interface,
                            "weight": "1"
                        }
                    ]
                }
            }
        },
        "table6": {
            "description": "blackhole ipv6",
            "destination-prefix":
                "{0}/{1}".format(ipv6_base["dst_net"], ipv6_base["prefix_len"]),
            "next-hop":{
                "special-next-hop-enum": "blackhole"
            }
        }
    }

    # expected route operational data
    tables_oper = {
        "table1_oper": {
            "destination-prefix":
                "{0}/{1}".format(ipv4_base["dst_net"], ipv4_base["prefix_len"]),
            "next-hop":{
                "next-hop-address": ipv4_base["next_hop"],
                "outgoing-interface": out_interface
            },
            "vpp-ipv4-unicast-routing:vpp-ipv4-route": {"classify-table": "classify-table-1"}
        },
        "table2_oper": {
            "destination-prefix":
                "{0}/{1}".format(ipv4_base["dst_net"], ipv4_base["prefix_len"]),
            "next-hop":{
                "next-hop-list": {
                    "next-hop": [
                        {
                            "index": 1,
                            "next-hop-address": ipv4_base["next_hop1"],
                            "outgoing-interface": out_interface,
                            "vpp-ipv4-unicast-routing:weight": 1
                        },
                        {
                            "index": 2,
                            "next-hop-address": ipv4_base["next_hop2"],
                            "outgoing-interface": out_interface,
                            "vpp-ipv4-unicast-routing:weight": 1
                        }
                    ]
                }
            },
            "vpp-ipv4-unicast-routing:vpp-ipv4-route": {"classify-table": "classify-table-1"}
        },
        "table3_oper": {
            "destination-prefix":
                "{0}/{1}".format(ipv4_base["dst_net"], ipv4_base["prefix_len"]),
            "next-hop":{
                "special-next-hop-enum": "blackhole"
            },
            "vpp-ipv4-unicast-routing:vpp-ipv4-route": {"classify-table": "classify-table-1"}
        },
        "table4_oper": {
            "destination-prefix":
                "{0}/{1}".format(ipv6_base["dst_net"],
                                 ipv6_base["prefix_len"]),
            "next-hop":{
                "next-hop-address": ipv6_base["next_hop"],
                "outgoing-interface": out_interface
            },
            "vpp-ipv6-unicast-routing:vpp-ipv6-route": {"classify-table": "classify-table-1"}
        },
        "table5_oper": {
            "destination-prefix":
                "{0}/{1}".format(ipv6_base["dst_net"],
                                 ipv6_base["prefix_len"]),
            "next-hop":{
                "next-hop-list": {
                    "next-hop": [
                        {
                            "next-hop-address": ipv6_base["next_hop1"],
                            "outgoing-interface": out_interface,
                            "vpp-ipv6-unicast-routing:weight": 1
                        },
                        {
                            "next-hop-address": ipv6_base["next_hop2"],
                            "outgoing-interface": out_interface,
                            "vpp-ipv6-unicast-routing:weight": 1
                        }
                    ]
                }
            },
            "vpp-ipv6-unicast-routing:vpp-ipv6-route": {"classify-table": "classify-table-1"}
        },
        "table6_oper": {
            "destination-prefix":
                "{0}/{1}".format(ipv6_base["dst_net"],
                                 ipv6_base["prefix_len"]),
            "next-hop":{
                "special-next-hop-enum": "blackhole"
            },
            "vpp-ipv6-unicast-routing:vpp-ipv6-route": {"classify-table": "classify-table-1"}
        }
    }

    for item in tables_oper.values():
        if "next-hop-list" in item.keys():
            item["next-hop-list"]["next-hop"].sort()

    variables.update(tables_cfg)
    variables.update(tables_oper)
    return variables
