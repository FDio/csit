# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Test variables for Lisp remote static mapping test suite."""

# Lisp default global value
locator_name = u"ls1"

# Lisp default locator_set value
duts_locator_set = {
    u"locator_name": locator_name,
    u"priority": 1,
    u"weight": 1
}

# IPv4 Lisp static mapping configuration
dut1_to_dut2_ip4 = u"1.1.1.1"
dut2_to_dut1_ip4 = u"1.1.1.2"
dut1_to_tg_ip4 = u"10.10.10.1"
dut2_to_tg_ip4 = u"20.20.20.1"
prefix4 = 24
dut1_ip4_static_adjacency = {
    u"vni": 0,
    u"deid": u"20.20.20.0",
    u"seid": u"10.10.10.0",
    u"rloc": u"1.1.1.2",
    u"prefix": 24
}
dut2_ip4_static_adjacency = {
    u"vni": 0,
    u"deid": u"10.10.10.0",
    u"seid": u"20.20.20.0",
    u"rloc": u"1.1.1.1",
    u"prefix": 24
}
dut1_ip4_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"10.10.10.0",
    u"prefix": 24
}
dut2_ip4_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"20.20.20.0",
    u"prefix": 24
}

# IPv6 Lisp static mapping configuration
dut1_to_dut2_ip6 = u"2001:3::1"
dut2_to_dut1_ip6 = u"2001:3::2"
dut1_to_tg_ip6 = u"2001:1::1"
dut2_to_tg_ip6 = u"2001:2::1"
prefix6 = 64
dut1_ip6_static_adjacency = {
    u"vni": 0,
    u"deid": u"2001:2::0",
    u"seid": u"2001:1::0",
    u"rloc": u"2001:3::2",
    u"prefix": 64
}
dut2_ip6_static_adjacency = {
    u"vni": 0,
    u"deid": u"2001:1::0",
    u"seid": u"2001:2::0",
    u"rloc": u"2001:3::1",
    u"prefix": 64
}
dut1_ip6_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"2001:1::0",
    u"prefix": 64
}
dut2_ip6_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"2001:2::0",
    u"prefix": 64
}

# IPv4 over IPv6 Lisp static mapping configuration
dut1_to_dut2_ip4o6 = u"2001:3::1"
dut2_to_dut1_ip4o6 = u"2001:3::2"
dut1_to_tg_ip4o6 = u"10.10.10.1"
dut2_to_tg_ip4o6 = u"20.20.20.1"
tg_prefix4o6 = 24
dut_prefix4o6 = 64
dut1_ip4o6_static_adjacency = {
    u"vni": 0,
    u"deid": u"20.20.20.0",
    u"seid": u"10.10.10.0",
    u"rloc": u"2001:3::2",
    u"prefix": 24
}
dut2_ip4o6_static_adjacency = {
    u"vni": 0,
    u"deid": u"10.10.10.0",
    u"seid": u"20.20.20.0",
    u"rloc": u"2001:3::1",
    u"prefix": 24
}
dut1_ip4o6_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"10.10.10.0",
    u"prefix": 24
}
dut2_ip4o6_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"20.20.20.0",
    u"prefix": 24
}

# IPv6 over IPv4 Lisp static mapping configuration
dut1_to_dut2_ip6o4 = u"1.1.1.1"
dut2_to_dut1_ip6o4 = u"1.1.1.2"
dut1_to_tg_ip6o4 = u"2001:1::1"
dut2_to_tg_ip6o4 = u"2001:2::1"
tg_prefix6o4 = 64
dut_prefix6o4 = 24
dut1_ip6o4_static_adjacency = {
    u"vni": 0,
    u"deid": u"2001:2::0",
    u"seid": u"2001:1::0",
    u"rloc": u"1.1.1.2",
    u"prefix": 64
}
dut2_ip6o4_static_adjacency = {
    u"vni": 0,
    u"deid": u"2001:1::0",
    u"seid": u"2001:2::0",
    u"rloc": u"1.1.1.1",
    u"prefix": 64
}
dut1_ip6o4_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"2001:1::0",
    u"prefix": 64
}
dut2_ip6o4_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"2001:2::0",
    u"prefix": 64
}
