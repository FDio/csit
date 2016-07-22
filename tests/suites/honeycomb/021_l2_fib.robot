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

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Resource | resources/libraries/robot/honeycomb/l2_fib.robot
| Variables | resources/test_data/honeycomb/l2_fib.py
| Documentation | *Honeycomb L2 FIB management test suite.*
| Suite Setup | Run keywords
| ... | Set test interface down
| ... | AND
| ... | Honeycomb removes all bridge domains | ${node}
| Suite Teardown | Honeycomb removes all bridge domains | ${node}
| Force tags | honeycomb_sanity

*** Variables ***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Test Cases ***
| Honeycomb adds L2 FIB entry (forward)
| | [Documentation] | Honeycomb creates a bridge domain and assignes an \
| | ... | interface to it. Then adds an L2 FIB entry (forward) to the bridge \
| | ... | domain.
| | ...
| | [Teardown] | Honeycomb removes L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper['phys-address']}
| | ...
| | Given Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | When Honeycomb sets interface state
| | ... | ${node} | ${interface} | up
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | When Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Then Bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Given Bridge domain configuration in interface operational data should be empty
| | ... | ${node} | ${interface}
| | When Honeycomb adds interface to bridge domain
| | ... | ${node} | ${interface} | ${bd_name} | ${if_bd_settings}
| | Then Bridge domain configuration in interface operational data should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | Given L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg}
| | Then L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_forward_vat}

| Honeycomb adds L2 FIB entry (static, forward)
| | [Documentation] | Honeycomb adds an L2 FIB entry (static, forward) to the \
| | ... | bridge domain.
| | ...
| | [Teardown] | Honeycomb removes L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_static_forward_oper['phys-address']}
| | ...
| | Given Bridge domain configuration in interface operational data should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | And L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_static_forward_cfg}
| | Then L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_static_forward_oper}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_static_forward_vat}

| Honeycomb adds L2 FIB entry (static, filter)
| | [Documentation] | Honeycomb adds an L2 FIB entry (static, filter) to the \
| | ... | bridge domain.
| | ...
| | [Teardown] | Honeycomb removes L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_filter_oper['phys-address']}
| | ...
| | Given Bridge domain configuration in interface operational data should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | And L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_filter_cfg}
| | Then L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_filter_oper}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_filter_vat}

| Honeycomb adds and removes L2 FIB entry (forward)
| | [Documentation] | Honeycomb adds an L2 FIB entry (forward) to the bridge \
| | ... | domain and then Honeycomb removes it from the bridge domain.
| | ...
| | [Teardown] | Honeycomb removes L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper['phys-address']}
| | ...
| | Given Bridge domain configuration in interface operational data should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | And L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg}
| | Then L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_forward_vat}
| | When Honeycomb removes L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper['phys-address']}
| | Then L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}

| Honeycomb adds more than one L2 FIB entry
| | [Documentation] | Honeycomb adds three L2 FIB entries to the bridge domain.
| | ...
| | [Teardown] | Honeycomb removes all L2 FIB entries
| | ... | ${node} | ${bd_name}
| | ...
| | Given Bridge domain configuration in interface operational data should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | And L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg}
| | And Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_static_forward_cfg}
| | And Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_filter_cfg}
| | Then L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper}
| | And L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_static_forward_oper}
| | And L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_filter_oper}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_forward_vat}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_static_forward_vat}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_filter_vat}

| Honeycomb fails to set wrong L2 FIB entry
| | [Documentation] | Honeycomb tries to add an L2 FIB entry with wrong \
| | ... | parameters to the bridge domain. It must fail.
| | ...
| | [Teardown] | Honeycomb removes all L2 FIB entries
| | ... | ${node} | ${bd_name}
| | ...
| | Given Bridge domain configuration in interface operational data should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | And L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb fails to add wrong L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg_wrong_mac}
| | Then L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb fails to add wrong L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg_wrong_if}
| | Then L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb fails to add wrong L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg_wrong_action}
| | Then L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}

| Honeycomb fails to modify existing L2 FIB entry
| | [Documentation] | Honeycomb tries to modify an existing L2 FIB entry. It \
| | ... | must fail.
| | ...
| | [Teardown] | Honeycomb removes all L2 FIB entries
| | ... | ${node} | ${bd_name}
| | ...
| | Given Bridge domain configuration in interface operational data should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | And L2 FIB Table from Honeycomb should be empty
| | ... | ${node} | ${bd_name}
| | And L2 FIB Table from VAT should be empty
| | ... | ${node} | ${bd_index}
| | When Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg}
| | Then L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper}
| | When Honeycomb fails to modify L2 FIB entry
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper['phys-address']}
| | ... | outgoing-interface
| | ... | ${l2_fib_forward_modified_cfg['outgoing-interface']}
| | Then L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper}
| | And L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_forward_vat}

*** Keywords ***
| Set test interface down
| | [Documentation] | Set the interface used in tests down.
| | ...
| | Honeycomb sets interface state
| | ... | ${node} | ${interface} | down
