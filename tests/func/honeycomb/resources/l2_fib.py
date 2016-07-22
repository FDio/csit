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

"""Test variables for Honeycomb L2 FIB test suite."""

# Bridge domain name.
bd_name = 'test-l2-bd'
bd_index = 1

# Bridge domain settings used while creating a test bridge domain.
bd_settings = {
    'flood': True,
    'forward': True,
    'learn': True,
    'unknown-unicast-flood': True,
    'arp-termination': True
}

# Bridge domain configuration used while adding the bridge domain to an
# interface.
if_bd_settings = {
    'bridge-domain': bd_name,
    'split-horizon-group': 1,
    'bridged-virtual-interface': False
}

# Add L2 FIB entry (forward).
# Configuration data:
l2_fib_forward_cfg = {
    "phys-address": "aa:bb:cc:dd:ee:ff",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "action": "l2-fib-forward"
}

# Expected operational data:
l2_fib_forward_oper = {
    "phys-address": "aa:bb:cc:dd:ee:ff",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "bridged-virtual-interface": False,
    "action": "v3po:l2-fib-forward",
    "static-config": False
}

# Expected VAT data:
l2_fib_forward_vat = {
    "mac": int("".join(l2_fib_forward_oper["phys-address"].split(':')), 16),
    "static_mac": 0,
    "filter_mac": 0,
    "bvi_mac": 0
  }

# Add L2 FIB entry (static, forward).
# Configuration data:
l2_fib_static_forward_cfg = {
    "phys-address": "22:22:33:44:55:66",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "static-config": True,
    "action": "l2-fib-forward"
}

# Expected operational data:
l2_fib_static_forward_oper = {
    "phys-address": "22:22:33:44:55:66",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "bridged-virtual-interface": False,
    "action": "v3po:l2-fib-forward",
    "static-config": True
}

# Expected VAT data:
l2_fib_static_forward_vat = {
    "mac": int("".join(l2_fib_static_forward_oper["phys-address"].
                       split(':')), 16),
    "sw_if_index": 5,
    "static_mac": 1,
    "filter_mac": 0,
    "bvi_mac": 0
}

# Add L2 FIB entry (filter).
# Configuration data:
l2_fib_filter_cfg = {
    "phys-address": "00:01:02:03:04:05",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "static-config": True,
    "action": "l2-fib-filter"
}

# Expected operational data:
l2_fib_filter_oper = {
    "phys-address": "00:01:02:03:04:05",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "bridged-virtual-interface": False,
    "action": "v3po:l2-fib-filter",
    "static-config": True
}

# Expected VAT data:
l2_fib_filter_vat = {
    "mac": int("".join(l2_fib_filter_oper["phys-address"].split(':')), 16),
    "sw_if_index": 5,
    "static_mac": 1,
    "filter_mac": 1,
    "bvi_mac": 0
}

# WRONG configuration data - Add L2 FIB entry.
l2_fib_forward_cfg_wrong_mac = {
    "phys-address": "WRONG-MAC",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "action": "l2-fib-forward"
}

l2_fib_forward_cfg_wrong_if = {
    "phys-address": "aa:bb:cc:dd:ee:ff",
    "outgoing-interface": "WRONG-INTERFACE",
    "action": "l2-fib-forward"
}

l2_fib_forward_cfg_wrong_action = {
    "phys-address": "aa:bb:cc:dd:ee:ff",
    "outgoing-interface": "GigabitEthernet0/8/0",
    "action": "WRONG-ACTION"
}

# Modify L2 FIB entry (forward).
# Configuration data:
l2_fib_forward_modified_cfg = {
    "phys-address": "aa:bb:cc:dd:ee:ff",
    "outgoing-interface": "GigabitEthernet0/9/0",
    "action": "l2-fib-forward"
}
