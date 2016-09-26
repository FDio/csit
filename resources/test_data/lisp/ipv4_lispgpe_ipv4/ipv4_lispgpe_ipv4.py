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
tg1_ip4 = '6.0.1.1'
dut1_to_tg_ip4 = '6.0.1.2'

dut1_vif1_ip4 = '6.0.2.1'
vm1_vif1_ip4 = '6.0.2.2'

vm1_vif2_ip4 = '6.0.3.1'
dut1_vif2_ip4 = '6.0.3.2'

dut1_to_dut2_ip4 = '6.0.4.1'
dut2_to_dut1_ip4 = '6.0.4.2'

dut2_to_tg_ip4 = '6.0.5.1'
tg2_ip4 = '6.0.5.2'

src_ip_range = '6.0.1.0'
dst_ip_range = '6.0.5.0'

vm1_vif1_mac = '52:54:00:00:04:01'
vm1_vif2_mac = '52:54:00:00:04:02'
prefix4 = 24

dut1_to_dut2_ip4_static_adjacency = {'vni': 0,
                                     'deid': dst_ip_range,
                                     'seid': src_ip_range,
                                     'rloc': dut2_to_dut1_ip4,
                                     'prefix': prefix4}
dut2_to_dut1_ip4_static_adjacency = {'vni': 0,
                                     'deid': src_ip_range,
                                     'seid': dst_ip_range,
                                     'rloc': dut1_to_dut2_ip4,
                                     'prefix': prefix4}

dut1_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': src_ip_range,
                'prefix': prefix4}
dut2_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': dst_ip_range,
                'prefix': prefix4}

dut1_fib_table = 1
dut2_fib_table = 2

sock1 = "/tmp/sock1"
sock2 = "/tmp/sock2"

bid = 10
