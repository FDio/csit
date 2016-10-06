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

"""Test variables for ip6-ipsec-lispgpe-ip6 encapsulation test suite."""

# Lisp default global value
locator_name = 'tst_locator'

# Lisp default locator_set value
duts_locator_set = {'locator_name': locator_name,
                    'priority': 1,
                    'weight': 1}

# IPv4 Lisp static mapping configuration
dut1_to_dut2_ip6 = '2001:cdba:3::1'
dut2_to_dut1_ip6 = '2001:cdba:3::2'
dut1_to_tg_ip6 = '2001:cdba:1::1'
dut2_to_tg_ip6 = '2001:cdba:2::1'
tg1_ip6 = '2001:cdba:1::2'
tg2_ip6 = '2001:cdba:2::2'
prefix6 = 64

dut1_to_dut2_ip6_static_adjacency = {'vni': 0,
                                     'deid': '2001:cdba:2::0',
                                     'rloc': dut2_to_dut1_ip6,
                                     'seid': '2001:cdba:1::0',
                                     'prefix': 64}
dut2_to_dut1_ip6_static_adjacency = {'vni': 0,
                                     'deid': '2001:cdba:1::0',
                                     'seid': '2001:cdba:2::0',
                                     'rloc': dut1_to_dut2_ip6,
                                     'prefix': 64}

dut1_ip6_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '2001:cdba:1::0',
                'prefix': 64}
dut2_ip6_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '2001:cdba:2::0',
                'prefix': 64}

dut1_fib_table = '1'
dut2_fib_table = '2'
