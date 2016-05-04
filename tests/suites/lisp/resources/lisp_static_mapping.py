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

"""Test variables for Lisp remote static mapping test suite."""

#Lisp default value
duts_locator_name = 'ls1'
duts_priority = 1
duts_weight = 1
dut1_vni = 0
dut2_vni = 0

# IPv4 Lisp static mapping configuration
dut1_to_dut2_ip4 = '6.0.3.1'
dut2_to_dut1_ip4 = '6.0.3.2'
dut1_to_tg_ip4 = '6.0.1.1'
dut2_to_tg_ip4 = '6.0.2.1'
tg1_ip4 = '6.0.1.2'
tg2_ip4 = '6.0.2.2'
prefix4 = 24
dut1_eid4 = '6.0.1.0'
dut2_eid4 = '6.0.2.0'
dut1_deid4 = '6.0.2.0'
dut2_deid4 = '6.0.1.0'
dut1_seid4 = '6.0.1.0'
dut2_seid4 = '6.0.2.0'
dut1_rloc4 = '6.0.3.2'
dut2_rloc4 = '6.0.3.1'
eid_prefix4 = 24

# IPv6 Lisp static mapping configuration
dut1_to_dut2_ip6 = '6:0:3::1'
dut2_to_dut1_ip6 = '6:0:3::2'
dut1_to_tg_ip6 = '6:0:1::1'
dut2_to_tg_ip6 = '6:0:2::1'
tg1_ip6 = '6:0:1::2'
tg2_ip6 = '6:0:2::2'
prefix6 = 64
dut1_eid6 = '6:0:1::0'
dut2_eid6 = '6:0:2::0'
dut1_deid6 = '6:0:2::0'
dut2_deid6 = '6:0:1::0'
dut1_seid6 = '6:0:1::0'
dut2_seid6 = '6:0:2::0'
dut1_rloc6 = '6:0:3::2'
dut2_rloc6 = '6:0:3::1'
eid_prefix6 = 64

# IPv4 over IPv6 Lisp static mapping configuration
dut1_to_dut2_ip4o6 = '6:0:3::1'
dut2_to_dut1_ip4o6 = '6:0:3::2'
dut1_to_tg_ip4o6 = '6.0.1.1'
dut2_to_tg_ip4o6 = '6.0.2.1'
tg1_ip4o6 = '6.0.1.2'
tg2_ip4o6 = '6.0.2.2'
tg_prefix4o6 = 24
dut_prefix4o6 = 64
dut1_eid4o6 = '6.0.1.0'
dut2_eid4o6 = '6.0.2.0'
dut1_deid4o6 = '6.0.2.0'
dut2_deid4o6 = '6.0.1.0'
dut1_seid4o6 = '6.0.1.0'
dut2_seid4o6 = '6.0.2.0'
dut1_rloc4o6 = '6:0:3::2'
dut2_rloc4o6 = '6:0:3::1'
eid_prefix4o6 = 24

# IPv6 over IPv4 Lisp static mapping configuration
dut1_to_dut2_ip6o4 = '6.0.3.1'
dut2_to_dut1_ip6o4 = '6.0.3.2'
dut1_to_tg_ip6o4 = '6:0:1::1'
dut2_to_tg_ip6o4 = '6:0:2::1'
tg1_ip6o4 = '6:0:1::2'
tg2_ip6o4 = '6:0:2::2'
tg_prefix6o4 = 64
dut_prefix6o4 = 24
dut1_eid6o4 = '6:0:1::0'
dut2_eid6o4 = '6:0:2::0'
dut1_deid6o4 = '6:0:2::0'
dut2_deid6o4 = '6:0:1::0'
dut1_seid6o4 = '6:0:1::0'
dut2_seid6o4 = '6:0:2::0'
dut1_rloc6o4 = '6.0.3.2'
dut2_rloc6o4 = '6.0.3.1'
eid_prefix6o4 = 64
