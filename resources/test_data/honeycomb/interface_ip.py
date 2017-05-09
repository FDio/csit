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

"""Test variables for Basic interface management and IP addresses."""

# Configuration which will be set and verified during tests.
ipv4_address = "192.168.0.2"
ipv4_address2 = "192.168.1.2"
ipv4_prefix = 24
ipv4_mask = "255.255.255.0"
ipv4_neighbor = "192.168.0.4"
ipv4_neighbor2 = "192.168.1.4"
ipv4_settings = {"mtu": 9000}
ipv6_address = "10::10"
ipv6_address2 = "11::10"
ipv6_prefix = 64
ipv6_neighbor = "10::11"
ipv6_neighbor2 = "11::11"
neighbor_mac = "08:00:27:c0:5d:37"
neighbor_mac2 = "08:00:27:c0:5d:37"
ipv6_settings = {"enabled": True, "forwarding": True, "mtu": 9000,
                 "dup-addr-detect-transmits": 5}
ethernet = {"mtu": 9000}
routing = {"vrf-id": 27}
