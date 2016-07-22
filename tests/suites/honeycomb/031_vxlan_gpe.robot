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

*** Variables ***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}

# Parameters to be set on existing interface
| ${vxlan_gpe_existing_if}= | ${interface}
| &{vxlan_gpe_base_wrong_interface_settings}=
| ... | name=${vxlan_gpe_existing_if}
| ... | type=iana-if-type:ethernetCsmacd
| ... | description=for testing purposes
| ... | enabled=true
| ... | link-up-down-trap-enable=enabled
| &{vxlan_gpe_wrong_interface_settings}=
| ... | local=192.168.50.77
| ... | remote=192.168.50.72
| ... | vni=${9}
| ... | next-protocol=wrong_ipv4
| ... | encap-vrf-id=${0}
| ... | decap-vrf-id=${0}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/vxlan_gpe.robot
# Import additional VxLAN GPE settings from resource file
| Variables | resources/test_data/honeycomb/vxlan_gpe.py
| Documentation | *Honeycomb VxLAN-GPE management test suite.*
| Force Tags | honeycomb_sanity

*** Test Cases ***
| Honeycomb creates VxLAN GPE tunnel
| | [Documentation] | Check if Honeycomb API can configure VxLAN GPE tunnel.
| | ...
| | Given interface configuration from Honeycomb should be empty
| | ... | ${node} | ${vxlan_gpe_if1}
| | And interface configuration from VAT should be empty
| | ... | ${node} | ${vxlan_gpe_if1}
| | When Honeycomb creates VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if1}
| | ... | ${vxlan_gpe_base_settings} | ${vxlan_gpe_settings}
| | Then run keyword and continue on failure
| | ... | VxLAN GPE configuration from Honeycomb should be
| | ... | ${node} | ${vxlan_gpe_if1}
| | ... | ${vxlan_gpe_base_settings} | ${vxlan_gpe_settings}
| | And run keyword and continue on failure
| | ... | VxLAN GPE configuration from VAT should be
| | ... | ${node} | ${vxlan_gpe_if1} | ${vxlan_gpe_settings}
| | And run keyword and continue on failure
| | ... | VxLAN GPE Interface indices from Honeycomb and VAT should correspond
| | ... | ${node} | ${vxlan_gpe_if1}

| Honeycomb removes VxLAN GPE tunnel
| | [Documentation] | Check if Honeycomb API can remove VxLAN GPE tunnel.
| | ...
# Disabled beacuse of bug in Honeycomb.
# TODO: Enable when fixed.
#| | Given VxLAN GPE configuration from Honeycomb should be
#| | ... | ${node} | ${vxlan_gpe_if1}
#| | ... | ${vxlan_gpe_base_settings} | ${vxlan_gpe_settings}
#| | And VxLAN GPE configuration from VAT should be
#| | ... | ${node} | ${vxlan_gpe_if1} | ${vxlan_gpe_settings}
| | When Honeycomb removes VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if1}
| | Then VxLAN GPE configuration from VAT should be empty
| | ... | ${node}
| | And VxLAN GPE configuration from Honeycomb should be
| | ... | ${node} | ${vxlan_gpe_if1}
| | ... | ${vxlan_gpe_disabled_base_settings} | ${vxlan_gpe_settings}

| Honeycomb sets wrong interface type while creating VxLAN GPE tunnel
| | [Documentation] | Check if Honeycomb refuses to create a VxLAN GPE tunnel\
| | ... | with a wrong interface type set.
| | ...
| | Given interface configuration from Honeycomb should be empty
| | ... | ${node} | ${vxlan_gpe_if2}
| | And interface configuration from VAT should be empty
| | ... | ${node} | ${vxlan_gpe_if2}
| | When Honeycomb fails to create VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if2}
| | ... | ${vxlan_gpe_wrong_type_base_settings} | ${vxlan_gpe_settings}
| | Then interface configuration from Honeycomb should be empty
| | ... | ${node} | ${vxlan_gpe_if2}
| | And interface configuration from VAT should be empty
| | ... | ${node} | ${vxlan_gpe_if2}

| Honeycomb sets wrong protocol while creating VxLAN GPE tunnel
| | [Documentation] | Check if Honeycomb refuses to create a VxLAN GPE tunnel\
| | ... | with a wrong next-protocol set.
| | ...
| | Given interface configuration from Honeycomb should be empty
| | ... | ${node} | ${vxlan_gpe_if3}
| | And interface configuration from VAT should be empty
| | ... | ${node} | ${vxlan_gpe_if3}
| | When Honeycomb fails to create VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if3}
| | ... | ${vxlan_gpe_wrong_protocol_base_settings}
| | ... | ${vxlan_gpe_wrong_protocol_settings}
| | Then interface configuration from Honeycomb should be empty
| | ... | ${node} | ${vxlan_gpe_if3}
| | And interface configuration from VAT should be empty
| | ... | ${node} | ${vxlan_gpe_if3}

| Honeycomb sets VxLAN GPE tunnel on existing interface with wrong type
| | [Documentation] | Check if Honeycomb refuses to create a VxLAN GPE tunnel\
| | ... | on existing interface with wrong type.
| | ...
| | Given VxLAN GPE configuration from VAT should be empty
| | ... | ${node}
| | When Honeycomb fails to create VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_existing_if}
| | ... | ${vxlan_gpe_base_wrong_interface_settings}
| | ... | ${vxlan_gpe_wrong_interface_settings}
| | Then VxLAN GPE configuration from VAT should be empty
| | ... | ${node}

| Honeycomb creates VxLAN GPE tunnel with ipv6
| | [Documentation] | Check if Honeycomb API can configure VxLAN GPE tunnel\
| | ... | with IPv6 addresses.
| | ...
| | Given VxLAN GPE configuration from VAT should be empty
| | ... | ${node}
# Disabled beacuse of bug in Honeycomb
# TODO: Enable when fixed.
#| | And VxLAN GPE configuration from Honeycomb should be
#| | ... | ${node} | ${vxlan_gpe_if5}
#| | ... | ${vxlan_gpe_disabled_base_settings} | ${vxlan_gpe_settings}
| | When Honeycomb creates VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if5}
| | ... | ${vxlan_gpe_base_ipv6_settings} | ${vxlan_gpe_ipv6_settings}
| | Then run keyword and continue on failure
| | ... | VxLAN GPE configuration from Honeycomb should be
| | ... | ${node} | ${vxlan_gpe_if5}
| | ... | ${vxlan_gpe_base_ipv6_settings} | ${vxlan_gpe_ipv6_settings}
| | And run keyword and continue on failure
| | ... | VxLAN GPE configuration from VAT should be
| | ... | ${node} | ${vxlan_gpe_if5} | ${vxlan_gpe_ipv6_settings}
| | And run keyword and continue on failure
| | ... | VxLAN GPE Interface indices from Honeycomb and VAT should correspond
| | ... | ${node} | ${vxlan_gpe_if5}

| Honeycomb creates the second VxLAN GPE tunnel with ipv6
| | [Documentation] | Check if Honeycomb API can configure another one VxLAN\
| | ... | GPE tunnel with IPv6 addresses.
| | ...
| | Given interface configuration from Honeycomb should be empty
| | ... | ${node} | ${vxlan_gpe_if6}
| | And interface configuration from VAT should be empty
| | ... | ${node} | ${vxlan_gpe_if6}
| | When Honeycomb creates VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if6}
| | ... | ${vxlan_gpe_base_ipv6_settings2} | ${vxlan_gpe_ipv6_settings2}
| | Then run keyword and continue on failure
| | ... | VxLAN GPE configuration from Honeycomb should be
| | ... | ${node} | ${vxlan_gpe_if6}
| | ... | ${vxlan_gpe_base_ipv6_settings2} | ${vxlan_gpe_ipv6_settings2}
| | And run keyword and continue on failure
| | ... | VxLAN GPE configuration from VAT should be
| | ... | ${node} | ${vxlan_gpe_if6} | ${vxlan_gpe_ipv6_settings2}
| | And run keyword and continue on failure
| | ... | VxLAN GPE Interface indices from Honeycomb and VAT should correspond
| | ... | ${node} | ${vxlan_gpe_if6}
