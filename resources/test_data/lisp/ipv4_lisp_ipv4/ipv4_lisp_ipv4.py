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

"""Test variables for ip4-lispgpe-ip4 encapsulation test suite."""

# Lisp default global value
locator_name = 'tst_locator'

# Test configuration data
tg_if1_ip4= '6.0.0.2'
tg_if2_ip4= '6.0.1.2'
dut_if1_ip4= '6.0.0.1'
dut_if2_ip4= '6.0.1.1'
ip4_plen= 24
src_ip4= '6.0.0.2'
dst_ip4= '6.0.2.2'
src_rloc4= dut_if2_ip4
dst_rloc4= tg_if2_ip4
#src_rloc6= dut_if2_ip6
#dst_rloc6= tg_if2_ip6

#IP6 over IP4 LISP configuration data
tg_if1_ip6= '6::2'
dut_if1_ip6= '6:0:0::1'
src_ip6= '6::2'
dst_ip6= '6:0:2::2'
ip6_plen=64

# Lisp default locator_set value
duts_locator_set = {'locator_name': locator_name,
                    'priority': 1,
                    'weight': 1}

# IPv4 Lisp static mapping configuration

dut1_to_tg_ip4_static_adjacency = {'vni': 0,
                                   'deid': '6.0.2.0',
                                   'seid': '6.0.0.0',
                                   'rloc': '6.0.1.2',
                                   'prefix': 24}

dut1_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '6.0.0.0',
                'prefix': 24}

#IPv6 over IPv4 LISP mapping
dut1_ip6o4_static_adjacency = {'vni': 0,
                               'deid': '6:0:2::0',
                               'seid': '6:0:0::0',
                               'rloc': '6.0.1.2',
                               'prefix': 64}
dut1_ip6o4_eid = {'locator_name': locator_name,
                  'vni': 0,
                  'eid': '6:0:0::0',
                  'prefix': 64}

#IPv4 over IPv6 LISP mapping
dut1_ip4o6_static_adjacency = {'vni': 0,
                               'deid': '6.0.2.0',
                               'seid': '6.0.0.0',
                               'rloc': '6:0:1::2',
                               'prefix': 24}
dut1_ip4o6_eid = {'locator_name': locator_name,
                  'vni': 0,
                  'eid': '6.0.0.0',
                  'prefix': 24}
