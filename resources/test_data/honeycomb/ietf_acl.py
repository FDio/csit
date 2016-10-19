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

"""Test variables for ietf-ACL test suite."""


def get_variables(test_case, name):
    """Create and return a dictionary of test variables for the specified
    test case.

    :param test_case: Determines which test variables to return.
    :param name: Name for the classify chain used in test.
    :type test_case: str
    :type name: str

    :return: Dictionary of test variables - settings for Honeycomb's
    ietf-acl node and packet fields to use in verification.
    :rtype: dict
    """

    test_case = test_case.lower()
    variables = {
        # Variables for control packet, should always pass through DUT
        "src_ip": "16.0.0.1",
        "dst_ip": "16.0.1.1",
        "dst_net": "16.0.1.0",
        "src_port": "1234",
        "dst_port": "1234",
        "src_mac": "01:02:03:04:05:06",
        "dst_mac": "10:20:30:40:50:60"}

    test_vars = {
        "l2": {
            # MACs classified directly
            "classify_src": "12:23:34:45:56:67",
            "classify_dst": "89:9A:AB:BC:CD:DE",
            # MACs classified through mask
            "classify_src2": "01:02:03:04:56:67",
            "classify_dst2": "89:9A:AB:BC:50:60",
            "src_mask": "00:00:00:00:FF:FF",
            "dst_mask": "FF:FF:FF:FF:00:00"
        },
        "l3_ip4": {
            # IPs for DUT interface setup
            "dut_to_tg_if1_ip": "16.0.0.2",
            "dut_to_tg_if2_ip": "192.168.0.2",
            "prefix_length": 24,
            "gateway": "192.168.0.1",
            # classified networks
            "classify_src_net": "16.0.2.0",
            "classify_dst_net": "16.0.3.0",
            # IPs in classified networks
            "classify_src": "16.0.2.1",
            "classify_dst": "16.0.3.1",
        },
        "l3_ip6": {
            # Override control packet addresses with IPv6
            "src_ip": "10::1",
            "dst_ip": "11::1",
            "dst_net": "11::",
            # IPs for DUT interface setup
            "dut_to_tg_if1_ip": "10::2",
            "dut_to_tg_if2_ip": "20::2",
            "prefix_length": 64,
            "gateway": "20::1",
            # classified networks
            "classify_src_net": "12::",
            "classify_dst_net": "13::",
            # IPs in classified networks
            "classify_src": "12::1",
            "classify_dst": "13::1",
        },
        "l4": {
            # IPs for DUT interface and route setup
            "dut_to_tg_if1_ip": "16.0.0.2",
            "dut_to_tg_if2_ip": "192.168.0.2",
            "prefix_length": 24,
            "gateway": "192.168.0.1",
            "classify_dst_net": "16.0.3.0",
            # Ports in classified ranges
            "classify_src": 1500,
            "classify_dst": 2000,
        },
        "mixed": {
            # IPs for DUT interface setup
            "dut_to_tg_if1_ip": "16.0.0.2",
            "dut_to_tg_if2_ip": "192.168.0.2",
            "gateway": "192.168.0.1",
            # classified networks
            "classify_src_net": "16.0.2.0",
            "classify_dst_net": "16.0.3.0",
            # IPs in classified networks
            "classify_src_ip": "16.0.2.1",
            "classify_dst_ip": "16.0.3.1",
            "prefix_length": 24,
            # MACs classified through mask
            "classify_src_mac": "01:02:03:04:56:67",
            "classify_dst_mac": "89:9A:AB:BC:50:60",
            "src_mask": "00:00:00:00:FF:FF",
            "dst_mask": "FF:FF:FF:FF:00:00",
            # classified ports
            "classify_src_port": 1500,
            "classify_dst_port": 2000,
        },
        "multirule": {
            # MACs classified by first rule
            "classify_src": "12:23:34:45:56:67",
            "classify_dst": "89:9A:AB:BC:CD:DE",
            # MACs classified by second rule
            "classify_src2": "01:02:03:04:56:67",
            "classify_dst2": "89:9A:AB:BC:50:60",
            # MAC rule masks -  only match specific addresses
            "src_mask": "FF:FF:FF:FF:FF:FF",
            "dst_mask": "FF:FF:FF:FF:FF:FF",
        }
    }
    acl_data = {
        # ACL configuration for L2 tests
        "l2": {
            "acl": [{
                "acl-type":
                    "ietf-access-control-list:eth-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "source-mac-address":
                            test_vars["l2"]["classify_src"],
                        "source-mac-address-mask":
                            test_vars["l2"]["src_mask"],
                        "destination-mac-address":
                            test_vars["l2"]["classify_dst"],
                        "destination-mac-address-mask":
                            test_vars["l2"]["dst_mask"]
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        },
        # ACL configuration for L3 IPv4 tests
        "l3_ip4": {
            "acl": [{
                "acl-type":
                    "ietf-access-control-list:ipv4-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "source-ipv4-network":
                            "{0}/{1}".format(
                                test_vars["l3_ip4"]["classify_src_net"],
                                test_vars["l3_ip4"]["prefix_length"]),
                        "destination-ipv4-network":
                            "{0}/{1}".format(
                                test_vars["l3_ip4"]["classify_dst_net"],
                                test_vars["l3_ip4"]["prefix_length"]),
                        "protocol": 17
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        },
        # ACL settings for L3 IPv6 tests
        "l3_ip6": {
            "acl": [{
                "acl-type":
                    "ietf-access-control-list:ipv6-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "source-ipv6-network":
                            "{0}/{1}".format(
                                test_vars["l3_ip6"]["classify_src_net"],
                                test_vars["l3_ip6"]["prefix_length"]),
                        "destination-ipv6-network":
                            "{0}/{1}".format(
                                test_vars["l3_ip6"]["classify_dst_net"],
                                test_vars["l3_ip6"]["prefix_length"]),
                        "protocol": 17
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        },
        # ACL configuration for L4 tests
        "l4": {
            "acl": [{
                "acl-type":
                    "vpp-acl:mixed-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "destination-ipv4-network": "0.0.0.0/0",
                        "destination-port-range": {
                            "lower-port": test_vars["l4"]["classify_dst"],
                            "upper-port": test_vars["l4"]["classify_dst"] + 50
                        },
                        "source-port-range": {
                            "lower-port": test_vars["l4"]["classify_src"],
                            "upper-port": test_vars["l4"]["classify_src"] + 50
                        }
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        },
        "mixed": {
            "acl": [{
                "acl-type":
                    "vpp-acl:mixed-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "vpp-acl:source-mac-address":
                            test_vars["mixed"]["classify_src_mac"],
                        "vpp-acl:source-mac-address-mask":
                            test_vars["mixed"]["src_mask"],
                        "vpp-acl:destination-mac-address":
                            test_vars["mixed"]["classify_dst_mac"],
                        "vpp-acl:destination-mac-address-mask":
                            test_vars["mixed"]["dst_mask"],
                        "vpp-acl:source-ipv4-network":
                            "{0}/{1}".format(
                                test_vars["mixed"]["classify_src_net"],
                                test_vars["mixed"]["prefix_length"]),
                        "vpp-acl:destination-ipv4-network":
                            "{0}/{1}".format(
                                test_vars["mixed"]["classify_dst_net"],
                                test_vars["mixed"]["prefix_length"]),
                        "vpp-acl:protocol": 17,
                        "vpp-acl:destination-port-range": {
                            "lower-port": test_vars["l4"]["classify_dst"],
                            "upper-port": test_vars["l4"]["classify_dst"] + 50
                        },
                        "vpp-acl:source-port-range": {
                            "lower-port": test_vars["l4"]["classify_src"],
                            "upper-port": test_vars["l4"]["classify_src"] + 50
                        }
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        },
        "multirule": {
            "acl": [{
                "acl-type":
                    "ietf-access-control-list:eth-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [
                    {
                        "rule-name": "rule1",
                        "matches": {
                            "source-mac-address":
                                test_vars["multirule"]["classify_src"],
                            "source-mac-address-mask":
                                test_vars["multirule"]["src_mask"],
                            "destination-mac-address":
                                test_vars["multirule"]["classify_dst"],
                            "destination-mac-address-mask":
                                test_vars["multirule"]["dst_mask"]
                        },
                        "actions": {
                            "deny": {}
                        }
                    },
                    {
                        "rule-name": "rule2",
                        "matches": {
                            "source-mac-address":
                                test_vars["multirule"]["classify_src2"],
                            "source-mac-address-mask":
                                test_vars["multirule"]["src_mask"],
                            "destination-mac-address":
                                test_vars["multirule"]["classify_dst2"],
                            "destination-mac-address-mask":
                                test_vars["multirule"]["dst_mask"]
                        },
                        "actions": {
                            "deny": {}
                        }
                    },
                    {
                        "rule-name": "rule3",
                        "matches": {
                            "source-mac-address":
                                variables["src_mac"],
                            "source-mac-address-mask":
                                test_vars["multirule"]["src_mask"],
                            "destination-mac-address":
                                variables["dst_mac"],
                            "destination-mac-address-mask":
                                test_vars["multirule"]["dst_mask"]
                        },
                        "actions": {
                            "permit": {}
                        }
                    }
                ]}
            }]
        }
    }
    try:
        ret_vars = {}
        ret_vars.update(variables)
        ret_vars.update(test_vars[test_case])
        ret_vars.update(
            {"acl_settings": acl_data[test_case]}
        )
    except KeyError:
        raise Exception("Unrecognized test case {0}."
                        " Valid options are: {1}".format(
                            test_case, acl_data.keys()))
    return ret_vars
