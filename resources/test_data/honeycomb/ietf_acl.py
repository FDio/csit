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
    """Return dictionary of test variables."""

    variables = {
        # generic packet data
        "src_ip": "16.0.0.1",
        "dst_ip": "16.0.1.1",
        "dst_net": "16.0.1.0",
        "src_port": "1234",
        "dst_port": "1234",
        "src_mac": "01:02:03:04:05:06",
        "dst_mac": "10:20:30:40:50:60"}

    if test_case.lower() == "l2":
        classify_vars = {
            "classify_src": "12:23:34:45:56:67",
            "classify_dst": "89:9A:AB:BC:CD:DE",
            "classify_src2": "01:02:03:04:56:67",
            "classify_dst2": "89:9A:AB:BC:50:60",
            "src_mask": "00:00:00:00:FF:FF",
            "dst_mask": "FF:FF:FF:FF:00:00",
            }

        acl_settings = {
            "acl": [{
                "acl-type":
                    "ietf-access-control-list:eth-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "source-mac-address":
                            classify_vars["classify_src"],
                        "source-mac-address-mask":
                            classify_vars["src_mask"],
                        "destination-mac-address":
                            classify_vars["classify_dst"],
                        "destination-mac-address-mask":
                            classify_vars["dst_mask"]
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        }

    elif test_case.lower() == "l3_ip4":
        classify_vars = {
            "classify_src_net": "16.0.2.0",
            "classify_dst_net": "16.0.3.0",
            "classify_src": "16.0.2.1",
            "classify_dst": "16.0.3.1",
            "prefix_length": 24,
            "dut_to_tg_if1_ip": "16.0.0.2",
            "dut_to_tg_if2_ip": "192.168.0.2",
            "gateway": "192.168.0.1"
        }

        acl_settings = {
            "acl": [{
                "acl-type":
                    "ietf-access-control-list:ipv4-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "source-ipv4-network":
                            "{0}/{1}".format(classify_vars["classify_src_net"],
                                             classify_vars["prefix_length"]
                                             ),
                        "destination-ipv4-network":
                            "{0}/{1}".format(classify_vars["classify_dst_net"],
                                             classify_vars["prefix_length"]
                                             ),
                        "protocol": 17
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        }

    elif test_case.lower() == "l3_ip6":
        classify_vars = {
            "classify_src_net": "12::",
            "classify_dst_net": "13::",
            "classify_src": "12::1",
            "classify_dst": "13::1",
            "prefix_length": 64,
            "dut_to_tg_if1_ip": "10::2",
            "dut_to_tg_if2_ip": "20::2",
            "gateway": "20::1",
            # Override IPv4 addresses
            "src_ip": "10::1",
            "dst_ip": "11::1",
            "dst_net": "11::"
        }

        acl_settings = {
            "acl": [{
                "acl-type":
                    "ietf-access-control-list:ipv6-acl",
                "acl-name": name,
                "access-list-entries": {"ace": [{
                    "rule-name": "rule1",
                    "matches": {
                        "source-ipv6-network":
                            "{0}/{1}".format(classify_vars["classify_src_net"],
                                             classify_vars["prefix_length"]
                                             ),
                        "destination-ipv6-network":
                            "{0}/{1}".format(classify_vars["classify_dst_net"],
                                             classify_vars["prefix_length"]
                                             ),
                        "protocol": 17
                    },
                    "actions": {
                        "deny": {}
                    }
                }]}
            }]
        }
    else:
        raise Exception("Unrecognized test case {0}".format(test_case))

    variables.update(classify_vars)
    variables["acl_settings"] = acl_settings
    return variables
