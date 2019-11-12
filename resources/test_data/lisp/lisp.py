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

"""Test variables of lisp and lispgpe (ip4/ip6) encapsulation test suite."""

# Lisp default global value
locator_name = u"tst_locator"

# Test configuration data
tg_if1_ip4= u"6.0.0.2"
tg_if2_ip4= u"6.0.1.2"
dut_if1_ip4= u"6.0.0.1"
dut_if2_ip4= u"6.0.1.1"
tg_if2_ip6= u"6:0:1::2"
dut_if2_ip6= u"6:0:1::1"
ip4_plen= 24
src_ip4= u"6.0.0.2"
dst_ip4= u"6.0.2.2"
src_rloc4= dut_if2_ip4
dst_rloc4= tg_if2_ip4
src_rloc6= dut_if2_ip6
dst_rloc6= tg_if2_ip6

#IP6 over IP4 LISP configuration data
tg_if1_ip6= u"6::2"
dut_if1_ip6= u"6:0:0::1"
src_ip6= u"6::2"
dst_ip6= u"6:0:2::2"
ip6_plen=64

# Lisp default locator_set value
duts_locator_set = {
    u"locator_name": locator_name,
    u"priority": 1,
    u"weight": 1
}

# IPv4 Lisp static mapping configuration

dut1_to_tg_ip4_static_adjacency = {
    u"vni": 0,
    u"deid": u"6.0.2.0",
    u"seid": u"6.0.0.0",
    u"rloc": u"6.0.1.2",
    u"prefix": 24
}

dut1_ip4_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"6.0.0.0",
    u"prefix": 24
}

# IPv6 Lisp static mapping configuration

dut1_to_tg_ip6_static_adjacency = {
    u"vni": 0,
    u"deid": u"6:0:2::0",
    u"seid": u"6:0:0::0",
    u"rloc": u"6:0:1::2",
    u"prefix": 64
}

dut1_ip6_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"6:0:0::0",
    u"prefix": 64
}


#IPv6 over IPv4 LISP mapping
dut1_ip6o4_static_adjacency = {
    u"vni": 0,
    u"deid": u"6:0:2::0",
    u"seid": u"6:0:0::0",
    u"rloc": u"6.0.1.2",
    u"prefix": 64
}
dut1_ip6o4_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"6:0:0::0",
    u"prefix": 64
}

#IPv4 over IPv6 LISP mapping
dut1_ip4o6_static_adjacency = {
    u"vni": 0,
    u"deid": u"6.0.2.0",
    u"seid": u"6.0.0.0",
    u"rloc": u"6:0:1::2",
    u"prefix": 24
}
dut1_ip4o6_eid = {
    u"locator_name": locator_name,
    u"vni": 0,
    u"eid": u"6.0.0.0",
    u"prefix": 24
}
