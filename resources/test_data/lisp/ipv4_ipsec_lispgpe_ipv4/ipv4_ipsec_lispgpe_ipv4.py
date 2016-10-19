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
duts_locator_set = {'locator_name': locator_name,
                    'priority': 1,
                    'weight': 1}

# IPv4 Lisp static mapping configuration
dut1_to_dut2_ip4 = '6.6.3.1'
dut2_to_dut1_ip4 = '6.6.3.2'
dut1_to_tg_ip4 = '6.6.1.1'
dut2_to_tg_ip4 = '6.6.2.1'
tg1_ip4 = '6.6.1.2'
tg2_ip4 = '6.6.2.2'
prefix4 = 24

dut1_to_dut2_ip4_static_adjacency = {'vni': 0,
                                     'deid': '6.6.2.0',
                                     'rloc': '6.6.3.2',
                                     'seid': '6.6.1.0',
                                     'prefix': 24}
dut2_to_dut1_ip4_static_adjacency = {'vni': 0,
                                     'deid': '6.6.1.0',
                                     'seid': '6.6.2.0',
                                     'rloc': '6.6.3.1',
                                     'prefix': 24}

dut1_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '6.6.1.0',
                'prefix': 24}
dut2_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '6.6.2.0',
                'prefix': 24}

fib_table_1 = 1
dut1_dut2_vni = 1

dut2_spi = 1000
dut1_spi = 1001
ESP_PROTO = 50
