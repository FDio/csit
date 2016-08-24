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
dut1_to_dut2_ip4 = '6.0.3.1'
dut2_to_dut1_ip4 = '6.0.3.2'
dut1_to_tg_ip4 = '6.0.1.1'
dut2_to_tg_ip4 = '6.0.2.1'
tg1_ip4 = '6.0.1.2'
tg2_ip4 = '6.0.2.2'
prefix4 = 24

dut1_to_dut2_ip4_static_adjacency = {'vni': 0,
                                     'deid': '6.0.2.0',
                                     'seid': '6.0.1.0',
                                     'rloc': '6.0.3.2',
                                     'prefix': 24}
dut2_to_dut1_ip4_static_adjacency = {'vni': 0,
                                     'deid': '6.0.1.0',
                                     'seid': '6.0.2.0',
                                     'rloc': '6.0.3.1',
                                     'prefix': 24}

dut1_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '6.0.1.0',
                'prefix': 24}
dut2_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': '6.0.2.0',
                'prefix': 24}

dut1_fib_table = '1'
dut2_fib_table = '2'
dut1_fib_table2 = '12'
dut2_fib_table2 = '22'

sock_11 = '/tmp/sock11'
sock_12 = '/tmp/sock12'
sock_21 = '/tmp/sock21'
sock_22 = '/tmp/sock22'

dut1_vm = 'dut1_vm'
dut2_vm = 'dut2_vm'

vm1_ip_1 = '6.0.8.2'
vm1_ip_2 = '6.0.8.3'
vm2_ip_1 = '6.0.9.2'
vm2_ip_2 = '6.0.9.3'

vm1_mac_id = '10'
vm2_mac_id = '20'

vm1_vif1_mac = '52:54:00:00:10:01'
vm1_vif2_mac = '52:54:00:00:10:02'
vm2_vif1_mac = '52:54:00:00:20:01'
vm2_vif2_mac = '52:54:00:00:20:02'

dut1_vhost_ip_1 = '6.0.8.1'
dut1_vhost_ip_2 = '6.0.8.4'
dut2_vhost_ip_1 = '6.0.9.1'
dut2_vhost_ip_2 = '6.0.9.4'

vni_blue = '23'
vni_red = '24'

bid_b = '23'
bid_r = '24'
