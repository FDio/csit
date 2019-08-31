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

# Lisp default locator_set value
duts_locator_set = {'locator_name': locator_name,
                    'priority': 1,
                    'weight': 1}

# IPv4 Lisp static mapping configuration
tg1_ip4 = '6.0.0.2'
tg2_ip4 = '6.0.1.2'
dut_to_tg_if1_ip4 = '6.0.0.1'
dut_to_tg_if2_ip4 = '6.0.1.1'

src_ip_range = '6.0.0.0'
dst_ip_range = '6.0.2.0'

src_ip4 = '6.0.0.2'
dst_ip4 = '6.0.2.2'

prefix4 = 24

dut1_to_tg_ip4_static_adjacency = {'vni': 0,
                                   'deid': dst_ip_range,
                                   'seid': src_ip_range,
                                   'rloc': tg2_ip4,
                                   'prefix': prefix4}

dut1_ip4_eid = {'locator_name': locator_name,
                'vni': 0,
                'eid': src_ip_range,
                'prefix': prefix4}

fib_table_1 = 1

sock1 = "/tmp/sock1"

bid = 10
