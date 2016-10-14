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

"""Test variables for RTR (re-encapsulating router) IPv4 test suite."""

# Lisp default locator_set value
duts_locator_set = {'priority': 1,
                    'weight': 1}

# Lisp default global value
locator1 = 'locator_1'
locator2 = 'locator_2'
vni_dut1_1 = 0
vni_dut1_2 = 1
vni_dut2 = 1
tg1_ip4 = '10.0.1.1'
tg2_ip4 = '10.0.2.1'
dut1_to_tg_if1_ip = '10.0.1.2'
dut1_to_tg_if2_ip = '10.0.2.2'
dut2_to_dut1_if1_ip4 = '10.0.3.2'
dut2_to_dut1_if2_ip4 = '10.0.3.3'
dut1_to_dut2_if2_ip4 = '10.0.3.4'
dut1_to_dut2_if1_ip4 = '10.0.3.1'
dst_ip_range = '10.0.2.0'
src_ip_range = '10.0.1.0'

prefix4 = 24

fib_table_2 = 2

