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

"""Test variables for DHCP relay test suite."""

# IPv4 addresses used in traffic tests
dut_to_tg_if1_ip = "172.16.0.1"
dut_to_tg_if2_ip = "192.168.0.1"
dhcp_server1_ip = "192.168.0.100"
dhcp_server2_ip = "192.168.0.101"
client_ip = "172.16.0.2"
prefix_length = 24

# IPv6 addresses used in traffic tests
dut_to_tg_if1_ip6 = "3ffe:62::1"
dut_to_tg_if2_ip6 = "3ffe:63::1"
dhcp_server_ip6 = "3ffe:63::2"
client_ip6 = "3ffe:62::2"
prefix_length_v6 = 64

# DHCP relay configuration
relay1 = {
    "relay": [
        {
            "address-type": "ipv4",
            "rx-vrf-id": 0,
            "gateway-address": dut_to_tg_if1_ip,
            "server": [
                {
                    "vrf-id": 0,
                    "address": dhcp_server1_ip
                },
            ]
        }
    ]
}

relay1_oper = {
    "address-type": "dhcp:ipv4",
    "rx-vrf-id": 0,
    "gateway-address": dut_to_tg_if1_ip,
    "server": [
        {
            "vrf-id": 0,
            "address": dhcp_server1_ip
        }
    ]
}

relay2 = {
    "relay": [
        {
            "address-type": "ipv4",
            "rx-vrf-id": 0,
            "gateway-address": dut_to_tg_if1_ip,
            "server": [
                {
                    "vrf-id": 0,
                    "address": dhcp_server1_ip
                },
                {
                    "vrf-id": 0,
                    "address": dhcp_server2_ip
                },
            ]
        }
    ]
}

relay2_oper = {
    "address-type": "dhcp:ipv4",
    "rx-vrf-id": 0,
    "gateway-address": dut_to_tg_if1_ip,
    "server": [
        {
            "vrf-id": 0,
            "address": dhcp_server1_ip
        },
        {
            "vrf-id": 0,
            "address": dhcp_server2_ip
        }
    ]
}

relay_v6 = {
    "relay": [
        {
            "address-type": "ipv6",
            "rx-vrf-id": 0,
            "gateway-address": dut_to_tg_if1_ip6,
            "server": [
                {
                    "vrf-id": 0,
                    "address": dhcp_server_ip6
                },
            ]
        }
    ]
}

relay_v6_oper = {
    "address-type": "dhcp:ipv6",
    "rx-vrf-id": 0,
    "gateway-address": dut_to_tg_if1_ip6,
    "server": [
        {
            "vrf-id": 0,
            "address": dhcp_server_ip6
        }
    ]
}
