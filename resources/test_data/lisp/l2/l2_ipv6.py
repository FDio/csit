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

"""Test variables for ip4-lispgpe-ip4 encapsulation test suite."""

# Lisp default global value
locator_name = 'tst_locator'

# Lisp default locator_set value
lisp_dut_settings = {'locator_name': locator_name,
                     'priority': 1,
                     'weight': 1,
                     'bd': 10,
                     'vni': 5}

# IPv4 Lisp static mapping configuration
dut1_to_dut2_ip6 = '2001:cdba:3::1'
dut2_to_dut1_ip6 = '2001:cdba:3::2'
dut1_to_tg_ip6 = '2001:cdba:1::1'
dut2_to_tg_ip6 = '2001:cdba:2::1'
tg1_ip6 = '2001:cdba:1::2'
tg2_ip6 = '2001:cdba:2::2'
prefix6 = 64
vpp_bd_id = 10
tg_if1_mac = '08:22:22:22:22:11'
tg_if2_mac = '08:22:22:22:22:22'

dut1_to_dut2_ip6_static_adjacency = {'eid': tg_if2_mac,
                                     'seid': tg_if1_mac,
                                     'rloc': dut2_to_dut1_ip6,
                                     'int': 'dut1_to_dut2',
                                     'map_res': tg2_ip6}
dut2_to_dut1_ip6_static_adjacency = {'eid': tg_if1_mac,
                                     'seid': tg_if2_mac,
                                     'rloc': dut1_to_dut2_ip6,
                                     'map_res': tg1_ip6,
                                     'int': 'dut2_to_dut1'}
