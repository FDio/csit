# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Test variables for ip4-lispgpe-ip6 encapsulation test suite."""

# IP settings
dut1_to_dut2_ip6 = '2001:cdba:3::1'
dut2_to_dut1_ip6 = '2001:cdba:3::2'
dut1_to_tg_ip4 = '6.0.1.1'
dut2_to_tg_ip4 = '6.0.2.1'
tg1_ip4 = '6.0.1.2'
tg2_ip4 = '6.0.2.2'
dut1_vhost1_ip4 = '6.6.6.1'
dut1_vhost2_ip4 = '6.6.6.2'
prefix4 = 24
prefix6 = 64
fib_table_1 = 1
fib_table_2 = 0

# vhost sockets
sock1 = '/tmp/sock1'
sock2 = '/tmp/sock2'

# Lisp default global value
locator_name = 'tst_locator'

# Lisp default locator_set value
duts_locator_set = {'locator_name': locator_name,
                    'priority': 1,
                    'weight': 1}

# IPv4 Lisp static mapping configuration
vni_table = 0
dut1_to_dut2_ip46_static_adjacency = {'vni': 0,
                                      'deid': '6.0.2.0',
                                      'seid': '6.0.1.0',
                                      'rloc': dut2_to_dut1_ip6,
                                      'prefix': prefix4}
dut2_to_dut1_ip46_static_adjacency = {'vni': 0,
                                      'deid': '6.0.1.0',
                                      'seid': '6.0.2.0',
                                      'rloc': dut1_to_dut2_ip6,
                                      'prefix': prefix4}

dut1_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '6.0.1.0',
                'prefix': prefix4}
dut2_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '6.0.2.0',
                'prefix': prefix4}

lisp_gpe_int = 'lisp_gpe0'

# IPSEC settings
dut2_spi = 1000
dut1_spi = 1001
ESP_PROTO = 50
